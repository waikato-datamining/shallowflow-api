from shallowflow.api.config import get_class_name


class AbstractContainer(object):
    """
    Ancestor for flow containers.
    """

    def __init__(self):
        """
        Initializes the container.
        """
        self._values = dict()
        self._additional_names = list()
        self._help = dict()
        self._init_help()

    def _add_help(self, name, desc, cls=None):
        """
        Adds the help for a container value.

        :param name: the name of the value to add the help for
        :type name: str
        :param desc: the help string
        :type desc: str
        :param cls: the optional type or types (list)
        """
        if not self._is_valid_name(name):
            return
        if cls is not None:
            desc += "; "
            if isinstance(cls, list):
                desc += ", ".join([get_class_name(x) for x in cls])
            else:
                desc += get_class_name(cls)
        self._help[name] = desc

    def _init_help(self):
        """
        Populates the help strings for the values.
        """
        pass

    def names(self):
        """
        Returns the names of the values that can be stored.

        :return: the list of names
        :rtype: list
        """
        raise NotImplemented()

    def stored(self):
        """
        Returns the names of the values currently stored.

        :return: the list of names
        :rtype: list
        """
        result = list(self._values.keys())
        result.sort()
        return result

    def _is_valid_name(self, name):
        """
        Checks whether the name is valid, ie allowed to be stored.

        :param name: the name to check
        :type name: str
        :return: True if valid
        :rtype: bool
        """
        if name in self._additional_names:
            return True
        if name in self.names():
            return True
        return False

    def has(self, name):
        """
        Checks whether the specified value is stored.

        :param name: the name of the value to look for
        :type name: str
        :return: True if store
        :rtype: bool
        """
        return name in self._values

    def get(self, name):
        """
        Returns the value stored under the specified name.

        :param name: the name of the value to retrieve
        :type name: str
        :return: the value, None if not stored
        """
        if not self.has(name):
            return None
        else:
            return self._values[name]

    def set(self, name, value):
        """
        Sets the value under the specified name (if valid name).

        :param name: the name to store the value under
        :type name: str
        :param value: the value to store
        :return: if successfully stored
        :rtype: bool
        """
        if value is None:
            return False
        if self._is_valid_name(name):
            self._values[name] = value
            return True
        else:
            return False

    def has_help(self, name):
        """
        Checks whether a help string is available for the value.

        :param name: the value to check for the help
        :type name: str
        :return: True if help available
        :rtype: bool
        """
        return name in self._help

    def get_help(self, name):
        """
        Returns the help string for the specified value.

        :param name: the name of the value to get the help for
        :type name: str
        :return: the help string, None if no help available
        :rtype: str
        """
        if not self.has_help(name):
            return None
        else:
            return self._help[name]

    def add_additional_name(self, name):
        """
        Adds the additional value name to allow for storage.

        :param name: the name to allow
        :type name: str
        """
        if name not in self._additional_names:
            self._additional_names.append(name)

    def remove_additional_name(self, name):
        """
        Removes the additional value name from being allowed for storage.

        :param name: the name to remove
        :type name: str
        """
        if name in self._additional_names:
            self._additional_names.remove(name)

    def __str__(self):
        """
        Returns a short string representation of the container.

        :return: the string representation
        :rtype: str
        """
        result = ""
        for name in self.stored():
            if len(result) > 0:
                result += ", "
            result += name + "=" + str(self.get(name))
        return result
