import ctypes
from functools import wraps


class Register8:

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None) -> int:
        register = getattr(obj, self.private_name)
        return register.value

    def __set__(self, obj, value: int):
        setattr(obj, self.private_name, ctypes.c_uint8(value))


class Register16(Register8):

    def __set__(self, obj, value: int):
        setattr(obj, self.private_name, ctypes.c_uint16(value))


class Registers:

    A = Register8()
    X = Register8()
    Y = Register8()
    program_counter = Register16()
    stack_pointer = Register8()

    def __init__(self):
        self.A = 0x00
        self.X = 0x00
        self.Y = 0x00
        self.program_counter = 0x0000
        self.stack_pointer = 0xFF


class StatusInt(ctypes.Structure):

    _fields_ = [("value", ctypes.c_uint8)]


class StatusFlags(ctypes.Structure):

    _fields_ = [
        ("carry", ctypes.c_uint8, 1),
        ("zero", ctypes.c_uint8, 1),
        ("interrupt_mask", ctypes.c_uint8, 1),
        ("decimal", ctypes.c_uint8, 1),
        ("pbreak", ctypes.c_uint8, 1),
        ("_unused", ctypes.c_uint8, 1),
        ("overflow", ctypes.c_uint8, 1),
        ("negative", ctypes.c_uint8, 1),
    ]


class Status(ctypes.Union):

    _fields_ = [
        ("status", StatusInt),
        ("flags", StatusFlags),
    ]

    def __init__(self):
        self.flags._unused = True
