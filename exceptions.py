class BaseError(Exception):

    def __init__(self, message: str):
        self.message = message

    def __repr__(self):
        return f'{self.message}'

    def __str__(self):
        return f'{self.message}'



class BusOffsetNotPageAlignedError(BaseError):

    def __init__(self):
        message = "Bus object offset not aligned to page boundary"
        super().__init__(message)


class BusOffsetOutsideAddressSpaceError(BaseError):

    def __init__(self):
        message = "Bus object offset outside addressable range (0x0000 to 0xFFFF)"
        super().__init__(message)


class BusAddressError(BaseError):

    def __init__(self):
        message = "Cannot attach due to the address space overlapping another attached bus object"
        super().__init__(message)