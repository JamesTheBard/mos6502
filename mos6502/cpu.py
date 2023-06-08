from typing import Optional

from mos6502.bus import Bus
from mos6502.instructions import generate_inst_map
from mos6502.periphery import Registers, Status

inst_map = generate_inst_map()


def convert_int(value: int) -> int:
    """
    Convert unsigned int into a properly signed int.
    """
    if (value >> 7):
        return (value ^ 0xFF) + 1
    return value


def inc_no_carry(value: int) -> int:
    """
    Increments the low-byte of an address without carrying to the high byte
    """
    value &= 0xFFFF
    address = (value + 1 & 0xFF) + (value & 0xFF00)
    return address


class CPU:

    bus: Bus
    registers: Registers
    ps: Status
    current_instruction: list
    current_instruction_pc: int
    interrupt_vectors: dict

    def __init__(self, origin: int = 0):
        self.bus = Bus()
        self.registers = Registers()
        self.ps = Status()
        self.registers.program_counter = origin
        self.current_instruction = list()
        self.interrupt_vectors = {
            "BRK": 0xFFFE,
            "RST": 0xFFFC,
            "NMI": 0xFFFA,
            "ABT": 0xFFF8,
            "COP": 0xFFF4,
        }

    def read_v(self) -> int:
        """Read the value located at the current program counter's location and increment the program counter.

        Returns:
            int: the value that the program counter points to
        """
        v = self.bus.read(self.registers.program_counter)
        self.registers.program_counter += 1
        self.current_instruction.append(v)
        return v

    def process_instruction(self) -> int:
        """Process the instruction at the current program counter location

        Returns:
            int: The opcode of the current instruction
        """
        self.current_instruction_pc = self.registers.program_counter
        opcode = self.read_v()
        self.current_instruction = [opcode]
        inst_name = inst_map[opcode]
        getattr(self, f'_i_{inst_name}')(opcode)
        return opcode

    # Stack functions
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

    # Addressing functions
    def _a_x_indexed_zp_indirect(self) -> tuple:
        """Retrieve the address and data using X-Indexed Zero Page Indirect method using the current program counter address.

        Returns:
            tuple: Address referenced and the data at the location.
        """
        offset = self.read_v()
        address = (offset + self.registers.X) & 0xFF
        address = self.bus.read(address) + (self.bus.read(address + 1) << 8)
        address &= 0xFFFF
        return (address, self.bus.read(address))

    def _a_zp_indirect_y_indexed(self) -> list:
        """Retrieve the address and data using Zero Page Indirect Y-Indexed method using the current program counter address.

        Returns:
            tuple: Address referenced and the data at the location.
        """
        offset = self.read_v()
        address = self.bus.read(
            offset) + (self.bus.read(offset + 1) << 8) + self.registers.Y
        address &= 0xFFFF
        return [address, self.bus.read(address)]

    def _a_zero_page(self) -> list:
        """Retrieve the address and data using the Zero Page addressing method using the current program counter address.

        Returns:
            tuple: Address referenced and the data at the location.
        """
        address = self.read_v()
        address &= 0xFF
        return [address, self.bus.read(address)]

    def _a_zero_page_indexed(self, register: str) -> list:
        """Retrieve the address and data using the Zero Page Indexed addressing method using the current program counter address.

        Returns:
            tuple: Address referenced and the data at the location.
        """
        address = self.read_v() + getattr(self.registers, register)
        address &= 0xFF
        return [address, self.bus.read(address)]

    def _a_absolute(self) -> list:
        """Retrieve the address and data using the Absolute addressing method using the current program counter address.

        Returns:
            tuple: Address referenced and the data at the location.
        """
        address = self.read_v() + (self.read_v() << 8)
        address &= 0xFFFF
        return [address, self.bus.read(address)]

    def _a_indirect(self) -> list:
        """Retrieve the address and data using the Indirect addressing method using the current program counter address.

        Returns:
            tuple: Address referenced and the data at the location.
        """
        addr_low, addr_high = self.read_v(), self.read_v()
        address = addr_low + (addr_high << 8)
        address_next = inc_no_carry(address)

        next_address = self.bus.read(
            address) + (self.bus.read(address_next) << 8)
        next_address &= 0xFFFF
        return [next_address, self.bus.read(address)]

    def _a_indexed_absolute(self, register: str) -> list:
        """Retrieve the address and data using the Indexed Absolute addressing method using the current program counter address.

        Returns:
            tuple: Address referenced and the data at the location.
        """
        r = getattr(self.registers, register)
        address = self.read_v() + (self.read_v() << 8) + r
        address &= 0xFFFF
        return [address, self.bus.read(address)]

    def _a_immediate(self) -> list:
        """Retrieve the address and data using the Immediate addressing method using the current program counter address.

        Returns:
            tuple: Address referenced and the data at the location.
        """
        return [None, self.read_v()]

    # 6502 Opcodes/Instructions
    def _i_lda(self, opcode: int):
        """Load the A register/accumulator.

        Args:
            opcode (int): The LDA opcode to process.
        """

        match opcode:
            case 0xA1:
                _, value = self._a_x_indexed_zp_indirect()
            case 0xA5:
                _, value = self._a_zero_page()
            case 0xA9:
                _, value = self._a_immediate()
            case 0xAD:
                _, value = self._a_absolute()
            case 0xB1:
                _, value = self._a_zp_indirect_y_indexed()
            case 0xB5:
                _, value = self._a_zero_page_indexed('X')
            case 0xB9:
                _, value = self._a_indexed_absolute('Y')
            case 0xBD:
                _, value = self._a_indexed_absolute('X')

        self.registers.A = value
        self.ps.flags.zero = not bool(value)
        self.ps.flags.negative = bool(value >> 7)

    def _i_ldx(self, opcode: int):
        """Load the X register.

        Args:
            opcode (int): The LDX opcode to process.
        """

        match opcode:
            case 0xA2:
                _, value = self._a_immediate()
            case 0xAE:
                _, value = self._a_absolute()
            case 0xBE:
                _, value = self._a_indexed_absolute('Y')
            case 0xA6:
                _, value = self._a_zero_page()
            case 0xB6:
                _, value = self._a_zero_page_indexed('Y')

        self.registers.X = value
        self.ps.flags.zero = not bool(value)
        self.ps.flags.negative = bool(value >> 7)

    def _i_ldy(self, opcode: int):
        """Load the Y register.

        Args:
            opcode (int): The LDY opcode to process.
        """

        match opcode:
            case 0xA0:
                _, value = self._a_immediate()
            case 0xAC:
                _, value = self._a_absolute()
            case 0xBC:
                _, value = self._a_indexed_absolute('X')
            case 0xA4:
                _, value = self._a_zero_page()
            case 0xB4:
                _, value = self._a_zero_page_indexed('X')

        self.registers.Y = value
        self.ps.flags.zero = not bool(value)
        self.ps.flags.negative = bool(value >> 7)

    def _i_adc(self, opcode: int):
        """Add a given value with the accumulator including the carry bit.

        Args:
            opcode (int): The ADC opcode to process.
        """

        def add_to_accumulator(value):
            result = value + self.registers.A + self.ps.flags.carry
            self.ps.flags.carry = bool(result > 0xFF)
            result &= 0xFF
            self.ps.flags.overflow = bool(
                (self.registers.A ^ result) & (value ^ result) & 0x80)
            self.ps.flags.negative = bool(result >> 7)
            self.ps.flags.zero = result == 0
            self.registers.A = result

        def add_to_accumulator_sbc(value):
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

        match opcode:
            case 0x61:
                _, v = self._a_x_indexed_zp_indirect()
            case 0x65:
                _, v = self._a_zero_page()
            case 0x69:
                _, v = self._a_immediate()
            case 0x6D:
                _, v = self._a_absolute()
            case 0x71:
                _, v = self._a_zp_indirect_y_indexed()
            case 0x75:
                _, v = self._a_zero_page_indexed('X')
            case 0x79:
                _, v = self._a_indexed_absolute('Y')
            case 0x7D:
                _, v = self._a_indexed_absolute('X')

        if self.ps.flags.decimal:
            add_to_accumulator_sbc(v)
        else:
            add_to_accumulator(v)

    def _i_and(self, opcode: int):
        """Perform bitwise "and" operation between a value and the accumulator.

        Args:
            opcode (int): The AND opcode to process.
        """

        match opcode:
            case 0x21:
                _, value = self._a_x_indexed_zp_indirect()
            case 0x25:
                _, value = self._a_zero_page()
            case 0x29:
                _, value = self._a_immediate()
            case 0x2D:
                _, value = self._a_absolute()
            case 0x31:
                _, value = self._a_zp_indirect_y_indexed()
            case 0x35:
                _, value = self._a_zero_page_indexed('X')
            case 0x39:
                _, value = self._a_indexed_absolute('Y')
            case 0x3D:
                _, value = self._a_indexed_absolute('X')

        self.registers.A &= value
        self.ps.flags.negative = bool(value >> 7)
        self.ps.flags.zero = not bool(value)

    def _i_asl(self, opcode: int):
        """Arithmetically shift left a given value.

        Args:
            opcode (int): The ASL opcode to process.
        """

        def arithmetic_shift_left(value, address: Optional[int] = None):
            self.ps.flags.carry = bool(value >> 7)
            value = (value << 1) & 0xFF
            self.ps.flags.zero = not bool(value)
            self.ps.flags.negative = bool(value >> 7)
            return value

        match opcode:
            case 0x06:
                address, v = self._a_zero_page()
            case 0x0A:
                self.registers.A = arithmetic_shift_left(v)
            case 0x0E:
                address, v = self._a_absolute()
            case 0x16:
                address, v = self._a_zero_page_indexed('X')
            case 0x1E:
                address, v = self._a_indexed_absolute('X')

        if opcode not in [0x0A]:
            self.bus.write(address, arithmetic_shift_left(v))

    def _i_brk(self, opcode: int):
        """Break processor operations.

        Args:
            opcode (int): The BRK opcode to process.
        """
        self.ps.flags.pbreak = True
        self._s_push_address(self.registers.program_counter + 1)
        self._s_push_byte(self.ps.status.value)
        self.ps.flags.interrupt_mask = True
        address = self.interrupt_vectors["BRK"]
        self.registers.program_counter = self.bus.read(
            address) + (self.bus.read(address + 1) << 8)

    def _i_cmp(self, opcode: int):
        """Compare a given value to the accumulator.

        Args:
            opcode (int): The CMP opcode to process.
        """

        match opcode:
            case 0xC9:
                _, v = self._a_immediate()
            case 0xCD:
                _, value = self._a_absolute()
            case 0xDD:
                _, value = self._a_indexed_absolute('X')
            case 0xD9:
                _, value = self._a_indexed_absolute('Y')
            case 0xC5:
                _, value = self._a_zero_page()
            case 0xD5:
                _, value = self._a_zero_page_indexed('X')
            case 0xC1:
                _, value = self._a_x_indexed_zp_indirect()
            case 0xD1:
                _, value = self._a_zp_indirect_y_indexed()

        result = self.registers.A - value
        result = result if result >= 0 else result + 0x100
        self.ps.flags.zero = (self.registers.A == value)
        self.ps.flags.negative = bool(result >> 7)
        self.ps.flags.carry = (value <= self.registers.A)

    def _i_branch(self, opcode: int):
        """Perform a branching instruction based on the opcode provided.

        Args:
            opcode (int): The branching instruction opcode to process.
        """

        v = self.read_v()
        v = convert_int(v)

        match opcode:
            case 0x90:
                if not self.ps.flags.carry:
                    self.registers.program_counter += v
            case 0xB0:
                if self.ps.flags.carry:
                    self.registers.program_counter += v
            case 0xF0:
                if self.ps.flags.zero:
                    self.registers.program_counter += v
            case 0x30:
                if self.ps.flags.negative:
                    self.registers.program_counter += v
            case 0xD0:
                if not self.ps.flags.zero:
                    self.registers.program_counter += v
            case 0x10:
                if not self.ps.flags.negative:
                    self.registers.program_counter += v
            case 0x50:
                if not self.ps.flags.overflow:
                    self.registers.program_counter += v
            case 0x70:
                if self.ps.flags.overflow:
                    self.registers.program_counter += v

    def _i_sta(self, opcode: int):
        """Store value in the accumulator.

        Args:
            opcode (int): The STA opcode to process.
        """

        match opcode:
            case 0x8D:
                address, _ = self._a_absolute()
            case 0x9D:
                address, _ = self._a_indexed_absolute('X')
            case 0x99:
                address, _ = self._a_indexed_absolute('Y')
            case 0x85:
                address, _ = self._a_zero_page()
            case 0x95:
                address, _ = self._a_zero_page_indexed('X')
            case 0x81:
                address, _ = self._a_x_indexed_zp_indirect()
            case 0x91:
                address, _ = self._a_zp_indirect_y_indexed()

        self.bus.write(address, self.registers.A)

    def _i_inx(self, opcode: int):
        """Increment the X register.

        Args:
            opcode (int): The INX opcode to process.
        """
        self.registers.X += 1
        self.ps.flags.negative = bool(self.registers.X >> 7)
        self.ps.flags.zero = not bool(self.registers.X)

    def _i_iny(self, opcode: int):
        """Increment the Y register.

        Args:
            opcode (int): The INY opcode to process.
        """
        self.registers.Y += 1
        self.ps.flags.negative = bool(self.registers.Y >> 7)
        self.ps.flags.zero = not bool(self.registers.Y)

    def _i_inc(self, opcode: int):
        """Increment a value in memory.

        Args:
            opcode (int): The INC opcode to process.
        """

        match opcode:
            case 0xEE:
                address, value = self._a_absolute()
            case 0xFE:
                address, value = self._a_indexed_absolute('X')
            case 0xE6:
                address, value = self._a_zero_page()
            case 0xF6:
                address, value = self._a_zero_page_indexed('X')

        value = value + 1 & 0xFF
        self.bus.write(address, value)
        self.ps.flags.negative = bool(value >> 7)
        self.ps.flags.zero = not bool(value)

    def _i_dex(self, opcode: int):
        """Decrement the X register.

        Args:
            opcode (int): The DEX opcode to process.
        """
        self.registers.X -= 1
        self.ps.flags.negative = bool(self.registers.X >> 7)
        self.ps.flags.zero = not bool(self.registers.X)

    def _i_dey(self, opcode: int):
        """Decrement the Y register.

        Args:
            opcode (int): The DEY opcode to process.
        """
        self.registers.Y -= 1
        self.ps.flags.negative = bool(self.registers.Y >> 7)
        self.ps.flags.zero = not bool(self.registers.Y)

    def _i_dec(self, opcode: int):
        """Decrement a value in memory.

        Args:
            opcode (int): The DEC opcode to process.
        """

        match opcode:
            case 0xCE:
                address, value = self._a_absolute()
            case 0xDE:
                address, value = self._a_indexed_absolute('X')
            case 0xC6:
                address, value = self._a_zero_page()
            case 0xD6:
                address, value = self._a_zero_page_indexed('X')

        value = value - 1 & 0xFF
        self.bus.write(address, value)
        self.ps.flags.negative = bool(value >> 7)
        self.ps.flags.zero = not bool(value)

    def _i_jmp(self, opcode: int):
        """Jump to another part of the program.

        Args:
            opcode (int): The JMP opcode to process.
        """

        match opcode:
            case 0x4C:
                address, _ = self._a_absolute()
            case 0x6C:
                address, _ = self._a_indirect()

        self.registers.program_counter = address

    def _i_sed(self, opcode: int):
        """Set the decimal flag on the processor.

        Args:
            opcode (int): The SED opcode to process.
        """
        self.ps.flags.decimal = True

    def _i_cld(self, opcode: int):
        """Clear the decimal flag on the processor.

        Args:
            opcode (int): The CLD opcode to process.
        """
        self.ps.flags.decimal = False

    def _i_clc(self, opcode: int):
        """Clear the carry flag on the processor.

        Args:
            opcode (int): The CLC opcode to process.
        """
        self.ps.flags.carry = False

    def _i_cli(self, opcode: int):
        """Clear the interrupt mask flag on the processor.

        Args:
            opcode (int): The CLI opcode to process.
        """
        self.ps.flags.interrupt_mask = False

    def _i_clv(self, opcode: int):
        """Clear the overflow flag on the processor.

        Args:
            opcode (int): The CLV opcode to process.
        """
        self.ps.flags.overflow = False

    def _i_bit(self, opcode: int):
        """Test bits in memory.

        Args:
            opcode (int): The BIT opcode to process.
        """

        match opcode:
            case 0x2C:
                _, value = self._a_absolute()
            case 0x24:
                _, value = self._a_zero_page()

        v = self.registers.A & value
        self.ps.flags.negative = bool(value >> 7)
        self.ps.flags.overflow = bool((value >> 6) & 1)
        self.ps.flags.zero = not bool(v)

    def _i_cpx(self, opcode: int):
        """Compare the X register with memory.

        Args:
            opcode (int): The CPX opcode to process.
        """

        match opcode:
            case 0xE0:
                _, v = self._a_immediate()
            case 0xEC:
                _, v = self._a_absolute()
            case 0xE4:
                _, v = self._a_zero_page()

        value = (self.registers.X - v) & 0xFF
        self.ps.flags.negative = (value >> 7)
        self.ps.flags.carry = self.registers.X >= v
        self.ps.flags.zero = not bool(value)

    def _i_cpy(self, opcode: int):
        """Compare the Y register with memory.

        Args:
            opcode (int): The CPY opcode to process.
        """

        match opcode:
            case 0xC0:
                _, v = self._a_immediate()
            case 0xCC:
                _, v = self._a_absolute()
            case 0xC4:
                _, v = self._a_zero_page()

        value = (self.registers.Y - v) & 0xFF
        self.ps.flags.negative = (value >> 7)
        self.ps.flags.carry = self.registers.Y >= v
        self.ps.flags.zero = not bool(value)

    def _i_eor(self, opcode: int):
        """Exlusive OR the accumulator with memory.

        Args:
            opcode (int): The EOR opcode to process.
        """

        match opcode:
            case 0x49:
                _, v = self._a_immediate()
            case 0x4D:
                _, v = self._a_absolute()
            case 0x5D:
                _, v = self._a_indexed_absolute('X')
            case 0x59:
                _, v = self._a_indexed_absolute('Y')
            case 0x45:
                _, v = self._a_zero_page()
            case 0x55:
                _, v = self._a_zero_page_indexed('X')
            case 0x41:
                _, v = self._a_x_indexed_zp_indirect()
            case 0x51:
                _, v = self._a_zp_indirect_y_indexed()

        self.registers.A ^= v
        self.ps.flags.negative = bool(self.registers.A >> 7)
        self.ps.flags.zero = not bool(self.registers.A)

    def _i_lsr(self, opcode):

        match opcode:
            case 0x4A:
                v = self.register.A
            case 0x4E:
                address, v = self._a_absolute()
            case 0x5E:
                address, v = self._a_indexed_absolute('X')
            case 0x46:
                address, v = self._a_zero_page()
            case 0x56:
                address, v = self._a_zero_page_indexed('X')

        self.registers.carry = v & 1
        v >>= 1
        self.ps.flags.negative = False
        self.ps.flags.zero = not bool(v)

        if opcode == 0x4A:
            self.registers.A = v
        else:
            self.bus.write(address, v)

    def _i_nop(self, opcode):
        pass

    def _i_ora(self, opcode):

        match opcode:
            case 0x09:
                address, v = self._a_immediate()
            case 0x05:
                address, v = self._a_zero_page()
            case 0x15:
                address, v = self._a_zero_page_indexed('X')
            case 0x0D:
                address, v = self._a_absolute()
            case 0x1D:
                address, v = self._a_indexed_absolute('X')
            case 0x19:
                address, v = self._a_indexed_absolute('Y')
            case 0x01:
                address, v = self._a_x_indexed_zp_indirect()
            case 0x11:
                address, v = self._a_zp_indirect_y_indexed()

        self.registers.A |= v
        self.ps.flags.zero = not bool(self.registers.A)
        self.ps.flags.negative = bool(self.registers.A >> 7)

    def _i_jsr(self, opcode):
        address, _ = self._a_absolute()
        self._s_push_address(self.registers.program_counter)
        self.registers.program_counter = address

    def _i_pha(self, opcode):
        self._s_push_byte(self.registers.A)

    def _i_php(self, opcode):
        self._s_push_byte(self.ps.status.value)

    def _i_pla(self, opcode):
        self.registers.A = self._s_pop_byte()
        self.ps.flags.zero = not bool(self.registers.A)
        self.ps.flags.negative = (self.registers.A >> 7)

    def _i_plp(self, opcode):
        self.ps.status.value = self._s_pop_byte()

    def _i_rol(self, opcode):

        match opcode:
            case 0x2A:
                v = self.registers.A
            case 0x2E:
                address, v = self._a_absolute()
            case 0x3E:
                address, v = self._a_indexed_absolute('X')
            case 0x26:
                address, v = self._a_zero_page()
            case 0x36:
                address, v = self._a_zero_page_indexed('X')

        result = ((v << 1) & 0xFF) + self.ps.flags.carry
        self.ps.flags.carry = v >> 7
        self.ps.flags.negative = result >> 7
        self.ps.flags.zero = not bool(result)

        if opcode == 0x2A:
            self.registers.A = result
        else:
            self.bus.write(address, result)

    def _i_ror(self, opcode):

        match opcode:
            case 0x6A:
                v = self.registers.A
            case 0x6E:
                address, v = self._a_absolute()
            case 0x7E:
                address, v = self._a_indexed_absolute('X')
            case 0x66:
                address, v = self._a_zero_page()
            case 0x76:
                address, v = self._a_zero_page_indexed('X')

        result = ((v >> 1)) + (self.ps.flags.carry << 7)
        self.ps.flags.carry = v & 1
        self.ps.flags.negative = result >> 7
        self.ps.flags.zero = not bool(result)

        if opcode == 0x6A:
            self.registers.A = result
        else:
            self.bus.write(address, result)

    def _i_rti(self, opcode):
        self.ps.status.value = self._s_pop_byte()
        self.registers.program_counter = self._s_pop_address()

    def _i_rts(self, opcode):
        self.registers.program_counter = self._s_pop_address() + 1

    def _i_sec(self, opcode):
        self.ps.flags.carry = True

    def _i_sbc(self, opcode):

        def subtract_binary(v):
            a = self.registers.A
            c = self.ps.flags.carry
            result = a + (v ^ 0xFF) + c
            self.ps.flags.carry = result != (result & 0xFF)
            result &= 0xFF
            self.ps.flags.overflow = bool(
                (a ^ result) & ((v ^ 0xFF) ^ result) & 0x80)
            self.ps.flags.zero = not bool(result)
            self.ps.flags.negative = bool(result & (1 << 7))
            self.registers.A = result

        def subtract_decimal(v):
            # After days of frustration, this is slightly altered code from mnaberez's py65
            # project...and I greatly appreciate that it works as does my sanity...
            a = self.registers.A

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

        match opcode:
            case 0xE9:
                _, v = self._a_immediate()
            case 0xED:
                _, v = self._a_absolute()
            case 0xFD:
                _, v = self._a_indexed_absolute('X')
            case 0xF9:
                _, v = self._a_indexed_absolute('Y')
            case 0xE5:
                _, v = self._a_zero_page()
            case 0xF5:
                _, v = self._a_zero_page_indexed('X')
            case 0xE1:
                _, v = self._a_x_indexed_zp_indirect()
            case 0xF1:
                _, v = self._a_zp_indirect_y_indexed()

        if self.ps.flags.decimal:
            subtract_decimal(v)
        else:
            subtract_binary(v)

    def _i_sei(self, opcode):
        self.ps.flags.interrupt_mask = True

    def _i_stx(self, opcode):

        match opcode:
            case 0x8E:
                address, _ = self._a_absolute()
            case 0x86:
                address, _ = self._a_zero_page()
            case 0x96:
                address, _ = self._a_zero_page_indexed('Y')

        self.bus.write(address, self.registers.X)

    def _i_sty(self, opcode):

        match opcode:
            case 0x8C:
                address, _ = self._a_absolute()
            case 0x84:
                address, _ = self._a_zero_page()
            case 0x94:
                address, _ = self._a_zero_page_indexed('X')

        self.bus.write(address, self.registers.Y)

    def _i_tax(self, opcode):
        self.registers.X = self.registers.A
        self.ps.flags.negative = bool(self.registers.X >> 7)
        self.ps.flags.zero = not bool(self.registers.X)

    def _i_tay(self, opcode):
        self.registers.Y = self.registers.A
        self.ps.flags.negative = bool(self.registers.Y >> 7)
        self.ps.flags.zero = not bool(self.registers.Y)

    def _i_tsx(self, opcode):
        self.registers.X = self.registers.stack_pointer
        self.ps.flags.negative = bool(self.registers.X >> 7)
        self.ps.flags.zero = not bool(self.registers.X)

    def _i_txa(self, opcode):
        self.registers.A = self.registers.X
        self.ps.flags.negative = bool(self.registers.A >> 7)
        self.ps.flags.zero = not bool(self.registers.A)

    def _i_txs(self, opcode):
        self.registers.stack_pointer = self.registers.X

    def _i_tya(self, opcode):
        self.registers.A = self.registers.Y
        self.ps.flags.negative = bool(self.registers.A >> 7)
        self.ps.flags.zero = not bool(self.registers.A)
