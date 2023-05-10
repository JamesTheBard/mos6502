from typing import Union, Optional
from instructions import generate_inst_map
from bus import Bus

inst_map = generate_inst_map()

def convert_int(value: int) -> int:
    """
    Convert unsigned int into a properly signed int.
    """
    return ((value >> 7) * -1) * (value & 0x7F)

class Registers:

    def __init__(self):
        self.A = 0x0
        self.X = 0x0
        self.Y = 0x0
        self.stack_pointer = 0xFF
        self.program_counter = 0x00

        self.negative = False
        self.overflow = False
        self.decimal = False
        self.interrupt_disable = False
        self.zero = False
        self.carry = False

        self.register_map = {
            "negative": "N",
            "overflow": "O",
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


class CPU:

    bus: Bus
    registers: Registers

    def __init__(self, starting_address: int = 0):
        self.bus = Bus()
        self.registers = Registers()
        self.registers.program_counter = starting_address

    def read_data(self) -> int:
        data = self.bus.read(self.registers.program_counter)
        self.registers.program_counter += 1
        return data

    def process_instruction(self) -> None:
        opcode = self.read_data()
        inst_name = inst_map[opcode]
        getattr(self, f'_i_{inst_name}')(opcode)

    def x_indexed_zp_indirect(self) -> list:
        offset = self.read_data()
        address = (offset + self.registers.X) & 0xFF
        address = self.bus.read(address) + (self.bus.read(address + 1) << 8)
        address &= 0xFFFF
        return [address, self.bus.read(address)]

    def zp_indirect_y_indexed(self) -> list:
        offset = self.read_data()
        address = self.bus.read(offset) + (self.bus.read(offset + 1) << 8) + self.registers.Y
        address &= 0xFFFF
        return [address, self.bus.read(address)]

    def zero_page(self) -> list:
        address = self.read_data()
        address &= 0xFF
        return [address, self.bus.read(address)]

    def zero_page_indexed(self, register: str) -> list:
        address = self.read_data() + getattr(self.registers, register)
        address &= 0xFF
        return [address, self.bus.read(address)]
    
    def absolute(self) -> list:
        address = self.read_data() + (self.read_data() << 8)
        address &= 0xFFFF
        return [address, self.bus.read(address)]

    def indexed_absolute(self, register: str) -> list:
        register = register.upper()
        address = self.read_data() + (self.read_data() << 8) + getattr(self.registers, register)
        address &= 0xFFFF
        return [address, self.bus.read(address)]
    
    def immediate(self) -> list:
        return [None, self.read_data()]

    def _i_lda(self, opcode):

        def set_accumulator(value):
            self.registers.A = value
            self.registers.zero = not bool(value)
            self.registers.negative = bool(value & 1 << 7)

        match opcode:
            case 0xA1:
                _, data = self.x_indexed_zp_indirect()
            case 0xA5:
                _, data = self.zero_page()
            case 0xA9:
                _, data = self.immediate()
            case 0xAD:
                _, data = self.absolute()
            case 0xB1:
                _, data = self.zp_indirect_y_indexed()
            case 0xB5:
                _, data = self.zero_page_indexed('X')
            case 0xB9:
                _, data = self.indexed_absolute('Y')
            case 0xBD:
                _, data = self.indexed_absolute('X')

        set_accumulator(data)

    def _i_ldx(self, opcode):

        def set_x_register(value):
            self.registers.X = value
            self.registers.zero = not bool(value)
            self.registers.negative = bool(value & 1 << 7)

        match opcode:
            case 0xA2:
                _, data = self.immediate()
            case 0xAE:
                _, data = self.absolute()
            case 0xBE:
                _, data = self.indexed_absolute('Y')
            case 0xA6:
                _, data = self.zero_page()
            case 0xB6:
                _, data = self.zero_page_indexed('Y')

        set_x_register(data)

    def _i_adc(self, opcode):

        def add_to_accumulator(value):
            value += self.registers.A
            self.registers.carry = bool(value > 0xFF)
            value &= 0xFF
            self.registers.overflow = (value & 1 << 7) != (self.registers.A & 1 << 7)
            self.registers.negative = bool(value & 1 << 7)
            self.registers.zero = value == 0
            self.registers.A = value

        match opcode:
            case 0x61:
                _, data = self.x_indexed_zp_indirect()
            case 0x65:
                _, data = self.zero_page()
            case 0x69:
                _, data = self.immediate()
            case 0x6D:
                _, data = self.absolute()
            case 0x71:
                _, data = self.zp_indirect_y_indexed()
            case 0x75:
                _, data = self.zero_page_indexed('X')
            case 0x79:
                _, data = self.indexed_absolute('Y')
            case 0x7D:
                _, data = self.indexed_absolute('X')

        add_to_accumulator(data)

    def _i_and(self, opcode):

        def and_to_accumulator(value):
            self.registers.A ^= value
            self.registers.negative = bool(value & 1 << 7)
            self.registers.zero = value == 0

        match opcode:
            case 0x21:
                _, data = self.x_indexed_zp_indirect()
            case 0x25:
                _, data = self.zero_page()
            case 0x29:
                _, data = self.immediate()
            case 0x2D:
                _, data = self.absolute()
            case 0x31:
                _, data = self.zp_indirect_y_indexed()
            case 0x35:
                _, data = self.zero_page_indexed('X')
            case 0x39:
                _, data = self.indexed_absolute('Y')
            case 0x3D:
                _, data = self.indexed_absolute('X')

        and_to_accumulator(data)
    
    def _i_asl(self, opcode):

        def arithmetic_shift_left(value, address: Optional[int] = None):
            self.registers.carry = bool(value & 1 << 7)
            value = (value << 1) & 0xFF
            self.registers.zero = value == 0
            self.registers.negative = bool(value & 1 << 7)
            return value

        match opcode:
            case 0x06:
                address, data = self.zero_page()
            case 0x0A:
                self.registers.A = arithmetic_shift_left(data)
            case 0x0E:
                address, data = self.absolute()
            case 0x16:
                address, data = self.zero_page_indexed('X')
            case 0x1E:
                address, data = self.indexed_absolute('X')

        if opcode not in [0x0A]:
            self.bus.write(address, arithmetic_shift_left(data))

    def _i_cmp(self, opcode):

        def compare(value):
            result = self.registers.X - value
            result = result if result > 0 else result + 0x100
            self.registers.zero = 1 if result == 0 else 0
            self.registers.negative = bool(result & 1 << 7)
            self.registers.carry = 1 if result <= 0 else 0

        match opcode:
            case 0xC9:
                _, data = self.immediate()
            case 0xCD:
                _, data = self.absolute()
            case 0xDD:
                _, data = self.indexed_absolute('X')
            case 0xD9:
                _, data = self.indexed_absolute('Y')
            case 0xC5:
                _, data = self.zero_page()
            case 0xD5:
                _, data = self.zero_page_indexed('X')
            case 0xC1:
                _, data = self.x_indexed_zp_indirect()
            case 0xD1:
                _, data = self.zp_indirect_y_indexed()

        compare(data)

    def _i_branch(self, opcode):

        data = convert_int(self.read_data())

        match opcode:
            case 0x90:
                if not self.registers.carry:
                    self.registers.program_counter += data
            case 0xB0:
                if self.registers.carry:
                    self.registers.program_counter += data
            case 0xF0:
                if self.registers.zero:
                    self.registers.program_counter += data
            case 0x30:
                if self.registers.negative:
                    self.registers.program_counter += data
            case 0xD0:
                if not self.registers.zero:
                    self.registers.program_counter += data
            case 0x10:
                if not self.registers.negative:
                    self.registers.program_counter += data
            case 0x50:
                if not self.registers.overflow:
                    self.registers.program_counter += data
            case 0x70:
                if self.registers.overflow:
                    self.registers.program_counter += data

    def _i_sta(self, opcode):

        match opcode:
            case 0x8D:
                address, _ = self.absolute()
            case 0x9D:
                address, _ = self.indexed_absolute('X')
            case 0x99:
                address, _ = self.indexed_absolute('Y')
            case 0x85:
                address, _ = self.zero_page()
            case 0x95:
                address, _ = self.zero_page_indexed('X')
            case 0x81:
                address, _ = self.x_indexed_zp_indirect()
            case 0x91:
                address, _ = self.zp_indirect_y_indexed()
        
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
                address, data = self.absolute()
            case 0xFE:
                address, data = self.indexed_absolute('X')
            case 0xE6:
                address, data = self.zero_page()
            case 0xF6:
                address, data = self.zero_page_indexed('X')

        data = data + 1 & 0xFF
        self.bus.write(address, data)
        # data = self.bus.read(address)
        self.registers.negative = bool(data >> 7)
        self.registers.zero = bool(data == 0)

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
                address, data = self.absolute()
            case 0xDE:
                address, data = self.indexed_absolute('X')
            case 0xC6:
                address, data = self.zero_page()
            case 0xD6:
                address, data = self.zero_page_indexed('X')

        data = data - 1 & 0xFF
        self.bus.write(address, data)
        # data = self.bus.read(address)
        self.registers.negative = bool(data >> 7)
        self.registers.zero = bool(data == 0)
