from .actor import Actor
from .config import Option
from .director import AbstractDirector


class ActorHandlerInfo(object):
    """
    For storing meta-information about an ActorHandler.
    """

    def __init__(self, can_contain_standalones=False, can_contain_source=False):
        """
        Initializes the info object.

        :param can_contain_standalones: whether standalones can be added
        :type can_contain_standalones: bool
        :param can_contain_source: whether a source can be added
        :type can_contain_source: bool
        """
        self.can_contain_standalones = can_contain_standalones
        self.can_contain_source = can_contain_source


class ActorHandler(Actor):
    """
    Interface for actors that manage sub-actors.
    """

    def _define_options(self):
        """
        For configuring the options.
        """
        super()._define_options()
        self.option_manager.add(Option(name="actors", value_type=list, def_value=list(),
                                       help="The sub-actors to manage", base_type=Actor))

    def _new_director(self):
        """
        Returns the director to use for executing the actors.

        :return: the director
        :rtype: AbstractDirector
        """
        raise NotImplemented()

    @property
    def actor_handler_info(self):
        """
        Returns meta-info about itself.

        :return: the info
        :rtype: ActorHandlerInfo
        """
        raise NotImplemented()

    @property
    def actors(self):
        """
        Returns the current sub-actors.

        :return: the sub-actors
        :rtype: list
        """
        return self._option_manager.get("actors")

    @actors.setter
    def actors(self, actors):
        """
        Sets the new sub-actors.

        :param actors: the new actors
        :type actors: list
        """
        for a in actors:
            if not isinstance(a, Actor):
                raise Exception("Can only set objects of type Actor!")
            a.parent = self

        # ensure that names are unique
        names = []
        for a in actors:
            name = a.name
            if name in names:
                i = 1
                while name in names:
                    i += 1
                    name = a.name + " (" + str(i) + ")"
                a.set("name", name)
                names.append(name)
            else:
               names.append(name)

        msg = self._check_actors(actors)
        if msg is not None:
            raise Exception(msg)

        self._option_manager.set("actors", actors)

    def manage(self, actors):
        """
        Same as using the 'actors' property for setting the actors to manage,
        but returns itself, allowing for method chaining.

        :param actors: the new actors to manage
        :type actors: list
        :return: itself
        :rtype: ActorHandler
        """
        self.actors = actors
        return self

    def index(self, actor):
        """
        Returns the index of the actor in the managed list of actors.

        :param actor: the actor to look for (Actor or actor name)
        :return: the index, -1 if not found
        :rtype: int
        """
        result = -1
        if isinstance(actor, str):
            for i, a in enumerate(self.actors):
                if a.name == actor:
                    result = i
                    break
        else:
            if actor in self.actors:
                result = self.actors.index(actor)
        return result

    @property
    def first_active(self):
        """
        Returns the first non-skipped actor.

        :return: the first active Actor, None if none available
        :rtype: Actor
        """
        for actor in self.actors:
            if not actor.is_skipped:
                return actor
        return None

    @property
    def last_active(self):
        """
        Returns the last non-skipped actor.

        :return: the last active Actor, None if none available
        :rtype: Actor
        """
        for i in range(len(self.actors) - 1, -1, -1):
            if not self.actors[i].is_skipped:
                return self.actors[i]
        return None

    def __len__(self):
        """
        Returns the number of actors.

        :return: the number of actors
        :rtype: int
        """
        return len(self.actors)

    def _check_actors(self, actors):
        """
        Performs checks on the sub-actors.

        :param actors: the actors to check
        :type actors: list
        :return: None if successful check, otherwise error message
        :rtype: str
        """
        return None

    def setup(self):
        """
        Prepares the actor for use.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        result = super().setup()
        if result is None:
            result = self._check_actors(self.actors)
        if result is None:
            for actor in self.actors:
                actor.parent = self
                result = actor.setup()
                if result is not None:
                    break
        if result is None:
            self._director = self._new_director()

        return result

    def _do_execute(self):
        """
        Performs the actual execution.

        :return: None if successful, otherwise error message
        :rtype: str
        """
        return self._director.execute(self.actors)

    def stop_execution(self):
        """
        Stops the actor execution.
        """
        if self._director is not None:
            self._director.stop_execution()
        for actor in self.actors:
            actor.stop_execution()
        super().stop_execution()

    def wrap_up(self):
        """
        For finishing up the execution.
        Does not affect graphical output.
        """
        for actor in self.actors:
            actor.wrap_up()
        if self._director is not None:
            self._director.wrap_up()
        super().wrap_up()

    def clean_up(self):
        """
        Also cleans up graphical output.
        """
        for actor in self.actors:
            actor.clean_up()
        if self._director is not None:
            self._director.clean_up()
        super().clean_up()


class MutableActorHandler(ActorHandler):
    """
    Ancestor for actor handlers that allow appending, removing of actors.
    """

    def append(self, actor):
        """
        Appends the specified actor.

        :param actor: the actor to append
        :type actor: Actor
        :return: itself
        :rtype: MutableActorHandler
        """
        actors = self.actors
        actors.append(actor)
        self.actors = actors
        return self

    def remove(self, actor):
        """
        Removes the specified actor.

        :param actor: the actor to remove
        :type actor: Actor
        :return: itself
        :rtype: MutableActorHandler
        """
        actors = self.actors
        if actor in actors:
            actors.remove(actor)
            self.actors = actors
        return self

    def clear(self):
        """
        Removes all actors.

        :return: itself
        :rtype: MutableActorHandler
        """
        self.actors = []
        return self
