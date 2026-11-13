from app.errors import AppError


class StatisticsError(AppError):  # Inherits AppError constructor, message, status_code and to_dict.
    """An error while loading or calculating statistics."""
