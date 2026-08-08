class AppError(Exception):
    code = "application_error"
    status_code = 400

    def __init__(self, message: str | None = None, *, details: list | None = None):
        super().__init__(message or self.code)
        self.message = message or self.code
        self.details = details or []


class InvalidSubmission(AppError):
    code = "invalid_submission"
    status_code = 422


class PayloadTooLarge(AppError):
    code = "payload_too_large"
    status_code = 413


class OriginDenied(AppError):
    code = "origin_denied"
    status_code = 403


class WidgetNotFound(AppError):
    code = "widget_not_found"
    status_code = 404


class RateLimitExceeded(AppError):
    code = "rate_limit_exceeded"
    status_code = 429

    def __init__(self, retry_after: int):
        super().__init__("Too many submissions. Try again later.")
        self.retry_after = retry_after
