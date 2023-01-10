import json
import os
import pickle
import traceback
import yaml
from .config import optionhandler_to_dict, dict_to_optionhandler
from .serialization.vars import AbstractStringReader, add_string_reader
from .actor import Actor, FLOW_DIR, FLOW_PATH
from .logging import log

FLOW_READERS = None
""" contains all flow readers (.ext -> reader)"""

FLOW_WRITERS = None
""" contains all flow writers (.ext -> writer)"""


class File(str):
    """
    Simple class to differentiate files from plain strings.
    """
    pass


class Directory(str):
    """
    Simple class to differentiate directories from plain strings.
    """
    pass


class FileStringReader(AbstractStringReader):
    """
    Turns strings into File objects.
    """

    def handles(self, cls):
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, File)

    def convert(self, s, base_type=None):
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        return File(s)


class DirectoryStringReader(AbstractStringReader):
    """
    Turns strings into Directory objects.
    """

    def handles(self, cls):
        """
        Whether it can convert a string into the specified class.

        :param cls: the class to convert to
        :type cls: type
        :return: True if it can handle it
        """
        return issubclass(cls, Directory)

    def convert(self, s, base_type=None):
        """
        Turns the string into an object.

        :param s: the string to convert
        :type s: str
        :param base_type: optional type when reconstructing lists etc
        :return: the generated object
        """
        return Directory(s)


def fix_extension(ext):
    """
    Ensures that the extension starts with a dot.

    :param ext: the extension to (potentially) fix
    :type ext: str
    :return: the (potentially) fixed extension
    :rtype: str
    """
    if not ext.startswith("."):
        return "." + ext
    else:
        return ext


def get_flow_readers():
    """
    Returns the registered readers.

    :return: the readers
    :rtype: dict
    """
    global FLOW_READERS
    if FLOW_READERS is None:
        FLOW_READERS = dict()
    return FLOW_READERS


def get_reader_extensions():
    """
    Returns a list of extensions for which readers are available.

    :return: the list of extensions
    :rtype: list
    """
    result = list(get_flow_readers().keys())
    result.sort()
    return result


def add_flow_reader(ext, reader):
    """
    Adds a reader for the specified extension.

    :param ext: the extension to add the reader for (incl. dot)
    :type ext: str
    :param reader: the reader method to add
    :type reader: object
    """
    get_flow_readers()[fix_extension(ext)] = reader


def has_flow_reader(ext):
    """
    Checks whether a reader is registered for the extension.

    :param ext: the extension to check
    :type ext: str
    :return: true if reader registered
    :rtype: bool
    """
    return fix_extension(ext) in get_flow_readers()


def get_flow_reader(ext):
    """
    Returns the reader registered for the extension.

    :param ext: the extension to get the reader for
    :type ext: str
    :return: the reader method, None if none registered
    :rtype: object
    """
    if has_flow_reader(fix_extension(ext)):
        return get_flow_readers()[fix_extension(ext)]
    else:
        return None


def get_flow_writers():
    """
    Returns the registered writers.

    :return: the writers
    :rtype: dict
    """
    global FLOW_WRITERS
    if FLOW_WRITERS is None:
        FLOW_WRITERS = dict()
    return FLOW_WRITERS


def get_writer_extensions():
    """
    Returns a list of extensions for which writers are available.

    :return: the list of extensions
    :rtype: list
    """
    result = list(get_flow_writers().keys())
    result.sort()
    return result


def add_flow_writer(ext, writer):
    """
    Adds a writer for the specified extension.

    :param ext: the extension to add the writer for
    :type ext: str
    :param writer: the writer method to add
    :type writer: object
    """
    get_flow_writers()[fix_extension(ext)] = writer


def has_flow_writer(ext):
    """
    Checks whether a writer is registered for the extension.

    :param ext: the extension to check
    :type ext: str
    :return: true if writer registered
    :rtype: bool
    """
    return fix_extension(ext) in get_flow_writers()


def get_flow_writer(ext):
    """
    Returns the writer registered for the extension.

    :param ext: the extension to get the writer for
    :type ext: str
    :return: the writer method, None if none registered
    :rtype: object
    """
    if has_flow_writer(fix_extension(ext)):
        return get_flow_writers()[fix_extension(ext)]
    else:
        return None


def add_flow_vars(actor, path):
    """
    Adds variables derived from the path to the actor's variables.

    :param actor: the actor to update
    :type actor: Actor
    :param path: the path to use
    :type path: str
    :return: the (potentially) updated actor
    :rtype: Actor
    """
    if actor is None:
        return None

    if path is not None:
        actor.variables.set(FLOW_PATH, path)
        actor.variables.set(FLOW_DIR, os.path.dirname(path))

    return actor


