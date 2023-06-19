import ctypes


class Register8:
    """A set of descriptors to store unsigned 8-bit values that roll-over and roll-under.
    """

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None) -> int:
        register = getattr(obj, self.private_name)
        return register.value

    def __set__(self, obj, value: int):
        setattr(obj, self.private_name, ctypes.c_uint8(value))


class Register16(Register8):
    """A set of descriptors to store unsigned 16-bit values that roll-over and roll-under.
    """

    def __set__(self, obj, value: int):
        setattr(obj, self.private_name, ctypes.c_uint16(value))


class Registers:
    """An implementation of the 6502 CPU's registers.
    """

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
    """For the processor status information, this is the unsigned 8-bit value that all of the flags will 'sum' up to.  Used to push/pop the processor status to/from the stack
    """

    _fields_ = [("value", ctypes.c_uint8)]


class StatusFlags(ctypes.Structure):
    """For the processor status information, this is each bit of an unsigned 8-bit value represented as individual bits using a C bitfield.  Makes it easy to set individual flags.
    """

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
    """A C-typed union of bit flags and an unsigned integer to represent the flags used by the 6502 CPU.
    """

    _fields_ = [
        ("status", StatusInt),
        ("flags", StatusFlags),
    ]

    def __init__(self):
        self.flags._unused = True


class MathMixin:

    def add_to_accumulator(self, value: int) -> None:
        """Add the value to the accumulator and set all appropriate flags/registers.

        Args:
            value (int): The value to add to the accumulator.
        """
        if self.ps.flags.decimal:
            self.add_to_accumulator_dec(value)
        else:
            self.add_to_accumulator_bin(value)

    def subtract_from_accumulator(self, value: int) -> None:
        """Subtract the value from the accumulator and set all the appropriate flags/registers.

        Args:
            value (int): The value to subtract from the accumulator.
        """
        if self.ps.flags.decimal:
            self.subtract_from_accumulator_dec(value)
        else:
            self.subtract_from_accumulator_bin(value)

    def add_to_accumulator_bin(self, value: int) -> None:
        """Add the value to the accumulator in binary mode and set all of the appropriate flags/register values.

        Args:
            value (int): The value to add to the accumulator.
        """
        result = value + self.registers.A + self.ps.flags.carry
        self.ps.flags.carry = bool(result > 0xFF)
        result &= 0xFF
        self.ps.flags.overflow = bool(
            (self.registers.A ^ result) & (value ^ result) & 0x80)
        self.ps.flags.negative = bool(result >> 7)
        self.ps.flags.zero = result == 0
        self.registers.A = result

    def add_to_accumulator_dec(self, value: int) -> None:
        """Add the value to the accumulator in decimal mode and set all of the appropriate flags/register values.

        Args:
            value (int): The value to add to the accumulator.
        """
        a = self.registers.A
        v = value
        temp = (a & 0x0F) + (v & 0x0F) + self.ps.flags.carry
        if temp >= 0x0A:
            temp = ((temp + 0x06) & 0x0F) + 0x10
        temp += (a & 0xF0) + (v & 0xF0)
        temp2 = temp
        if temp >= 0xA0:
            temp += 0x60

        self.ps.flags.overflow = bool((~(a ^ v) & (a ^ temp2)) & 0x80)
        self.ps.flags.carry = bool(temp > 99)
        self.ps.flags.negative = bool((temp & 0xFF) >> 7)
        self.ps.flags.zero = ((a + v + self.ps.flags.carry) & 0xFF) == 0
        self.registers.A = (temp & 0xFF)

    def subtract_from_accumulator_bin(self, value: int) -> None:
        """Subtract the value from the accumulator in binary mode, then set all the appropriate flags/registers.

        Args:
            value (int): The value to subtract from the accumulator.
        """
        a = self.registers.A
        c = self.ps.flags.carry
        v = value
        result = a + (v ^ 0xFF) + c
        self.ps.flags.carry = result != (result & 0xFF)
        result &= 0xFF
        self.ps.flags.overflow = bool(
            (a ^ result) & ((v ^ 0xFF) ^ result) & 0x80)
        self.ps.flags.zero = not bool(result)
        self.ps.flags.negative = bool(result & (1 << 7))
        self.registers.A = result

    def subtract_from_accumulator_dec(self, value: int) -> None:
        """Subtract the value from the accumulator in decimal mode, then set all the appropriate flags/registers.

        Args:
            value (int): The value to subtract from the accumulator.
        """
        # After days of frustration, this is slightly altered code from mnaberez's py65
        # project...and I greatly appreciate that it works as does my sanity...
        a = self.registers.A
        v = value

        halfcarry = 1
        decimalcarry = 0
        adjust0 = 0
        adjust1 = 0

        nibble0 = (a & 0xf) + (~v & 0xf) + self.ps.flags.carry
        if nibble0 <= 0xf:
            halfcarry = 0
            adjust0 = 10
        nibble1 = ((a >> 4) & 0xf) + ((~v >> 4) & 0xf) + halfcarry
        if nibble1 <= 0xf:
            adjust1 = 10 << 4

        # the ALU outputs are not decimally adjusted
        aluresult = a + (~v & 0xFF) + self.ps.flags.carry

        if aluresult > 0xFF:
            decimalcarry = 1
        aluresult &= 0xFF

        # but the final result will be adjusted
        nibble0 = (aluresult + adjust0) & 0xf
        nibble1 = ((aluresult + adjust1) >> 4) & 0xf

        self.ps.flags.zero = aluresult == 0
        self.ps.flags.carry = bool(decimalcarry)
        self.ps.flags.overflow = bool(((a ^ v) & (a ^ aluresult)) & 0x80)
        self.ps.flags.negative = bool(aluresult >> 7)
        self.registers.A = (nibble1 << 4) + nibble0
