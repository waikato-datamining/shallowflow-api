from .config import AbstractOptionHandler, optionhandler_to_dict, dict_to_optionhandler
from .actor import FlowContextHandler
from .serialization.objects import add_dict_writer, add_dict_reader


class AbstractBooleanCondition(AbstractOptionHandler, FlowContextHandler):
    """
    Ancestor for boolean conditions.
    """

    def _initialize(self):
        """
        Performs initializations.
        """
        super()._initialize()
        self._flow_context = None

    @property
    def flow_context(self):
        """
        Returns the owning actor.

        :return: the owning actor
        :rtype: Actor
        """
        return self._flow_context

    @flow_context.setter
    def flow_context(self, a):
        """
        Sets the actor to use as owner.

        :param a: the owning actor
        :type a: Actor
        """
        self._flow_context = a
        self._log_prefix = None
        self.reset()

    def _get_log_prefix(self):
        """
        Returns the log prefix for this actor.

        :return: the prefix
        :rtype: str
        """
        if self._log_prefix is None:
            if self.flow_context is not None:
                prefix = self.flow_context.log_prefix + "."
            else:
                prefix = ""
            prefix += type(self).__name__
            self._log_prefix = prefix
        return self._log_prefix

    def _check(self, o):
        """
        Performs checks before performing the evaluation.

        :param o: the current object from the owning actor
        :return: None if successfully passed checks, otherwise error message
        :rtype: str
        """
        if self._flow_context is None:
            return "No owning actor set!"
        return None

    def _do_evaluate(self, o):
        """
        Evaluates the condition.

        :param o: the current object from the owning actor
        :return: the result of the evaluation
        :rtype: bool
        """
        raise NotImplemented()

    def evaluate(self, o):
        """
        Evaluates the condition.

        :param o: the current object from the owning actor
        :return: the result of the evaluation
        :rtype: bool
        """
        msg = self._check(o)
        if msg is not None:
            raise Exception(msg)

        return self._do_evaluate(o)


# register reader/writer
add_dict_writer(AbstractBooleanCondition, optionhandler_to_dict)
add_dict_reader(AbstractBooleanCondition, dict_to_optionhandler)
