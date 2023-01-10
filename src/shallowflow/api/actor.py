import traceback
import shallowflow.api.serialization.objects as serialization
from .config import Option, AbstractOptionHandler, dict_to_optionhandler, optionhandler_to_dict
from .stopping import Stoppable
from .vars import VariableChangeListener
from .scope import ScopeHandler
from .storage import StorageHandler

FLOW_PATH = "flow_path"
""" Variable that stores the full flow path. """

FLOW_DIR = "flow_dir"
""" Variable that stores the directory the flow resides in. """


class Actor(AbstractOptionHandler, VariableChangeListener, Stoppable):
    """
    The ancestor for all actors.
    """

    def _initialize(self):
        """
        Performs initializations.
        """
        super()._initialize()
        self._parent = None
        self._stopped = False

    def _define_options(self):
        """
        For configuring the options.
        """
        super()._define_options()
        self._option_manager.add(Option("skip", bool, False, "Whether to skip this actor during execution"))
        self._option_manager.add(Option("annotation", str, "", "For adding documentation to the actor"))
        self._option_manager.add(Option("name", str, "", "The name to use for this actor, leave empty for class name"))
        self._option_manager.add(Option("stop_flow_on_error", bool, True, "Whether to stop the flow in case of an error"))

    def reset(self):
        """
        Resets the state of the object.
        """
        super().reset()
        self._log_prefix = None
        self._variables_changed = False
        self._variables_detected = []

    @property
    def parent(self):
        """
        Returns the current parent actor.

        :return: the parent actor
        :rtype: Actor
        """
        return self._parent

    @parent.setter
    def parent(self, a):
        """
        Sets the actor to use as parent.

        :param a: the parent actor
        :type a: Actor
        """
        self._parent = a
        self.reset()

    @property
    def root(self):
        """
        Returns the root actor.

        :return: the root actor, None if not available
        :rtype: Actor
        """
        if self._parent is not None:
            return self._parent.root
        else:
            return self

    @property
    def scope_handler(self):
        """
        Returns the scope handler, if any.

        :return: the scope handler, None if not available
        :rtype: ScopeHandler
        """
        if isinstance(self, ScopeHandler):
            return self
        elif self._parent is not None:
            return self._parent.scope_handler
        else:
            return None

    @property
    def is_skipped(self):
        """
        Returns whether the actor is disabled and needs to be skipped during execution.

        :return: true if to skip
        :rtype: bool
        """
        return self.get("skip")

    @property
    def name(self):
        """
        Returns the stored name or the class name.

        :return: the name
        :rtype: str
        """
        if len(self.get("name")) == 0:
            return type(self).__name__
        else:
            return self.get("name")

    @property
    def full_name(self):
        """
        Returns the full path of the actor.

        :return: the path
        :rtype: str
        """
        return self._get_log_prefix()

    def _get_log_prefix(self):
        """
        Returns the log prefix for this actor.

        :return: the prefix
        :rtype: str
        """
        if self._log_prefix is None:
            if self.parent is not None:
                prefix = self.parent.log_prefix + "."
            else:
                prefix = ""
            prefix += self.name
            self._log_prefix = prefix
        return self._log_prefix

    def update_variables(self, variables):
        """
        Sets the variables to use.

        :param variables: the variables to use
        :type variables: Variables
        """
        self.variables.remove_listener(self)
        result = super().update_variables(variables)
        self.variables.add_listener(self)
        return result

    def variables_changed(self, event):
        """
        Gets called when the variable changes.

        :param event: the event
        :type event: VariableChangeEvent
        """
        if event.var in self._variables_detected:
            self._variables_changed = True
            if self.is_debug:
                self.log("Variable changed: %s -> %s" % (event.var, self.variables.get(event.var)))

    @property
    def storage_handler(self):
        """
        Returns the available storage handler, if any.

        :return: the storage handler
        :rtype: StorageHandler
        """
        if isinstance(self, StorageHandler):
            return self
        else:
            if self.parent is None:
                return None
            else:
                return self.parent.storage_handler

    def setup(self):
        """
        Prepares the actor for use.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        self._stopped = False
        self._log_prefix = None
        self._variables_detected = self.option_manager.detect_vars(skip=[Actor])
        if self.is_debug:
            self.log("Detected variables: %s" % str(self._variables_detected))
        self.variables.add_listener(self)
        return None

    def _backup_state(self):
        """
        For backing up the internal state before reconfiguring due to variable changes.

        :return: the state dictionary
        :rtype: dict
        """
        return dict()

    def _restore_state(self, state):
        """
        Restores the state from the state dictionary after being reconfigured due to variable changes.

        :param state: the state dictionary to use
        :type state: dict
        """
        pass

    def _pre_execute(self):
        """
        Before the actual code gets executed.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        if self._variables_changed:
            if self.is_debug:
                self.log("Variables changed, resetting!")
            state = self._backup_state()
            self.reset()
            self.setup()
            self._restore_state(state)
        return None

    def _do_execute(self):
        """
        Performs the actual execution.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        raise NotImplemented()

    def _post_execute(self):
        """
        After the actual code got executed.
        """
        pass

    def execute(self):
        """
        Executes the actor.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        try:
            result = self._pre_execute()
            if result is None:
                result = self._do_execute()
                self._post_execute()
        except Exception:
            result = traceback.format_exc()
        return result

    def wrap_up(self):
        """
        For finishing up the execution.
        Does not affect graphical output.
        """
        self.variables.remove_listener(self)

    def clean_up(self):
        """
        Also cleans up graphical output.
        """
        pass

    def stop_execution(self):
        """
        Stops the actor execution.
        """
        self._stopped = True
        if self.is_debug:
            self.log("Stopped!")

    @property
    def is_stopped(self):
        """
        Returns whether the actor was stopped.

        :return: true if stopped
        :rtype: bool
        """
        return self._stopped


