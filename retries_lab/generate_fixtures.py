"""Original mock HTTP outcomes; no requests or Retry-After header parsing."""


def stop(reason):
    return {"retry": False, "delay_seconds": None, "reason": reason}


def retry(delay):
    return {"retry": True, "delay_seconds": delay, "reason": "retryable_failure"}


def make_case(index):
    kind = index % 12
    data = {"status": 503, "method": "GET"}
    if kind == 0:
        data["attempt"] = 0
        description = "reject zero-based attempt numbers"
    elif kind == 1:
        data["retry_after"] = -1
        description = "reject negative retry-after intervals"
    elif kind == 2:
        data["method"] = "get"
        description = "reject lowercase request methods"
    elif kind == 3:
        data["max_attempts"] = True
        description = "reject boolean attempt limits"
    elif kind == 4:
        data["status"] = 999
        description = "reject out-of-range response statuses"
    elif kind == 5:
        data["status"] = 200
        expected, description = stop("non_retryable_status"), "stop retrying successful responses"
    elif kind == 6:
        data["method"] = "POST"
        expected, description = stop("unsafe_method"), "require explicit idempotence for POST retries"
    elif kind == 7:
        data.update({"attempt": 4, "max_attempts": 4})
        expected, description = stop("attempt_limit"), "stop when the final attempt has been used"
    elif kind == 8:
        attempt = 1 + (index // 12) % 3
        data.update({"attempt": attempt, "base_seconds": 2})
        expected, description = retry(2 ** attempt), "calculate exponential backoff for retryable failures"
    elif kind == 9:
        data.update({"method": "POST", "idempotent": True, "base_seconds": 2})
        expected, description = retry(2), "allow caller-declared idempotent POST requests"
    elif kind == 10:
        data.update({"status": 429, "retry_after": 120, "cap_seconds": 60})
        expected, description = retry(120), "honor retry-after minima above the backoff cap"
    else:
        data.update({"status": None, "attempt": 2})
        expected, description = retry(2), "plan a retry after a connection failure"
    result = {"id": "retries-{:04d}".format(index), "description": description, "input": data}
    result.update({"expected_error": True} if kind < 5 else {"expected": expected})
    return result
