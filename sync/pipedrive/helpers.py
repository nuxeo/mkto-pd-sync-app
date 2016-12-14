import string
from re import compile


def to_snake_case(label):
    """
    Convert a standard label to snake case variable name.
    >>> to_snake_case('My Label')
    'my_label'
    >>> to_snake_case('State/Country')
    'state_country'
    >>> to_snake_case('my-label')
    'my_label'
    >>> to_snake_case('Date SQL')
    'date_sql'
    """
    # TODO: add cases
    # "MarketoId" -> "marketo_id" (now "marketoid")
    # "No. of Employees (Range)" (now "no__of_employees__range_")
    filterpunct = compile('[%s\ ]' % string.punctuation)
    alphafilter = compile('[%s%s_-]' % (string.digits,
                                        string.ascii_letters))
    name = filterpunct.sub('_', label.lower())
    return ''.join(alphafilter.findall(name))


if __name__ == '__main__':
    import doctest

    doctest.testmod()
