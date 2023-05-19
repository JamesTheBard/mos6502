from typing import Optional, Union
import ctypes

from mos6502.bus import Bus
from mos6502.instructions import generate_inst_map

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


class Registers:

    def __init__(self):
        a = 0x0
        self.A = 0x0
        self.X = 0x0
        self.Y = 0x0
        self.stack_pointer = 0xFF
        self.program_counter = 0x00

        self.negative = False
        self.overflow = False
        self.decimal = False
        self.zero = True
        self.carry = False
        self.interrupt_disable = False
        self.pbreak = False

        self.header = "NVDIZC"

        self.register_map = {
            "negative": "N",
            "overflow": "V",
            "decimal": "D",
            "interrupt_disable": "I",
            "zero": "Z",
            "carry": "C",
        }

    def reset_registers(self, registers: Union[str, list]):
        if isinstance(registers, str):
            registers = list(registers)
        for register in registers:
            setattr(self, self.register_map[register], False)

    def register_output(self) -> str:
        return ''.join([str(int(getattr(self, i))) for i in self.register_map.keys()])
    
    def get_status(self) -> int:
        value = 0x00
        value += self.negative << 7
        value += self.overflow << 6
        value += self.decimal << 3
        value += self.interrupt_disable << 2
        value += self.zero << 1
        value += self.carry
        return value
    
    def set_status(self, value):
        self.negative = bool(value << 7)
        self.overflow = bool(value & (1 << 6))
        self.decimal = bool(value & (1 << 3))
        self.interrupt_disable = bool(value & (1 << 2))
        self.carry = bool(value & 1)
    

