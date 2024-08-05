#####################################################################################################

from typing import Any

from fastapi.exceptions import HTTPException

#####################################################################################################

class AppException(HTTPException):
    #####################################################################################################

    def __init__(
        self,
        detail: Any = None,
        err_code: str = 'INTERNAL_SERVER_ERROR',
        status_code: int = 500,
        headers: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
        self.err_code = err_code

#####################################################################################################

class ShutdownException(AppException):
    """NOTHING."""

#####################################################################################################
