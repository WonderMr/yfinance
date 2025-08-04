class YFException(Exception):
    def __init__(self, description=""):
        super().__init__(description)


class YFDataException(YFException):
    pass


class YFNotImplementedError(NotImplementedError):
    def __init__(self, method_name):
        super().__init__(f"Have not implemented fetching '{method_name}' from Yahoo API")


class YFTickerMissingError(YFException):
    def __init__(self, ticker, rationale):
        super().__init__(f"${ticker}: possibly delisted; {rationale}")
        self.rationale = rationale
        self.ticker = ticker


class YFTzMissingError(YFTickerMissingError):
    def __init__(self, ticker):
        super().__init__(ticker, "no timezone found")


class YFPricesMissingError(YFTickerMissingError):
    def __init__(self, ticker, debug_info):
        self.debug_info = debug_info
        if debug_info != '':
            super().__init__(ticker, f"no price data found {debug_info}")
        else:
            super().__init__(ticker, "no price data found")


class YFEarningsDateMissing(YFTickerMissingError):
    # note that this does not get raised. Added in case of raising it in the future
    def __init__(self, ticker):
        super().__init__(ticker, "no earnings dates found")


class YFInvalidPeriodError(YFException):
    def __init__(self, ticker, invalid_period, valid_ranges):
        self.ticker = ticker
        self.invalid_period = invalid_period
        self.valid_ranges = valid_ranges
        super().__init__(f"{self.ticker}: Period '{invalid_period}' is invalid, "
                         f"must be one of: {valid_ranges}")


class YFRateLimitError(YFException):
    def __init__(self):
        super().__init__("Too Many Requests. Rate limited. Try after a while.")


class YFRequestError(YFException):
    def __init__(self, url, message="", original_exception=None):
        self.url = url
        self.message = message
        self.original_exception = original_exception
        detail = message if message else "Request error"
        detail += f" for url {url}"
        if original_exception is not None:
            detail += f" ({original_exception})"
        super().__init__(detail)


class YFHTTPError(YFRequestError):
    def __init__(self, url, status_code, response_text=""):
        msg = f"HTTP {status_code}"
        if response_text:
            msg += f": {response_text}"
        super().__init__(url, msg)
        self.status_code = status_code
        self.response_text = response_text


class YFConnectionError(YFRequestError):
    def __init__(self, url, original_exception=None):
        super().__init__(url, "Connection error", original_exception)


class YFTimeoutError(YFRequestError):
    def __init__(self, url, timeout, original_exception=None):
        message = f"Request timed out after {timeout} seconds"
        super().__init__(url, message, original_exception)
        self.timeout = timeout
