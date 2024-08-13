from typing import Tuple, Union, Optional

from mos6502.bus import Bus
from mos6502.cpu_mixins import AddressingMixin, MathMixin, StackMixin
from mos6502.instructions import generate_inst_map
from mos6502.periphery import Registers, Status


def convert_int(value: int) -> int:
    """
    Convert unsigned int into a properly signed int.
    """
    if (value >> 7):
        return (value ^ 0xFF) + 1
    return value


class CPU(MathMixin, AddressingMixin, StackMixin):
    """The core of the 6502 8-bit processor.

    Args:
        origin (int): the address the CPU will start reading code from.
        use_illegal (bool): allow use of 'illegal' opcodes for the 6502.
    """

    bus: Bus
    registers: Registers
    ps: Status
    current_instruction: list
    current_instruction_pc: int
    interrupt_vectors: dict

    def __init__(self, origin: int = 0, use_illegal: bool = False):
        self.instruction_map = generate_inst_map(include_illegal=use_illegal)
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

    def run_program(self, halt_on: Optional[int] = None) -> None:
        """Execute the program and stop execution if the opcode 'halt_on' is specified.

        Args:
            halt_on (int, optional): The opcode to halt on. Defaults to None.
        """
        while True:
            self.process_instruction()
            if self.bus.read(self.registers.program_counter) == halt_on:
                break

    def read_value(self) -> int:
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
        opcode = self.read_value()
        self.current_instruction = [opcode]
        inst_name = self.instruction_map[opcode]
        getattr(self, f'_i_{inst_name}')(opcode)
        return opcode

    # 6502 Opcodes/Instructions
    def _i_lda(self, opcode: int):
        """Load the A register/accumulator with a value from memory.

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
        """Load the X register with a value from memory.

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
        """Load the Y register with a value from memory.

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

        match opcode:
            case 0x61:
                _, value = self._a_x_indexed_zp_indirect()
            case 0x65:
                _, value = self._a_zero_page()
            case 0x69:
                _, value = self._a_immediate()
            case 0x6D:
                _, value = self._a_absolute()
            case 0x71:
                _, value = self._a_zp_indirect_y_indexed()
            case 0x75:
                _, value = self._a_zero_page_indexed('X')
            case 0x79:
                _, value = self._a_indexed_absolute('Y')
            case 0x7D:
                _, value = self._a_indexed_absolute('X')

        self.add_to_accumulator(value)

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
        self.ps.flags.negative = bool(self.registers.A >> 7)
        self.ps.flags.zero = not bool(self.registers.A)

    def _i_asl(self, opcode: int):
        """Arithmetically shift left a given value.

        Args:
            opcode (int): The ASL opcode to process.
        """

        def arithmetic_shift_left(value):
            self.ps.flags.carry = bool(value >> 7)
            value = (value << 1) & 0xFF
            self.ps.flags.zero = not bool(value)
            self.ps.flags.negative = bool(value >> 7)
            return value

        match opcode:
            case 0x06:
                address, value = self._a_zero_page()
            case 0x0A:
                self.registers.A = arithmetic_shift_left(self.registers.A)
            case 0x0E:
                address, value = self._a_absolute()
            case 0x16:
                address, value = self._a_zero_page_indexed('X')
            case 0x1E:
                address, value = self._a_indexed_absolute('X')

        if opcode not in [0x0A]:
            self.bus.write(address, arithmetic_shift_left(value))

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
                _, value = self._a_immediate()
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

        result = (self.registers.A - value) & 0xFF
        self.ps.flags.zero = (self.registers.A == value)
        self.ps.flags.negative = bool(result >> 7)
        self.ps.flags.carry = (value <= self.registers.A)

    def _i_branch(self, opcode: int):
        """Perform a branching instruction based on the opcode provided.

        Args:
            opcode (int): The branching instruction opcode to process.
        """

        value = self.read_value()
        value = convert_int(value)

        match opcode:
            case 0x90:
                if not self.ps.flags.carry:
                    self.registers.program_counter += value
            case 0xB0:
                if self.ps.flags.carry:
                    self.registers.program_counter += value
            case 0xF0:
                if self.ps.flags.zero:
                    self.registers.program_counter += value
            case 0x30:
                if self.ps.flags.negative:
                    self.registers.program_counter += value
            case 0xD0:
                if not self.ps.flags.zero:
                    self.registers.program_counter += value
            case 0x10:
                if not self.ps.flags.negative:
                    self.registers.program_counter += value
            case 0x50:
                if not self.ps.flags.overflow:
                    self.registers.program_counter += value
            case 0x70:
                if self.ps.flags.overflow:
                    self.registers.program_counter += value

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
                _, value = self._a_immediate()
            case 0xEC:
                _, value = self._a_absolute()
            case 0xE4:
                _, value = self._a_zero_page()

        result = (self.registers.X - value) & 0xFF
        self.ps.flags.negative = (result >> 7)
        self.ps.flags.carry = self.registers.X >= value
        self.ps.flags.zero = not bool(result)

    def _i_cpy(self, opcode: int):
        """Compare the Y register with memory.

        Args:
            opcode (int): The CPY opcode to process.
        """

        match opcode:
            case 0xC0:
                _, value = self._a_immediate()
            case 0xCC:
                _, value = self._a_absolute()
            case 0xC4:
                _, value = self._a_zero_page()

        result = (self.registers.Y - value) & 0xFF
        self.ps.flags.negative = (result >> 7)
        self.ps.flags.carry = self.registers.Y >= value
        self.ps.flags.zero = not bool(result)

    def _i_eor(self, opcode: int):
        """Exlusive OR the accumulator with memory.

        Args:
            opcode (int): The EOR opcode to process.
        """

        match opcode:
            case 0x49:
                _, value = self._a_immediate()
            case 0x4D:
                _, value = self._a_absolute()
            case 0x5D:
                _, value = self._a_indexed_absolute('X')
            case 0x59:
                _, value = self._a_indexed_absolute('Y')
            case 0x45:
                _, value = self._a_zero_page()
            case 0x55:
                _, value = self._a_zero_page_indexed('X')
            case 0x41:
                _, value = self._a_x_indexed_zp_indirect()
            case 0x51:
                _, value = self._a_zp_indirect_y_indexed()

        self.registers.A ^= value
        self.ps.flags.negative = bool(self.registers.A >> 7)
        self.ps.flags.zero = not bool(self.registers.A)

    def _i_lsr(self, opcode: int):
        """Logical shift right the accumulator or a value in memory.

        Args:
            opcode (int): The LSR opcode to process.
        """

        match opcode:
            case 0x4A:
                value = self.registers.A
            case 0x4E:
                address, value = self._a_absolute()
            case 0x5E:
                address, value = self._a_indexed_absolute('X')
            case 0x46:
                address, value = self._a_zero_page()
            case 0x56:
                address, value = self._a_zero_page_indexed('X')

        self.ps.flags.carry = value & 1
        value >>= 1
        self.ps.flags.negative = False
        self.ps.flags.zero = not bool(value)

        if opcode == 0x4A:
            self.registers.A = value
        else:
            self.bus.write(address, value)

    def _i_nop(self, opcode: int):
        """Don't do anything (no operation)

        Args:
            opcode (int): The NOP opcode to not process.
        """
        match opcode:
            case 0x80 | 0x82 | 0x89 | 0xC2 | 0xE2:
                self._a_immediate()
            case 0x04 | 0x44 | 0x64:
                self._a_zero_page()
            case 0x14 | 0x34 | 0x54 | 0x74 | 0xD4 | 0xF4:
                self._a_zero_page_indexed('X')
            case 0x0C:
                self._a_absolute()
            case 0x1C | 0x3C | 0x5C | 0x7C | 0xDC | 0xFC:
                self._a_indexed_absolute('X')

    def _i_ora(self, opcode: int):
        """Bitwise OR a value and the contents of the accumulator.

        Args:
            opcode (int): The ORA opcode to process.
        """

        match opcode:
            case 0x09:
                _, value = self._a_immediate()
            case 0x05:
                _, value = self._a_zero_page()
            case 0x15:
                _, value = self._a_zero_page_indexed('X')
            case 0x0D:
                _, value = self._a_absolute()
            case 0x1D:
                _, value = self._a_indexed_absolute('X')
            case 0x19:
                _, value = self._a_indexed_absolute('Y')
            case 0x01:
                _, value = self._a_x_indexed_zp_indirect()
            case 0x11:
                _, value = self._a_zp_indirect_y_indexed()

        self.registers.A |= value
        self.ps.flags.zero = not bool(self.registers.A)
        self.ps.flags.negative = bool(self.registers.A >> 7)

    def _i_jsr(self, opcode: int):
        """Jump to subroutine.

        Args:
            opcode (int): The JSR opcode to process.
        """
        address, _ = self._a_absolute()
        self._s_push_address(self.registers.program_counter)
        self.registers.program_counter = address

    def _i_pha(self, opcode: int):
        """Push the accumulator contents onto the stack.

        Args:
            opcode (int): The PHA opcode to process.
        """
        self._s_push_byte(self.registers.A)

    def _i_php(self, opcode: int):
        """Push the processor status onto the stack.  Bits 4 and 5 are set to `1` when pushed.

        Args:
            opcode (int): The PHP opcode to process.
        """
        self._s_push_byte(self.ps.status.value | 0x30)

    def _i_pla(self, opcode: int):
        """Pull the accumulator contents off of the stack.

        Args:
            opcode (int): The PLA opcode to process.
        """
        self.registers.A = self._s_pop_byte()
        self.ps.flags.zero = not bool(self.registers.A)
        self.ps.flags.negative = (self.registers.A >> 7)

    def _i_plp(self, opcode: int):
        """Pull the processor status off of the stack.  Bits 4 and 5 are ignored when pulled from the stack.

        Args:
            opcode (int): The PLP opcode to process.
        """
        self.ps.status.value = self._s_pop_byte() & ~(0x30)

    def _i_rol(self, opcode: int):
        """Rotate the contents of the accumulator or memory value to the left.

        Args:
            opcode (int): The ROL opcode to process.
        """

        match opcode:
            case 0x2A:
                value = self.registers.A
            case 0x2E:
                address, value = self._a_absolute()
            case 0x3E:
                address, value = self._a_indexed_absolute('X')
            case 0x26:
                address, value = self._a_zero_page()
            case 0x36:
                address, value = self._a_zero_page_indexed('X')

        result = ((value << 1) & 0xFF) + self.ps.flags.carry
        self.ps.flags.carry = value >> 7
        self.ps.flags.negative = result >> 7
        self.ps.flags.zero = not bool(result)

        if opcode == 0x2A:
            self.registers.A = result
        else:
            self.bus.write(address, result)

    def _i_ror(self, opcode: int):
        """Rotate the contents of the accumulator or memory value to the right.

        Args:
            opcode (int): The ROR opcode to process.
        """

        match opcode:
            case 0x6A:
                value = self.registers.A
            case 0x6E:
                address, value = self._a_absolute()
            case 0x7E:
                address, value = self._a_indexed_absolute('X')
            case 0x66:
                address, value = self._a_zero_page()
            case 0x76:
                address, value = self._a_zero_page_indexed('X')

        result = ((value >> 1)) + (self.ps.flags.carry << 7)
        self.ps.flags.carry = value & 1
        self.ps.flags.negative = result >> 7
        self.ps.flags.zero = not bool(result)

        if opcode == 0x6A:
            self.registers.A = result
        else:
            self.bus.write(address, result)

    def _i_rti(self, opcode: int):
        """Return from interrupt.

        Args:
            opcode (int): The RTI opcode to process.
        """
        self.ps.status.value = self._s_pop_byte()
        self.registers.program_counter = self._s_pop_address()

    def _i_rts(self, opcode: int):
        """Return from subroutine.

        Args:
            opcode (int): The RTS opcode to process.
        """
        self.registers.program_counter = self._s_pop_address() + 1

    def _i_sec(self, opcode: int):
        """Set the carry flag on the processor.

        Args:
            opcode (int): The SEC opcode to process.
        """
        self.ps.flags.carry = True

    def _i_sbc(self, opcode: int):
        """Subtract value from the accumulator with borrow.

        Args:
            opcode (int): The SBC opcode to process.
        """
        match opcode:
            case 0xE9:
                _, value = self._a_immediate()
            case 0xED:
                _, value = self._a_absolute()
            case 0xFD:
                _, value = self._a_indexed_absolute('X')
            case 0xF9:
                _, value = self._a_indexed_absolute('Y')
            case 0xE5:
                _, value = self._a_zero_page()
            case 0xF5:
                _, value = self._a_zero_page_indexed('X')
            case 0xE1:
                _, value = self._a_x_indexed_zp_indirect()
            case 0xF1:
                _, value = self._a_zp_indirect_y_indexed()

        self.subtract_from_accumulator(value)

    def _i_sei(self, opcode: int):
        """Set the interrupt mask flag on the CPU.

        Args:
            opcode (int): The SEI opcode to process.
        """
        self.ps.flags.interrupt_mask = True

    def _i_stx(self, opcode: int):
        """Store value into the X register.

        Args:
            opcode (int): The STX opcode to process.
        """

        match opcode:
            case 0x8E:
                address, _ = self._a_absolute()
            case 0x86:
                address, _ = self._a_zero_page()
            case 0x96:
                address, _ = self._a_zero_page_indexed('Y')

        self.bus.write(address, self.registers.X)

    def _i_sty(self, opcode: int):
        """Store value into the Y register.

        Args:
            opcode (int): The STY opcode to process.
        """

        match opcode:
            case 0x8C:
                address, _ = self._a_absolute()
            case 0x84:
                address, _ = self._a_zero_page()
            case 0x94:
                address, _ = self._a_zero_page_indexed('X')

        self.bus.write(address, self.registers.Y)

    def _i_tax(self, opcode: int):
        """Transfer the contents of the accumulator into the X register.

        Args:
            opcode (int): The TAX opcode to process.
        """
        self.registers.X = self.registers.A
        self.ps.flags.negative = bool(self.registers.X >> 7)
        self.ps.flags.zero = not bool(self.registers.X)

    def _i_tay(self, opcode: int):
        """Transfer the contents of the accumulator into the Y register.

        Args:
            opcode (int): The TAY opcode to process.
        """
        self.registers.Y = self.registers.A
        self.ps.flags.negative = bool(self.registers.Y >> 7)
        self.ps.flags.zero = not bool(self.registers.Y)

    def _i_tsx(self, opcode: int):
        """Transfer the stack pointer value into the X register.

        Args:
            opcode (int): The TSX opcode to process.
        """
        self.registers.X = self.registers.stack_pointer
        self.ps.flags.negative = bool(self.registers.X >> 7)
        self.ps.flags.zero = not bool(self.registers.X)

    def _i_txa(self, opcode: int):
        """Transfer the contents of the X register into the accumulator.

        Args:
            opcode (int): The TXA opcode to process.
        """
        self.registers.A = self.registers.X
        self.ps.flags.negative = bool(self.registers.A >> 7)
        self.ps.flags.zero = not bool(self.registers.A)

    def _i_txs(self, opcode: int):
        """Transfer the contents of the X register into the stack pointer value.

        Args:
            opcode (int): The TXS opcode to process.
        """
        self.registers.stack_pointer = self.registers.X

    def _i_tya(self, opcode: int):
        """Transfer the contents of the accumulator into the Y register.

        Args:
            opcode (int): The TYA opcode to process.
        """
        self.registers.A = self.registers.Y
        self.ps.flags.negative = bool(self.registers.A >> 7)
        self.ps.flags.zero = not bool(self.registers.A)

    # Illegal opcodes that don't already have definitions
    def _i_slo(self, opcode: int) -> None:
        """Shift left one bit in memory, then OR accumulator with memory. (ASL + ORA)

        Args:
            opcodes (int): The SLO opcode to process
        """
        match opcode:
            case 0x07:
                _, value = self._a_zero_page()
            case 0x17:
                _, value = self._a_zero_page_indexed('X')
            case 0x0F:
                _, value = self._a_absolute()
            case 0x1F:
                _, value = self._a_indexed_absolute('X')
            case 0x1B:
                _, value = self._a_indexed_absolute('Y')
            case 0x03:
                _, value = self._a_x_indexed_zp_indirect()
            case 0x13:
                _, value = self._a_zp_indirect_y_indexed()

        self.ps.flags.carry = (value >> 7)
        value = (value << 1) | self.registers.A
        self.ps.flags.negative = bool(value >> 7)
        self.ps.flags.zero = not bool(value)
        self.registers.A = value

    def _i_rla(self, opcode: int) -> None:
        """Rotate left one bit in memory, then AND accumulator with memory. (ROL + AND)

        Args:
            opcode (int): The RLA opcode to process.
        """
        match opcode:
            case 0x27:
                _, value = self._a_zero_page()
            case 0x37:
                _, value = self._a_zero_page_indexed('X')
            case 0x2F:
                _, value = self._a_absolute()
            case 0x3F:
                _, value = self._a_indexed_absolute('X')
            case 0x3B:
                _, value = self._a_indexed_absolute('Y')
            case 0x23:
                _, value = self._a_x_indexed_zp_indirect()
            case 0x33:
                _, value = self._a_zp_indirect_y_indexed()

        carry = self.ps.flags.carry
        self.ps.flags.carry = (value >> 7)
        value = ((value << 1) + carry) & self.registers.A
        value &= 0xFF
        self.ps.flags.negative = bool(value >> 7)
        self.ps.flags.zero = not bool(value)
        self.registers.A = value

    def _i_sre(self, opcode: int) -> None:
        """Shift right one bit in memory, then XOR accumulator with memory. (ASR + EOR)

        Args:
            opcode (int): The SRE opcode to process.
        """
        match opcode:
            case 0x47:
                _, value = self._a_zero_page()
            case 0x57:
                _, value = self._a_zero_page_indexed('X')
            case 0x4F:
                _, value = self._a_absolute()
            case 0x5F:
                _, value = self._a_indexed_absolute('X')
            case 0x5B:
                _, value = self._a_indexed_absolute('Y')
            case 0x43:
                _, value = self._a_x_indexed_zp_indirect()
            case 0x53:
                _, value = self._a_zp_indirect_y_indexed()

        self.ps.flags.carry = (value & 1)
        value = (value >> 1) ^ self.registers.A
        self.ps.flags.negative = bool(value >> 7)
        self.ps.flags.zero = not bool(value)
        self.registers.A = value

    def _i_rra(self, opcode: int) -> None:
        """Rotate memory one bit to the right, then add memory to the accumulator. (ROR + ADC)

        Args:
            opcode (int): The RRA opcode to process.
        """
        match opcode:
            case 0x67:
                _, value = self._a_zero_page()
            case 0x77:
                _, value = self._a_zero_page_indexed('X')
            case 0x6F:
                _, value = self._a_absolute()
            case 0x7F:
                _, value = self._a_indexed_absolute('X')
            case 0x7B:
                _, value = self._a_indexed_absolute('Y')
            case 0x63:
                _, value = self._a_x_indexed_zp_indirect()
            case 0x73:
                _, value = self._a_zp_indirect_y_indexed()

        carry = self.ps.flags.carry
        self.ps.flags.carry = (value & 1)
        value = (value >> 1) & (carry << 7)
        self.subtract_from_accumulator(value)

    def _i_sax(self, opcode: int) -> None:
        """AND the contents of the accumulator and X register, then store the result in memory. (STA + STX)

        Args:
            opcode (int): The SAX opcode to process.
        """
        match opcode:
            case 0x87:
                address, _ = self._a_zero_page()
            case 0x8F:
                address, _ = self._a_absolute()
            case 0x83:
                address, _ = self._a_x_indexed_zp_indirect()
            case 0x97:
                address, _ = self._a_zero_page_indexed('Y')

        value = self.registers.A & self.registers.X
        self.bus.write(address, value)

    def _i_lax(self, opcode: int) -> None:
        """Load the accumulator and X register with a value from memory. (LDA + LDX)

        Args:
            opcode (int): The LAX opcode to process.
        """
        match opcode:
            case 0xA7:
                _, value = self._a_zero_page()
            case 0xAF:
                _, value = self._a_absolute()
            case 0xBF:
                _, value = self._a_indexed_absolute('Y')
            case 0xA3:
                _, value = self._a_x_indexed_zp_indirect()
            case 0xB3:
                _, value = self._a_zp_indirect_y_indexed()
            case 0xB7:
                _, value = self._a_zero_page_indexed('Y')

        self.registers.A = value
        self.registers.X = value
        self.ps.flags.negative = bool(value >> 7)
        self.ps.flags.zero = not bool(value)

    def _i_dcp(self, opcode: int) -> None:
        """Decrement the value of a location in memory, then compare with the accumulator. (DEC + CMP)

        Args:
            opcode (int): The DCP opcode to process.
        """
        match opcode:
            case 0xC7:
                address, value = self._a_zero_page()
            case 0xD7:
                address, value = self._a_zero_page_indexed('X')
            case 0xCF:
                address, value = self._a_absolute()
            case 0xDF:
                address, value = self._a_indexed_absolute('X')
            case 0xDB:
                address, value = self._a_indexed_absolute('Y')
            case 0xC3:
                address, value = self._a_x_indexed_zp_indirect()
            case 0xD3:
                address, value = self._a_zp_indirect_y_indexed()

        value = (value - 1) & 0xFF
        self.bus.write(address, value)
        result = self.registers.A - value
        result = result if result >= 0 else result + 0x100
        self.ps.flags.zero = (self.registers.A == value)
        self.ps.flags.negative = bool(result >> 7)
        self.ps.flags.carry = (value <= self.registers.A)

    def _i_isb(self, opcode: int) -> None:
        """Increase the value in memory by one, then subtract the result from the accumulator. (INC + SBC)

        Args:
            opcode (int): The ISB opcode to process.
        """
        match opcode:
            case 0xE7:
                address, value = self._a_zero_page()
            case 0xF7:
                address, value = self._a_zero_page_indexed('X')
            case 0xEF:
                address, value = self._a_absolute()
            case 0xFF:
                address, value = self._a_indexed_absolute('X')
            case 0xFB:
                address, value = self._a_indexed_absolute('Y')
            case 0xE3:
                address, value = self._a_x_indexed_zp_indirect()
            case 0xF3:
                address, value = self._a_zp_indirect_y_indexed()

        value = (value + 1) & 0xFF
        self.bus.write(address, value)
        self.subtract_from_accumulator(value)

    def _i_anc(self, opcode: int) -> None:
        """ANDs the contents of the accumulator with an immediate value, then moves bit 7 of the accumulator into the carry flag. (AND + ASL/ROL)

        Args:
            opcode (int): The ANC opcode to process.
        """
        _, value = self._a_immediate()
        self.registers.A &= value
        self.ps.flags.carry = bool(self.registers.A >> 7)

    def _i_asr(self, opcode: int) -> None:
        """AND the contents of the accumulator with an immediate value, then right shift the results. (AND + LSR)

        Args:
            opcode (int): The ASR opcode to process.
        """
        _, value = self._a_immediate()
        self.registers.A &= value
        self.ps.flags.carry = (self.registers.A & 1)
        self.registers.A >>= 1
        self.ps.flags.negative = 0
        self.ps.flags.zero = bool(self.registers.A)

    def _i_arr(self, opcode: int) -> None:
        """AND the accumulator with an immediate value and then rotate the content right. (AND + ROR)

        Args:
            opcode (int): The ARR opcode to process.
        """
        _, value = self._a_immediate()
        self.ps.flags.accumulator &= value

        # Get overflow setting post-AND
        a = self.registers.A
        status = self.ps.status.value
        self.add_to_accumulator(value)
        overflow = self.ps.flags.overflow
        self.ps.status.value = status
        self.registers.A = a
        self.ps.flags.overflow = overflow

        carry = self.ps.flags.carry
        bit_7 = (value >> 7)
        bit_6 = (value >> 6 & 1)

        self.registers.A >>= 1
        self.ps.flags.carry = bit_7
        self.ps.flags.overflow = bit_7 ^ bit_6
        self.registers.A |= (carry << 7)
        self.ps.flags.zero = bool(self.registers.A)

    def _i_sbx(self, opcode: int) -> None:
        """AND the values of the accumulator and X register, subtract the immediate value, then store into the X register. (CMP + DEX)

        Args:
            opcode (int): The SBX opcode to process.
        """
        _, value = self._a_immediate()
        temp = self.register.A & self.register.X
        self.ps.flags.carry = (value <= temp)
        temp = ((temp - value) & 0xFF)
        self.registers.X = temp
        self.ps.flags.negative = bool(temp >> 7)
        self.ps.flags.zero = not bool(temp)

    def _i_las(self, opcode: int) -> None:
        """AND memory with the stack pointer, then transfer the result to the accumulator, X, and stack pointer registers. (STA/TXS + LDA/TSX)

        Args:
            opcode (int): The LAS opcode to process.
        """
        _, value = self._a_immediate()
        result = self.registers.stack_pointer & value
        self.registers.A = result
        self.registers.X = result
        self.registers.stack_pointer = result
        self.ps.flags.zero = not bool(result)
        self.ps.flags.negative = bool(result >> 7)
