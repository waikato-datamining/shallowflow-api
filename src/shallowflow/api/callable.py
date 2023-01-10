from .actor import Actor
from .actor_utils import find_actor_handlers
from .config import Option
from .control import MutableActorHandler, ActorHandler
from .serialization.vars import AbstractStringReader, add_string_reader

UNKNOWN = "unknown"

STATE_CALLABLEACTOR = "callable actor"

STATE_CONFIGURED = "configured"


def find_callable_actor(actor, name):
    """
    Tries to find the referenced callable actor.

    :param actor: the actor to search
    :type actor: Actor
    :param name: the callable name to look for
    :type name: str
    :return: the located actor if found, otherwise None
    :rtype: Actor
    """
    result = None

    if isinstance(actor, ActorReferenceHandler):
        index = actor.index(name)
        if index > -1:
            result = actor.actors[index]
    elif isinstance(actor, ActorHandler):
        for i in range(len(actor)):
            for sub_actor in actor.actors:
                if isinstance(sub_actor, ActorReferenceHandler):
                    result = find_callable_actor(sub_actor, name)
                    if result is not None:
                        break
                # TODO external flows

    return result


def find_callable_actor_recursive(actor, name):
    """
    Tries to find the referenced callable actor. First all possible actor
    handlers are located recursively (up to the root) that allow also
    standalones. This list of actors is then searched for the callable actor.

    :param actor: the actor to start from
    :type actor: Actor
    :param name: the callable actor to look for
    :type name: str
    :return: the located actor if found, otherwise None
    :rtype: Actor
    """
    result = None
    handlers = find_actor_handlers(actor, must_allow_standalones=True)
    for handler in handlers:
        result = find_callable_actor(handler, name)
        if result is not None:
            break

    return result



class CallableActorReference(str):
    """
    For referencing actors by name.
    """
    pass


class ActorReferenceHandler(MutableActorHandler):
    """
    Ancestor for actors that manage actors that can be referenced.
    """
    pass


class CallableActorReferenceStringReader(AbstractStringReader):
    """
    Ancestor for classes that turn strings into CallableActorReference objects.
    """

    def handles(self, cls):
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, CallableActorReference)

    def convert(self, s, base_type=None):
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        return CallableActorReference(s)


class AbstractCallableActor(Actor):
    """
    Ancestor for callable actors.
    """

    def _initialize(self):
        """
        Performs initializations.
        """
        super()._initialize()
        self._find_callable_actor_error = None
        self._configured = False
        self._callable_actor = None

    def _define_options(self):
        """
        For configuring the options.
        """
        super()._define_options()
        self._option_manager.add(Option("callable_name", CallableActorReference, CallableActorReference(UNKNOWN), "The name of the callable actor to use."))
        self._option_manager.add(Option("optional", bool, False, "Whether the callable actor is optional; will not raise an error if not present."))

    def reset(self):
        """
        Resets the state of the object.
        """
        super().reset()
        self._find_callable_actor_error = None
        self._configured = False
        self._callable_actor = None

    def _backup_state(self):
        """
        For backing up the internal state before reconfiguring due to variable changes.

        :return: the state dictionary
        :rtype: dict
        """
        result = super()._backup_state()
        if self._callable_actor is not None:
            result[STATE_CALLABLEACTOR] = self._callable_actor
        result[STATE_CONFIGURED] = self._configured
        return result

    def _restore_state(self, state):
        """
        Restores the state from the state dictionary after being reconfigured due to variable changes.

        :param state: the state dictionary to use
        :type state: dict
        """
        if STATE_CALLABLEACTOR in state:
            self._callable_actor = state[STATE_CALLABLEACTOR]
            del state[STATE_CALLABLEACTOR]

        self._configured = state[STATE_CONFIGURED]
        del state[STATE_CONFIGURED]

        super()._restore_state(state)

    def _find_callable_actor(self):
        """
        Tries to find the specified callable actor,

        :return: the callable actor, None if not found
        :rtype: Actor
        """
        self._find_callable_actor_error = None
        return find_callable_actor_recursive(self, self.get("callable_name"))

    def _setup_callable_actor(self):
        """
        Configures the callable actor.

        :return: None if successfully set up, otherwise error message
        :rtype: str
        """
        result = None
        self._configured = True
        self._callable_actor = self._find_callable_actor()

        if self._callable_actor is None:
            if self._find_callable_actor_error is not None:
                msg = " " + self._find_callable_actor_error
            else:
                msg = ""
            if not self.get("optional"):
                result = "Could not find/initialize callable actor '%s'!%s" % (self.get("callable_name"), msg)
            else:
                self.log("Callable actor '%s' not found/failed to initialize, ignoring.%s" % (self.get("callable_name"), msg))
        else:
            variables = self._callable_actor.option_manager.detect_vars(skip=[Actor])
            self._variables_detected.extend(variables)
            if len(self._variables_detected) > 0:
                self.variables.add_listener(self)

        return result

    def setup(self):
        """
        Prepares the actor for use.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = super().setup()

        if result is None:
            if not self.option_manager.has_var("callable_name"):
                result = self._setup_callable_actor()

        return result

    def _do_execute_callable_actor(self):
        """
        Executes the callable actor.

        :return: None if successfully executed, otherwise error message
        :rtype: str
        """
        raise NotImplemented()

    def _do_execute(self):
        """
        Performs the actual execution.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = None

        if not self._configured:
            result = self._setup_callable_actor()

        if result is None:
            if self._callable_actor is not None:
                if not self._callable_actor.is_stopped:
                    result = self._do_execute_callable_actor()

        return result

    def stop_execution(self):
        """
        Stops the actor execution.
        """
        if self._callable_actor is not None:
            self._callable_actor.stop_execution()
        super().stop_execution()

    def wrap_up(self):
        """
        For finishing up the execution.
        Does not affect graphical output.
        """
        if self._callable_actor is not None:
            self._callable_actor.wrap_up()
        super().wrap_up()

    def clean_up(self):
        """
        Also cleans up graphical output.
        """
        if self._callable_actor is not None:
            self._callable_actor.clean_up()
        super().clean_up()


# serialization
add_string_reader(CallableActorReferenceStringReader)
