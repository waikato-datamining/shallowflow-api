class Stoppable:
    """
    Interface for classes that can be stopped.
    """

    def stop_execution(self):
        """
        Stops the actor execution.
        """
        raise NotImplementedError()

    @property
    def is_stopped(self):
        """
        Returns whether the actor was stopped.

        :return: true if stopped
        :rtype: bool
        """
        raise NotImplementedError()
