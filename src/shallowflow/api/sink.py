from .actor import InputConsumer
from .config import Option
from .io import File

STATE_INPUT = "input"


class AbstractSimpleSink(InputConsumer):
    """
    Ancestor for simple source actors.
    """

    def reset(self):
        """
        Resets the state of the actor.
        """
        super().reset()
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

    def _post_execute(self):
        """
        After the actual code got executed.
        """
        self._input = None


class AbstractFileWriter(AbstractSimpleSink):
    """
    Ancestor for sinks that write files to disk.
    """

    def _define_options(self):
        """
        For configuring the options.
        """
        super()._define_options()
        self._option_manager.add(Option("output_file", File, File("."), self._output_file_help()))

    def _output_file_help(self):
        """
        Returns the help string for the 'output_file' option.

        :return: the help string
        :rtype: str
        """
        return "The file to write to; can contain variables"
