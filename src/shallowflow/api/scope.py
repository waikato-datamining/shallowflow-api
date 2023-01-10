class ScopeHandler(object):
    """
    Interface for classes that manage scope within a flow.
    """

    def is_callable_name_used(self, handler, actor):
        """
        Returns whether a callable name is already in use.

        :param handler: the handler for the actor to check
        :type handler: ActorHandler
        :param actor: the actor to check the name for
        :type actor: Actor
        :return: True if already in use
        :rtype: bool
        """
        raise NotImplemented()

    def add_callable_name(self, handler, actor):
        """
        Adds the callable name, if possible.

        :param handler: the handler for the actor to add
        :type handler: ActorHandler
        :param actor: the actor to add
        :type actor: Actor
        :return: None if successfully added, otherwise error message
        :rtype: str
        """
        raise NotImplemented()
