class ParamInfoException(Exception):
    ...


class ParamInfoNotFoundError(ParamInfoException):
    def __init__(self):
        self.status_code = 404
        self.detail = "Param Info Not Found"


class ParamInfoInfoAlreadyExistError(ParamInfoException):
    def __init__(self):
        self.status_code = 409
        self.detail = "Param Info Already Exists"