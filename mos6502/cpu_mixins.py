from typing import Tuple


class AddressingMixin:
    """A CPU mixin that implements all of the addressing methods for 6502 instructions along with helper methods.
    """

    @staticmethod
    def inc_no_carry(value: int) -> int:
        """Increments the low-byte of an address without carrying to the high byte

        Args:
            value (int): the value to increment

        Returns:
            value (int): the value incremented while ignoring any carry operations to the high byte
        """
        value &= 0xFFFF
        address = (value + 1 & 0xFF) + (value & 0xFF00)
        return address

    # Addressing functions
    def _a_x_indexed_zp_indirect(self) -> Tuple[int, int]:
        """Retrieve the address by adding the second byte of the instruction to the X register (no carry).  The result is then used as a zero page address where two bytes are read and the data from that address is used to get the data.

        Example: `XXX ($nn,X)`

        Returns:
            tuple (int, int): Address referenced and the data at the location.
        """
        offset = self.read_value()
        address = (offset + self.registers.X) & 0xFF
        address = self.bus.read(address) + (self.bus.read(address + 1) << 8)
        address &= 0xFFFF
        return (address, self.bus.read(address))

    def _a_zp_indirect_y_indexed(self) -> Tuple[int, int]:
        """Retrieve the address by taking the second byte of the instruction and reading that location in the zero page.  After grabbing the data from zero page, add the Y register to that address and get the data at the new address.

        Example: `XXX ($nn),Y`

        Returns:
            tuple (int, int): Address referenced and the data at the location.
        """
        offset = self.read_value()
        address = self.bus.read(
            offset) + (self.bus.read(offset + 1) << 8) + self.registers.Y
        address &= 0xFFFF
        return (address, self.bus.read(address))

    def _a_zero_page(self) -> Tuple[int, int]:
        """Retrieve the address by taking the second byte of the instruction and reading the data in the zero page referenced by the second byte.

        Example: `XXX $nn`

        Returns:
            tuple (int, int): Address referenced and the data at the location.
        """
        address = self.read_value()
        address &= 0xFF
        return (address, self.bus.read(address))

    def _a_zero_page_indexed(self, register: str) -> Tuple[int, int]:
        """Retrieve the address by taking the second byte of the instruction, then adding the contents of the specified register, then looking up the value at that address on the zero page.  There is no carry when adding the register to the second byte of the instruction.

        Example: `XXX $nn,X` or `XXX $nn,Y`

        Args:
            register (str): The register to use.

        Returns:
            tuple (int, int): Address referenced and the data at the location.
        """
        address = self.read_value() + getattr(self.registers, register)
        address &= 0xFF
        return (address, self.bus.read(address))

    def _a_absolute(self) -> Tuple[int, int]:
        """Retrieve the data by directly referencing the address given in the second (low) and third (high) bytes of the instruction.

        Example: `XXX $nnnn`

        Returns:
            tuple (int, int): Address referenced and the data at the location.
        """
        address = self.read_value() + (self.read_value() << 8)
        address &= 0xFFFF
        return (address, self.bus.read(address))

    def _a_indirect(self) -> Tuple[int, int]:
        """Retrieve the data by getting the data specified at the second (low) and third (high) bytes of the instruction, then take that data and use it as an address to retrieve the relevant data.

        Example: `XXX ($nnnn)`

        Returns:
            tuple (int, int): Address referenced and the data at the location.
        """
        addr_low, addr_high = self.read_value(), self.read_value()
        address = addr_low + (addr_high << 8)
        address_next = self.inc_no_carry(address)

        next_address = self.bus.read(
            address) + (self.bus.read(address_next) << 8)
        next_address &= 0xFFFF
        return (next_address, self.bus.read(address))

    def _a_indexed_absolute(self, register: str) -> Tuple[int, int]:
        """Retrieve the data at the address specified in the second (low) and third (high) bytes of the instruction plus the contents of the specified register.

        Example: `XXX $nnnn,X` or `XXX $nnnn,Y`

        Args:
            register (str): The register to use.

        Returns:
            tuple (int, int): Address referenced and the data at the location.
        """
        r = getattr(self.registers, register)
        address = self.read_value() + (self.read_value() << 8) + r
        address &= 0xFFFF
        return (address, self.bus.read(address))

    def _a_immediate(self) -> Tuple[None, int]:
        """Retrieve the data at the second byte of the instruction, and return the data.  This method does not return an address as the second byte of the instruction holds the relevant data.

        Example: `XXX #$nn`

        Returns:
            tuple (None, int): None (since there is no associated address) and the data at the location.
        """
        return (None, self.read_value())


class MathMixin:
    """A CPU mixin that implements the ADC and SBC math functions to include binary and decimal modes.
    """

    # Main "math" functions
    def add_to_accumulator(self, value: int) -> None:
        """Add the value to the accumulator and set all appropriate flags/registers.

        Args:
            value (int): The value to add to the accumulator.
        """
        if self.ps.flags.decimal:
            self.__add_to_accumulator_dec(value)
        else:
            self.__add_to_accumulator_bin(value)

    def subtract_from_accumulator(self, value: int) -> None:
        """Subtract the value from the accumulator and set all the appropriate flags/registers.

        Args:
            value (int): The value to subtract from the accumulator.
        """
        if self.ps.flags.decimal:
            self.__subtract_from_accumulator_dec(value)
        else:
            self.__subtract_from_accumulator_bin(value)


    def __add_to_accumulator_bin(self, value: int) -> None:
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

    def __add_to_accumulator_dec(self, value: int) -> None:
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

    def __subtract_from_accumulator_bin(self, value: int) -> None:
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

    def __subtract_from_accumulator_dec(self, value: int) -> None:
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


class StackMixin:
    """Stack methods associated with pulling and pushing values onto the stack.
    """

    def _s_push_address(self, address: int):
        """Push an address onto the stack

        Args:
            address (int): an unsigned 16-bit address
        """
        address = (address - 1) & 0xFFFF
        self._s_push_byte(address >> 8)
        self._s_push_byte(address & 0xFF)

    def _s_push_byte(self, value: int):
        """Push a single byte onto the stack

        Args:
            value (int): an unsigned 8-bit value
        """
        value &= 0xFF
        address = 0x100 + self.registers.stack_pointer
        self.registers.stack_pointer -= 1
        self.bus.write(address, value)

    def _s_pop_address(self) -> int:
        """Pop an address off the stack

        Returns:
            int: A 16-bit unsigned integer address
        """
        return self._s_pop_byte() + (self._s_pop_byte() << 8)

    def _s_pop_byte(self) -> int:
        """Pop a byte off of the stack

        Returns:
            int: An 8-bit unsigned integer value
        """
        self.registers.stack_pointer += 1
        address = 0x100 + self.registers.stack_pointer
        value = self.bus.read(address)
        return value
