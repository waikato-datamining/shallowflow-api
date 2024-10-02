import os
from coed.config import Option


def actual_num_threads(num_threads: int) -> int:
    """
    Returns the actual number of threads.

    :param num_threads: the threads to use, 0=all, negative number #cores+num_threads
    :type num_threads: int
    :return: the actual number of threads to use
    :rtype: int
    """
    num_cores = os.cpu_count()
    if num_threads == 0:
        result = num_cores
    elif num_threads > 0:
        result = min(num_threads, num_cores)
    else:
        result = num_cores + num_threads
    return result


def num_threads_option(def_num_threads: int = 1) -> Option:
    """
    Configures an Option object to use for num_threads.

    :param def_num_threads: the default number of threads
    :type def_num_threads: int
    :return: the configured Option object
    :rtype: Option
    """
    return Option(name="num_threads", value_type=int, def_value=def_num_threads,
                  help="The number of threads to use; 0: all cores; >0: specific number of cores (capped at actual number of cores); <0: #cores + num_threads")
