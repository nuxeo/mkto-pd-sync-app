class Error(Exception):
    """Base class for exceptions in this module.
    """
    def __init__(self, title, message='', *data):
        self.title = title
        self.message = message.format(*data)
 
    def __str__(self):
        return '{}: {}'.format(self.title, self.message)


class InitializationError(Error):
    """Exception raised for errors in the entity initialization.
    """
    pass


class SavingError(Error):
    """Exception raised for errors in the entity saving.
    """
    pass
