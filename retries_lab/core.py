"""Calculate a toy client policy; no actual requests, delays, or random jitter."""
IDEMPOTENT = {"GET", "HEAD", "PUT", "DELETE", "OPTIONS"}
METHODS = IDEMPOTENT | {"POST", "PATCH"}
RETRYABLE = {429, 500, 502, 503, 504}


def number(value, label, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("{} must be an integer from {} to {}".format(label, low, high))
    return value


def plan_retry(data):
    if not isinstance(data, dict):
        raise ValueError("Retry input must be an object")
    status, method = data.get("status"), data.get("method", "GET")
    if status is not None:
        number(status, "status", 100, 599)
    if not isinstance(method, str) or method not in METHODS:
        raise ValueError("Unknown or lowercase HTTP method")
    idempotent = data.get("idempotent", False)
    if type(idempotent) is not bool:
        raise ValueError("idempotent must be true or false")
    attempt = number(data.get("attempt", 1), "attempt", 1, 10)
    maximum = number(data.get("max_attempts", 4), "max_attempts", 1, 10)
    base = number(data.get("base_seconds", 1), "base_seconds", 1, 60)
    cap = number(data.get("cap_seconds", 60), "cap_seconds", 1, 3600)
    hint = data.get("retry_after")
    if hint is not None:
        number(hint, "retry_after", 0, 86400)
    if status is not None and status not in RETRYABLE:
        reason = "non_retryable_status"
    elif method not in IDEMPOTENT and not idempotent:
        reason = "unsafe_method"
    elif attempt >= maximum:
        reason = "attempt_limit"
    else:
        delay = min(cap, base * 2 ** (attempt - 1))
        # A supplied retry-after minimum may exceed the normal backoff cap.
        return {"retry": True, "delay_seconds": max(delay, hint or 0), "reason": "retryable_failure"}
    return {"retry": False, "delay_seconds": None, "reason": reason}
