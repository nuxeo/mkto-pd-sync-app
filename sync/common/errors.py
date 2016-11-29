class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InitializationError(Error):
    """Exception raised for errors in the resource initialization.
    """
    pass


class SavingError(Error):
    """Exception raised for errors in the resource saving.
    """
    pass
