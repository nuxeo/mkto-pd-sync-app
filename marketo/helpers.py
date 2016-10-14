def simple_pluralize(word):
    """
    Simply pluralize word by adding an extra 's' at the end
    taking into account some exceptions.
    >>> simple_pluralize("lead")
    'leads'
    >>> simple_pluralize("opportunity")
    'opportunities'
    """
    plural = word
    if word.endswith("y"):
        plural = plural[:-1] + "ie"
    plural += "s"
    return plural


if __name__ == '__main__':
    import doctest
    doctest.testmod()
