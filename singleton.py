class Singleton(type):
    """
    Implements the Singleton design pattern for the ExtractMatches class.

    This metaclass ensures that each competition has its own instance of the ExtractMatches class, and it manages
    sending scheduled matches to a shared rich table. By using the Singleton approach, all matches are consolidated
    into a single table, which is only printed at the end. This approach eliminates the need for multiple tables for
    each competition.

    Attributes:
        _instances (dict): A dictionary to store instances of classes using this metaclass.

    Methods:
        __call__(*args, **kwargs): Creates and returns a new instance if it doesn't exist, otherwise returns the
        existing instance.

    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]