class CPU:

    bus: Bus
    registers: Registers
    current_instruction: list
    current_instruction_pc: int
    interrupt_vectors: dict

    def __init__(self, starting_address: int = 0):
        self.bus = Bus()
        self.registers = Registers()
        self.registers.program_counter = starting_address
        self.current_instruction = list()
        self.interrupt_vectors = {
            "BRK": 0xFFFE,
            "RST": 0xFFFC,
            "NMI": 0xFFFA,
            "ABT": 0xFFF8,
            "COP": 0xFFF4,
        }

    def read_v(self) -> int:
        v = self.bus.read(self.registers.program_counter)
        self.registers.program_counter += 1
        self.current_instruction.append(v)
        return v

    def process_instruction(self) -> int:
        self.current_instruction_pc = self.registers.program_counter
        opcode = self.read_v()
        self.current_instruction = [opcode]
        inst_name = inst_map[opcode]
        getattr(self, f'_i_{inst_name}')(opcode)
        return opcode

    # Stack functions
    def _s_push_address(self, address):
        address = (address - 1) & 0xFFFF
        self._s_push_byte(address >> 8)
        self._s_push_byte(address & 0xFF)

    def _s_push_byte(self, value):
        value &= 0xFF
        address = 0x100 + self.registers.stack_pointer
        self.registers.stack_pointer = (self.registers.stack_pointer - 1) & 0xFF
        self.bus.write(address, value)

    def _s_pop_address(self):
        return self._s_pop_byte() + (self._s_pop_byte() << 8)

    def _s_pop_byte(self) -> int:
        self.registers.stack_pointer = (self.registers.stack_pointer + 1) & 0xFF
        address = 0x100 + self.registers.stack_pointer
        value = self.bus.read(address)
        return value

    # Addressing functions
    def _a_x_indexed_zp_indirect(self) -> list:
        offset = self.read_v()
        address = (offset + self.registers.X) & 0xFF
        address = self.bus.read(address) + (self.bus.read(address + 1) << 8)
        address &= 0xFFFF
        return [address, self.bus.read(address)]

    def _a_zp_indirect_y_indexed(self) -> list:
        offset = self.read_v()
        address = self.bus.read(
            offset) + (self.bus.read(offset + 1) << 8) + self.registers.Y
        address &= 0xFFFF
        return [address, self.bus.read(address)]

    def _a_zero_page(self) -> list:
        address = self.read_v()
        address &= 0xFF
        return [address, self.bus.read(address)]

    def _a_zero_page_indexed(self, register: str) -> list:
        address = self.read_v() + getattr(self.registers, register)
        address &= 0xFF
        return [address, self.bus.read(address)]

    def _a_absolute(self) -> list:
        address = self.read_v() + (self.read_v() << 8)
        address &= 0xFFFF
        return [address, self.bus.read(address)]

    def _a_indirect(self) -> list:
        addr_low, addr_high = self.read_v(), self.read_v()
        address = addr_low + (addr_high << 8)
        address_next = inc_no_carry(address)

        next_address = self.bus.read(
            address) + (self.bus.read(address_next) << 8)
        next_address &= 0xFFFF
        return [next_address, self.bus.read(address)]

    def _a_indexed_absolute(self, register: str) -> list:
        r = getattr(self.registers, register)
        address = self.read_v() + (self.read_v() << 8) + r
        address &= 0xFFFF
        return [address, self.bus.read(address)]

    def _a_immediate(self) -> list:
        return [None, self.read_v()]

    # 6502 Opcodes/Instructions
    def _i_lda(self, opcode):

        def set_accumulator(value):
            self.registers.A = value
            self.registers.zero = not bool(value)
            self.registers.negative = bool(value >> 7)

        match opcode:
            case 0xA1:
                _, v = self._a_x_indexed_zp_indirect()
            case 0xA5:
                _, v = self._a_zero_page()
            case 0xA9:
                _, v = self._a_immediate()
            case 0xAD:
                _, v = self._a_absolute()
            case 0xB1:
                _, v = self._a_zp_indirect_y_indexed()
            case 0xB5:
                _, v = self._a_zero_page_indexed('X')
            case 0xB9:
                _, v = self._a_indexed_absolute('Y')
            case 0xBD:
                _, v = self._a_indexed_absolute('X')

        set_accumulator(v)

    def _i_ldx(self, opcode):

        match opcode:
            case 0xA2:
                _, v = self._a_immediate()
            case 0xAE:
                _, v = self._a_absolute()
            case 0xBE:
                _, v = self._a_indexed_absolute('Y')
            case 0xA6:
                _, v = self._a_zero_page()
            case 0xB6:
                _, v = self._a_zero_page_indexed('Y')

        self.registers.X = v
        self.registers.zero = not bool(v)
        self.registers.negative = bool(v >> 7)

    def _i_ldy(self, opcode):

        match opcode:
            case 0xA0:
                _, v = self._a_immediate()
            case 0xAC:
                _, v = self._a_absolute()
            case 0xBC:
                _, v = self._a_indexed_absolute('X')
            case 0xA4:
                _, v = self._a_zero_page()
            case 0xB4:
                _, v = self._a_zero_page_indexed('X')

        self.registers.Y = v
        self.registers.zero = not bool(v)
        self.registers.negative = bool(v >> 7)

    def _i_adc(self, opcode):

        def add_to_accumulator(value):
            result = value + self.registers.A + self.registers.carry
            self.registers.carry = bool(result > 0xFF)
            result &= 0xFF
            self.registers.overflow = bool((self.registers.A ^ result) & (value ^ result) & 0x80)
            self.registers.negative = bool(result >> 7)
            self.registers.zero = result == 0
            self.registers.A = result

        def add_to_accumulator_sbc(value):
            a = self.registers.A
            v = value
            temp = (a & 0x0F) + (v & 0x0F) + self.registers.carry
            if temp >= 0x0A:
                temp = ((temp + 0x06) & 0x0F) + 0x10
            temp += (a & 0xF0) + (v & 0xF0)
            temp2 = temp
            if temp >= 0xA0:
                temp += 0x60

            self.registers.overflow = bool((~(a ^ v) & (a ^ temp2)) & 0x80)
            self.registers.carry = bool(temp > 99)
            self.registers.negative = bool((temp & 0xFF) >> 7)
            self.registers.zero = ((a + v + self.registers.carry) & 0xFF) == 0
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

        if self.registers.decimal:
            add_to_accumulator_sbc(v)
        else:
            add_to_accumulator(v)

    def _i_and(self, opcode):

        def and_to_accumulator(value):
            self.registers.A &= value
            self.registers.negative = bool(value >> 7)
            self.registers.zero = value == 0

        match opcode:
            case 0x21:
                _, v = self._a_x_indexed_zp_indirect()
            case 0x25:
                _, v = self._a_zero_page()
            case 0x29:
                _, v = self._a_immediate()
            case 0x2D:
                _, v = self._a_absolute()
            case 0x31:
                _, v = self._a_zp_indirect_y_indexed()
            case 0x35:
                _, v = self._a_zero_page_indexed('X')
            case 0x39:
                _, v = self._a_indexed_absolute('Y')
            case 0x3D:
                _, v = self._a_indexed_absolute('X')

        and_to_accumulator(v)

    def _i_asl(self, opcode):

        def arithmetic_shift_left(value, address: Optional[int] = None):
            self.registers.carry = bool(value >> 7)
            value = (value << 1) & 0xFF
            self.registers.zero = value == 0
            self.registers.negative = bool(value >> 7)
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

    def _i_brk(self, opcode):
        self._s_push_address(self.registers.program_counter + 1)
        status = self.registers.get_status()
        status |= (1 << 4)
        self._s_push_byte(status)
        self.registers.pbreak = True
        self.registers.interrupt_disable = True
        address = self.interrupt_vectors["BRK"]
        self.registers.program_counter = self.bus.read(address) + (self.bus.read(address + 1) << 8)

    def _i_cmp(self, opcode):

        def compare(value):
            result = self.registers.A - value
            result = result if result >= 0 else result + 0x100
            self.registers.zero = (self.registers.A == value)
            self.registers.negative = bool(result >> 7)
            self.registers.carry = (value <= self.registers.A)

        match opcode:
            case 0xC9:
                _, v = self._a_immediate()
            case 0xCD:
                _, v = self._a_absolute()
            case 0xDD:
                _, v = self._a_indexed_absolute('X')
            case 0xD9:
                _, v = self._a_indexed_absolute('Y')
            case 0xC5:
                _, v = self._a_zero_page()
            case 0xD5:
                _, v = self._a_zero_page_indexed('X')
            case 0xC1:
                _, v = self._a_x_indexed_zp_indirect()
            case 0xD1:
                _, v = self._a_zp_indirect_y_indexed()

        compare(v)

    def _i_branch(self, opcode):

        v = self.read_v()
        v = convert_int(v)

        match opcode:
            case 0x90:
                if not self.registers.carry:
                    self.registers.program_counter += v
            case 0xB0:
                if self.registers.carry:
                    self.registers.program_counter += v
            case 0xF0:
                if self.registers.zero:
                    self.registers.program_counter += v
            case 0x30:
                if self.registers.negative:
                    self.registers.program_counter += v
            case 0xD0:
                if not self.registers.zero:
                    self.registers.program_counter += v
            case 0x10:
                if not self.registers.negative:
                    self.registers.program_counter += v
            case 0x50:
                if not self.registers.overflow:
                    self.registers.program_counter += v
            case 0x70:
                if self.registers.overflow:
                    self.registers.program_counter += v

    def _i_sta(self, opcode):

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

    def _i_inx(self, opcode):
        self.registers.X = (self.registers.X + 1) & 0xFF
        self.registers.negative = bool(self.registers.X >> 7)
        self.registers.zero = bool(self.registers.X == 0)

    def _i_iny(self, opcode):
        self.registers.Y = (self.registers.Y + 1) & 0xFF
        self.registers.negative = bool(self.registers.Y >> 7)
        self.registers.zero = bool(self.registers.Y == 0)

    def _i_inc(self, opcode):

        match opcode:
            case 0xEE:
                address, v = self._a_absolute()
            case 0xFE:
                address, v = self._a_indexed_absolute('X')
            case 0xE6:
                address, v = self._a_zero_page()
            case 0xF6:
                address, v = self._a_zero_page_indexed('X')

        v = v + 1 & 0xFF
        self.bus.write(address, v)
        # v = self.bus.read(address)
        self.registers.negative = bool(v >> 7)
        self.registers.zero = bool(v == 0)

    def _i_dex(self, opcode):
        self.registers.X = (self.registers.X - 1) & 0xFF
        self.registers.negative = bool(self.registers.X >> 7)
        self.registers.zero = bool(self.registers.X == 0)

    def _i_dey(self, opcode):
        self.registers.Y = (self.registers.Y - 1) & 0xFF
        self.registers.negative = bool(self.registers.Y >> 7)
        self.registers.zero = bool(self.registers.Y == 0)

    def _i_dec(self, opcode):

        match opcode:
            case 0xCE:
                address, v = self._a_absolute()
            case 0xDE:
                address, v = self._a_indexed_absolute('X')
            case 0xC6:
                address, v = self._a_zero_page()
            case 0xD6:
                address, v = self._a_zero_page_indexed('X')

        v = v - 1 & 0xFF
        self.bus.write(address, v)
        # v = self.bus.read(address)
        self.registers.negative = bool(v >> 7)
        self.registers.zero = bool(v == 0)

    def _i_jmp(self, opcode):

        match opcode:
            case 0x4C:
                address, _ = self._a_absolute()
            case 0x6C:
                address, _ = self._a_indirect()

        self.registers.program_counter = address

    def _i_sed(self, opcode):
        self.registers.decimal = True

    def _i_cld(self, opcode):
        self.registers.decimal = False

    def _i_clc(self, opcode):
        self.registers.carry = False

    def _i_cli(self, opcode):
        self.registers.interrupt_disable = False

    def _i_clv(self, opcode):
        self.registers.overflow = False

    def _i_bit(self, opcode):

        match opcode:
            case 0x2C:
                _, v = self._a_absolute()
            case 0x24:
                _, v = self._a_zero_page()

        value = self.registers.A & v
        self.registers.negative = bool(v >> 7)
        self.registers.overflow = bool((v >> 6) & 1)
        self.registers.zero = value == 0

    def _i_cpx(self, opcode):

        match opcode:
            case 0xE0:
                _, v = self._a_immediate()
            case 0xEC:
                _, v = self._a_absolute()
            case 0xE4:
                _, v = self._a_zero_page()

        value = (self.registers.X - v) & 0xFF
        self.registers.negative = (value >> 7)
        self.registers.carry = self.registers.X >= v
        self.registers.zero = self.registers.X == v

    def _i_cpy(self, opcode):

        match opcode:
            case 0xC0:
                _, v = self._a_immediate()
            case 0xCC:
                _, v = self._a_absolute()
            case 0xC4:
                _, v = self._a_zero_page()

        value = (self.registers.Y - v) & 0xFF
        self.registers.negative = (value >> 7)
        self.registers.carry = self.registers.Y >= v
        self.registers.zero = self.registers.Y == v

    def _i_eor(self, opcode):

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
        self.registers.zero = not bool(self.registers.A)
        self.registers.negative = bool(self.registers.A >> 7)

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
        self.registers.negative = False
        self.registers.zero = not bool(v)

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
        self.registers.zero = not bool(self.registers.A)
        self.registers.negative = bool(self.registers.A >> 7)

    def _i_jsr(self, opcode):
        address, _ = self._a_absolute()
        self._s_push_address(self.registers.program_counter)
        self.registers.program_counter = address

    def _i_pha(self, opcode):
        self._s_push_byte(self.registers.A)
    
    def _i_php(self, opcode):
        value = self.registers.get_status()
        value += 0b11 << 4
        self._s_push_byte(value)

    def _i_pla(self, opcode):
        self.registers.A = self._s_pop_byte()
        self.registers.zero = not bool(self.registers.A)
        self.registers.negative = (self.registers.A >> 7)

    def _i_plp(self, opcode):
        value = self._s_pop_byte()
        self.registers.negative = (value >> 7)
        self.registers.overflow = (value >> 6) & 1
        self.registers.decimal = (value >> 3) & 1
        self.registers.interrupt_disable = (value >> 2) & 1
        self.registers.zero = (value >> 1) & 1
        self.registers.carry = value & 1

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

        result = ((v << 1) & 0xFF) + self.registers.carry
        self.registers.carry = v >> 7
        self.registers.negative = result >> 7
        self.registers.zero = not bool(result)

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

        result = ((v >> 1)) + (self.registers.carry << 7)
        self.registers.carry = v & 1
        self.registers.negative = result >> 7
        self.registers.zero = not bool(result)

        if opcode == 0x6A:
            self.registers.A = result
        else:
            self.bus.write(address, result)

    def _i_rti(self, opcode):
        self.registers.set_status(self._s_pop_byte())
        self.registers.program_counter = self._s_pop_address()

    def _i_rts(self, opcode):
        self.registers.program_counter = self._s_pop_address() + 1

    def _i_sec(self, opcode):
        self.registers.carry = True

    def _i_sbc(self, opcode):

        def subtract_binary(v):
            a = self.registers.A
            c = self.registers.carry
            result = a + (v ^ 0xFF) + c
            self.registers.carry = result != (result & 0xFF)
            result &= 0xFF
            self.registers.overflow = bool((a ^ result) & ((v ^ 0xFF) ^ result) & 0x80)
            self.registers.zero = not bool(result)
            self.registers.negative = bool(result & (1 << 7))
            self.registers.A = result

        def subtract_decimal(v):
            # After days of frustration, this is slightly altered code from mnaberez's py65
            # project...and I greatly appreciate that it works as does my sanity...
            a = self.registers.A

            halfcarry = 1
            decimalcarry = 0
            adjust0 = 0
            adjust1 = 0

            nibble0 = (a & 0xf) + (~v & 0xf) + self.registers.carry
            if nibble0 <= 0xf:
                halfcarry = 0
                adjust0 = 10
            nibble1 = ((a >> 4) & 0xf) + ((~v >> 4) & 0xf) + halfcarry
            if nibble1 <= 0xf:
                adjust1 = 10 << 4

            # the ALU outputs are not decimally adjusted
            aluresult = a + (~v & 0xFF) + self.registers.carry

            if aluresult > 0xFF:
                decimalcarry = 1
            aluresult &= 0xFF

            # but the final result will be adjusted
            nibble0 = (aluresult + adjust0) & 0xf
            nibble1 = ((aluresult + adjust1) >> 4) & 0xf

            self.registers.zero = aluresult == 0
            self.registers.carry = bool(decimalcarry)
            self.registers.overflow = bool(((a ^ v) & (a ^ aluresult)) & 0x80)
            self.registers.negative = bool(aluresult >> 7)
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
            
        if self.registers.decimal:
            subtract_decimal(v)
        else:
            subtract_binary(v)

    def _i_sei(self, opcode):
        self.registers.interrupt_disable = True

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
        self.registers.negative = bool(self.registers.X >> 7)
        self.registers.zero = not bool(self.registers.X)

    def _i_tay(self, opcode):
        self.registers.Y = self.registers.A
        self.registers.negative = bool(self.registers.Y >> 7)
        self.registers.zero = not bool(self.registers.Y)

    def _i_tsx(self, opcode):
        self.registers.X = self.registers.stack_pointer
        self.registers.negative = bool(self.registers.X >> 7)
        self.registers.zero = not bool(self.registers.X)

    def _i_txa(self, opcode):
        self.registers.A = self.registers.X
        self.registers.negative = bool(self.registers.A >> 7)
        self.registers.zero = not bool(self.registers.A)

    def _i_txs(self, opcode):
        self.registers.stack_pointer = self.registers.X

    def _i_tya(self, opcode):
        self.registers.A = self.registers.Y
        self.registers.negative = bool(self.registers.A >> 7)
        self.registers.zero = not bool(self.registers.A)