def load_json_actor(path):
    """
    Loads a actor from the given JSON file.

    :param path: the file containing an actor in JSON (.json) format.
    :type path: str
    :return: the actor, None if failed to load
    :rtype: Actor
    """
    try:
        with open(path, "r") as jf:
            d = json.load(jf)
        return dict_to_optionhandler(d)
    except:
        print("Failed to load actor from: %s\n%s" % (path, traceback.format_exc()))
        return None


def load_yaml_actor(path):
    """
    Loads a actor from the given YAML file.

    :param path: the file containing an actor in YAML (.yaml) format.
    :type path: str
    :return: the actor, None if failed to load
    :rtype: Actor
    """
    try:
        with open(path, "r") as yf:
            d = yaml.safe_load(yf)
        return dict_to_optionhandler(d)
    except:
        print("Failed to load actor from: %s\n%s" % (path, traceback.format_exc()))
        return None


def load_pickle_actor(path):
    """
    Loads a actor from the given pickle file.

    :param path: the file containing an actor in pickle (.pkl) format.
    :type path: str
    :return: the actor, None if failed to load
    :rtype: Actor
    """
    try:
        with open(path, "rb") as pf:
            b = pf.read()
            d = pickle.loads(b)
        return dict_to_optionhandler(d)
    except:
        print("Failed to load actor from: %s\n%s" % (path, traceback.format_exc()))
        return None


def load_actor(path):
    """
    Loads a actor from the given file.

    :param path: the file containing an actor
    :type path: str
    :return: the actor, None if failed to load
    :rtype: Actor
    """
    ext = os.path.splitext(path)[1]
    if has_flow_reader(ext):
        return add_flow_vars(get_flow_reader(ext)(path), path)
    else:
        log("Failed to find flow reader for extension '%s' (file: %s)" % (ext, path))
        return None


def save_json_actor(actor, path):
    """
    Saves the actor to the given JSON file.

    :param actor: the actor to save
    :type actor: Actor
    :param path: the file to save the actor in JSON (.json) format
    :type path: str
    :return: None if successfully saved, otherwise error message
    :rtype: str
    """
    d = optionhandler_to_dict(actor)
    try:
        with open(path, "w") as jf:
            json.dump(d, jf, indent=2)
        return None
    except:
        return "Failed to save actor to: %s\n%s" % (path, traceback.format_exc())


def save_yaml_actor(actor, path):
    """
    Saves the actor to the given YAML file.

    :param actor: the actor to save
    :type actor: Actor
    :param path: the file to save the actor in YAML (.yaml) format
    :type path: str
    :return: None if successfully saved, otherwise error message
    :rtype: str
    """
    d = optionhandler_to_dict(actor)
    try:
        with open(path, "w") as yf:
            yaml.safe_dump(d, yf)
        return None
    except:
        return "Failed to save actor to: %s\n%s" % (path, traceback.format_exc())


def save_pickle_actor(actor, path):
    """
    Saves the actor to the given pickle file.

    :param actor: the actor to save
    :type actor: Actor
    :param path: the file to save the actor in pickle (.pkl) format
    :type path: str
    :return: None if successfully saved, otherwise error message
    :rtype: str
    """
    d = optionhandler_to_dict(actor)
    try:
        with open(path, "wb") as pf:
            pf.write(pickle.dumps(d))
            pf.flush()
        return None
    except:
        return "Failed to save actor to: %s\n%s" % (path, traceback.format_exc())


def save_actor(actor, path):
    """
    Saves the actor to the given file.

    :param actor: the actor to save
    :type actor: Actor
    :param path: the file to save the actor in JSON (.json) or YAML (.yaml) format
    :type path: str
    :return: None if successfully saved, otherwise error message
    :rtype: str
    """
    ext = os.path.splitext(path)[1]
    if has_flow_writer(ext):
        return get_flow_writer(ext)(actor, path)
    else:
        log("Failed to find flow writer for extension '%s' (file: %s)" % (ext, path))
        return None


def actor_to_json(actor):
    """
    Turns the actor into JSON representation.

    :param actor: the actor to convert
    :type actor: Actor
    :return: the generated string
    :rtype: str
    """
    d = optionhandler_to_dict(actor)
    return json.dumps(d, indent=2)


def json_to_actor(s):
    """
    Parses the JSON string and returns the actor.

    :param s: the string to parse
    :type s: str
    :return: the generated actor, None if failed to do so
    :rtype: Actor
    """
    try:
        d = json.loads(s)
        return dict_to_optionhandler(d)
    except Exception:
        log("Failed to parse JSON string as actor: %s" % s)
        return None


# JSON
add_flow_reader(".json", load_json_actor)
add_flow_writer(".json", save_json_actor)

# YAML
add_flow_reader(".yaml", load_yaml_actor)
add_flow_writer(".yaml", save_yaml_actor)

# pickle
add_flow_reader(".pkl", load_pickle_actor)
add_flow_writer(".pkl", save_pickle_actor)

# serialization
add_string_reader(FileStringReader)
add_string_reader(DirectoryStringReader)
