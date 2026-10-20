class DomainError(Exception):
    """Error base de reglas de negocio."""


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class ValidationError(DomainError):
    pass
