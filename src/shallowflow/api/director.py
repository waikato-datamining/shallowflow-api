from .logging import LoggableObject
from .stopping import Stoppable


class AbstractDirector(LoggableObject, Stoppable):
    """
    Ancestor for directors used by control actors.
    """

    def __init__(self, owner):
        """
        Initializes the director.

        :param owner: the owning actor
        :type owner: Actor
        """
        self._stopped = False
        self._owner = owner

    def _check(self, actors):
        """
        For performing checks.

        :param actors: the actors to execute
        :type actors: list
        :return: None if check successful, otherwise error message
        :rtype: str
        """
        if len(actors) == 0:
            return "No actors to execute!"
        return None

    def _do_execute(self, actors):
        """
        Executes the specified list of actors.

        :param actors: the actors to execute
        :type actors: list
        :return: None if successfully executed, otherwise error message
        :rtype: str
        """
        raise NotImplemented()

    def execute(self, actors):
        """
        Executes the specified list of actors.

        :param actors: the actors to execute
        :type actors: list
        :return: None if successfully executed, otherwise error message
        :rtype: str
        """
        self._stopped = False
        result = self._check(actors)
        if result is None:
            result = self._do_execute(actors)
        return result

    def stop_execution(self):
        """
        Stops the actor execution.

        :param msg: the optional stop message
        :type msg: str
        """
        self._stopped = True

    @property
    def is_stopped(self):
        """
        Returns whether the actor was stopped.

        :return: true if stopped
        :rtype: bool
        """
        return self._stopped

    def wrap_up(self):
        """
        Wraps up the execution.
        """
        pass

    def clean_up(self):
        """
        Cleans up the execution.
        """
        self._owner = None
