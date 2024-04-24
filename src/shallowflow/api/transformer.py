from .actor import InputConsumer, OutputProducer
from coed.config import Option

STATE_INPUT = "input"


class AbstractSimpleTransformer(InputConsumer, OutputProducer):
    """
    Ancestor for simple source actors.
    """

    def reset(self):
        """
        Resets the state of the actor.
        """
        super().reset()
        self._output = list()
        self._input = None

    def input(self, data):
        """
        Sets the input data to consume.

        :param data: the data to consume
        :type data: object
        """
        self._input = data

    def _backup_state(self):
        """
        For backing up the internal state before reconfiguring due to variable changes.

        :return: the state dictionary
        :rtype: dict
        """
        result = super()._backup_state()
        if self._input is not None:
            result[STATE_INPUT] = self._input
        return result

    def _restore_state(self, state):
        """
        Restores the state from the state dictionary after being reconfigured due to variable changes.

        :param state: the state dictionary to use
        :type state: dict
        """
        if STATE_INPUT in state:
            self._input = state[STATE_INPUT]
            del state[STATE_INPUT]
        super()._restore_state(state)

    def _pre_execute(self):
        """
        Before the actual code gets executed.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = super()._pre_execute()
        if result is None:
            self._output.clear()
        return result

    def _post_execute(self):
        """
        After the actual code got executed.
        """
        self._input = None
        if self.is_stopped:
            self._output = list()
        super()._post_execute()

    def has_output(self):
        """
        Returns whether output data is available.

        :return: true if available
        :rtype: bool
        """
        return len(self._output) > 0

    def output(self):
        """
        Returns the next output data.

        :return: the data, None if nothing available
        :rtype: object
        """
        result = None
        if len(self._output) > 0:
            result = self._output[0]
            del self._output[0]
        return result

    def wrap_up(self):
        """
        For finishing up the execution.
        Does not affect graphical output.
        """
        self._input = None
        self._output = None
        super().wrap_up()


class AbstractListOutputTransformer(AbstractSimpleTransformer):
    """
    Ancestor for transformer actors that can output data either as list or one by one.
    """

    def _define_options(self):
        """
        For configuring the options.
        """
        super()._define_options()
        self._option_manager.add(Option(name="output_as_list", value_type=bool, def_value=False,
                                        help="If enabled, the items get output as list rather than one-by-one"))

    def _get_item_type(self):
        """
        Returns the type of the individual items that get generated, when not outputting a list.

        :return: the type that gets generated
        """
        raise NotImplementedError()

    def generates(self):
        """
        Returns the types that get generated.

        :return: the list of types
        :rtype: list
        """
        if self.get("output_as_list"):
            return [list]
        else:
            return [self._get_item_type()]

    def output(self):
        """
        Returns the next output data.

        :return: the data, None if nothing available
        :rtype: object
        """
        if self.get("output_as_list"):
            result = self._output
            self._output = list()
            return result
        else:
            return super().output()
