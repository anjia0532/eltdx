"""eltdx exception hierarchy."""


class EltdxError(Exception):
    """Base class for package errors."""


class ProtocolError(EltdxError):
    """Raised when protocol encoding or decoding fails."""


class MissingCodesError(ProtocolError):
    """A batch contains confirmed missing codes; no partial result is returned."""

    def __init__(self, missing_codes):
        self.missing_codes = tuple(missing_codes)
        super().__init__("batch data missing for codes: " + ", ".join(self.missing_codes))


class MissingCodesWarning(RuntimeWarning):
    """Explicit skip mode omitted confirmed missing codes from a batch."""


class ResourceFormatError(EltdxError):
    """Raised when a downloaded TDX resource has an invalid format."""


class TdxStatsDateError(ResourceFormatError):
    """Raised when a TDX statistics resource cannot match the target session."""


class ShortlineIndicatorsNotReadyError(EltdxError):
    """Raised when current-session shortline inputs are not ready yet."""


class TransportError(EltdxError):
    """Raised when the transport cannot complete a request."""


class ConnectionClosedError(TransportError):
    """Raised when the remote server closes the connection."""


class ResponseTimeoutError(TransportError):
    """Raised when a request does not receive a response in time."""


class PoolBusyError(TransportError):
    """Raised when bounded pool admission has no remaining capacity."""


class PushOverflowError(TransportError):
    """Raised once after the bounded push buffer drops frames."""


class TransportCloseTimeoutError(TransportError):
    """Raised when a transport cannot prove resource shutdown in time."""


class UnsupportedCommandError(EltdxError):
    """Raised when an API method has no migrated 7709 command yet."""
