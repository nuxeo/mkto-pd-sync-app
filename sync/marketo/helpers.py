from re import compile


def is_marketo_guid(id_):
    """
    Return True if the given id is a Marketo GUID, False otherwise.
    >>> is_marketo_guid('6a38a3bd-edce-4d86-bcc0-83f1feef8997')
    True
    >>> is_marketo_guid('7591021')
    False
    """
    p = compile('[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}')
    return p.match(str(id_))


def compute_external_id(pd_entity_name, id_, prefix='pd'):
    """
    Compute an external id for a Marketo entity.
    :param pd_entity_name: The Pipedrive entity name it is synchronized from.
    :param id_: The Pipedrive entity id it is synchronized from.
    :param prefix: A custom prefix, default is "pd" (assuming it is synchronized from Pipedrive)
    :return:
    """
    return prefix + '-' + pd_entity_name + '-' + str(id_)


if __name__ == '__main__':
    import doctest

    doctest.testmod()
