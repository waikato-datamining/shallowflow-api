from .actor import Actor
from .control import ActorHandler


def find_actor_handlers(actor, must_allow_standalones=False, include_same_level=False):
    """
    Returns a list of actor handlers, starting from the current node (excluded).
    The search goes up in the actor hierarchy, up to the root (i.e., the last
    item in the returned list will be most likely a "Flow" actor).

    :param actor: the starting point
    :type actor: Actor
    :param must_allow_standalones: whether the handler must allow standalones
    :type must_allow_standalones: bool
    :param include_same_level: allows adding of actor handlers that are on
                               the same level as the current actor, but
                               are before it
    :return: the handlers
    :rtype: list
    """
    result = []
    root = actor.root
    child = actor
    parent = actor.parent
    while parent is not None:
        if isinstance(parent, ActorHandler):
            handler = parent
            if include_same_level:
                index = handler.index(child.name)
                for i in range(index - 1, -1, -1):
                    sub_handler = None
                    # TODO external flows
                    if isinstance(handler.actors[i], ActorHandler):
                        sub_handler = handler.actors[i]
                    if sub_handler is None:
                        continue
                    if must_allow_standalones:
                        if sub_handler.actor_handler_info.can_contain_standalones:
                            result.append(sub_handler)
                    else:
                        result.append(sub_handler)
            if must_allow_standalones:
                if handler.actor_handler_info.can_contain_standalones:
                    result.append(handler)
            else:
                result.append(handler)

        if parent == root:
            parent = None
        else:
            child = parent
            parent = parent.parent

    return result


def _find_closest_type(handler, cls):
    """
    Tries to find the cls within the specified actor handler.

    :param handler: the actor handler to search
    :type handler: ActorHandler
    :param cls: the type of actor to look for
    :type cls: type
    :return: the located actor or None if none found
    :rtype: Actor
    """
    result = None
    for actor in handler.actors:
        if isinstance(actor, cls):
            return actor
        # TODO external actors
    return result


def find_closest_type(actor, cls, include_same_level=False):
    """
    Tries to find the closest type in the actor tree, starting with the current
    actor.

    :param actor: the starting point
    :type actor: Actor
    :param cls: the type to look for
    :type cls: type
    :param include_same_level: whether to look on the same level or higher up
    :type include_same_level: bool
    :return: the located actor or None if none found
    :rtype: Actor
    """
    handlers = find_actor_handlers(actor, True, include_same_level=include_same_level)
    for handler in handlers:
        if isinstance(handler, cls):
            return handler
        result = _find_closest_type(handler, cls)
        if result is not None:
            return result
    return None
