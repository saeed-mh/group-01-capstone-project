class AppError(Exception):
    """Base class for errors the app raises on purpose."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        return {"error": self.message}
