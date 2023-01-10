class Unknown(object):
    """
    Dummy class used for compatibility checks. Matches with everything.
    """
    pass


def check_compatibility(output, input, strict=False):
    """
    Checks the compatibility between two classes.

    :param output: the generated class
    :param input: the accepted class
    :param strict: whether to be strict in the check
    :type strict: bool
    :return: True if compatible
    :rtype: bool
    """
    # unknown matches always
    if not strict:
        if issubclass(input, Unknown) or issubclass(output, Unknown):
            return True

    # both lists?
    if issubclass(output, list) and issubclass(input, list):
        return True

    if issubclass(output, list) != issubclass(input, list):
        return False

    if (input == object) and not strict:
        return True

    # exact match?
    if input == output:
        return True

    # does input accept superclass?
    if issubclass(output, input):
        return True

    return False


def is_compatible(output, input, strict=False):
    """
    Checks whether the classes are compatible.

    :param output: the class or list of classes that get generated
    :param input: the class or list of classes that can be accepted
    :param strict: whether to be strict
    :type strict: bool
    :return: True if compatible
    :rtype: bool
    """
    result = False

    if not isinstance(output, list):
        output = [output]
    if not isinstance(input, list):
        input = [input]

    for i in range(len(output)):
        out = output[i]
        for n in range(len(input)):
            inp = input[n]
            if check_compatibility(out, inp, strict=strict):
                result = True
                break

        if result:
            break

    return result
