class NotFound(Exception):
    """Raises an exception when resource does not exist"""
    pass


class DuplicateValue(Exception):
    """Raises an exception if a duplicate value exists"""
    pass


class PasswordsDoNotMatch(Exception):
    """Raises an exception if a password doesn't match it's hash"""
    pass