class InputConsumer(Actor):
    """
    Interface for actors that consume input.
    """

    def accepts(self):
        """
        Returns the types that are accepted.

        :return: the list of types
        :rtype: list
        """
        raise NotImplemented()

    def input(self, data):
        """
        Sets the input data to consume.

        :param data: the data to consume
        :type data: object
        """
        raise NotImplemented()


class OutputProducer(Actor):
    """
    Interface for actors that generate output.
    """

    def generates(self):
        """
        Returns the types that get generated.

        :return: the list of types
        :rtype: list
        """
        raise NotImplemented()

    def output(self):
        """
        Returns the next output data.

        :return: the data, None if nothing available
        :rtype: object
        """
        raise NotImplemented()

    def has_output(self):
        """
        Returns whether output data is available.

        :return: true if available
        :rtype: bool
        """
        raise NotImplemented()


class FlowContextHandler(object):

    @property
    def flow_context(self):
        """
        Returns the flow context.

        :return: the flow context, None if none set
        :rtype: Actor
        """
        raise NotImplemented()

    @flow_context.setter
    def flow_context(self, actor):
        """
        Sets the flow context.

        :param actor: the flow context
        :type actor: Actor
        """
        raise NotImplemented()


def is_standalone(actor):
    """
    Checks whether the actor is a standalone.

    :param actor: the actor to check
    :type actor: Actor
    :return: true if a standalone actor
    """
    return not isinstance(actor, OutputProducer) and not isinstance(actor, InputConsumer)


def is_source(actor):
    """
    Checks whether the actor is a source.

    :param actor: the actor to check
    :type actor: Actor
    :return: true if a source actor
    """
    return isinstance(actor, OutputProducer) and not isinstance(actor, InputConsumer)


def is_transformer(actor):
    """
    Checks whether the actor is a transformer.

    :param actor: the actor to check
    :type actor: Actor
    :return: true if a transformer actor
    """
    return isinstance(actor, OutputProducer) and isinstance(actor, InputConsumer)


def is_sink(actor):
    """
    Checks whether the actor is a sink.

    :param actor: the actor to check
    :type actor: Actor
    :return: true if a sink actor
    """
    return not isinstance(actor, OutputProducer) and isinstance(actor, InputConsumer)


# register reader/writer
serialization.add_dict_writer(Actor, optionhandler_to_dict)
serialization.add_dict_reader(Actor, dict_to_optionhandler)
