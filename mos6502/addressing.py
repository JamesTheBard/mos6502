from typing import Tuple


class AddressingMixin:

    @staticmethod
    def inc_no_carry(value: int) -> int:
        """
        Increments the low-byte of an address without carrying to the high byte
        """
        value &= 0xFFFF
        address = (value + 1 & 0xFF) + (value & 0xFF00)
        return address

    # Addressing functions
    def _a_x_indexed_zp_indirect(self) -> Tuple[int, int]:
        """Retrieve the address by adding the second byte of the instruction to the X register (no carry).  The result is then used as a zero page address where two bytes are read and the data from that address is used to get the data.
        
        Example: `XXX ($nn,X)`

        Returns:
            tuple: Address referenced and the data at the location.
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
            tuple: Address referenced and the data at the location.
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
            tuple: Address referenced and the data at the location.
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
            tuple: Address referenced and the data at the location.
        """
        address = self.read_value() + getattr(self.registers, register)
        address &= 0xFF
        return (address, self.bus.read(address))

    def _a_absolute(self) -> Tuple[int, int]:
        """Retrieve the data by directly referencing the address given in the second (low) and third (high) bytes of the instruction.
        
        Example: `XXX $nnnn`

        Returns:
            tuple: Address referenced and the data at the location.
        """
        address = self.read_value() + (self.read_value() << 8)
        address &= 0xFFFF
        return (address, self.bus.read(address))

    def _a_indirect(self) -> Tuple[int, int]:
        """Retrieve the data by getting the data specified at the second (low) and third (high) bytes of the instruction, then take that data and use it as an address to retrieve the relevant data.
        
        Example: `XXX ($nnnn)`

        Returns:
            tuple: Address referenced and the data at the location.
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
            tuple: Address referenced and the data at the location.
        """
        r = getattr(self.registers, register)
        address = self.read_value() + (self.read_value() << 8) + r
        address &= 0xFFFF
        return (address, self.bus.read(address))

    def _a_immediate(self) -> Tuple[None, int]:
        """Retrieve the data at the second byte of the instruction, and return the data.  This method does not return an address as the second byte of the instruction holds the relevant data.
        
        Example: `XXX #$nn`

        Returns:
            tuple: Address referenced and the data at the location.
        """
        return (None, self.read_value())
