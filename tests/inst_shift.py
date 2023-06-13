import os
import sys
import unittest
from typing import List

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from mos6502.bus import Bus, BusRam, BusRom
from mos6502.cpu import CPU

ram = BusRam()
rom = BusRom()
rom.load_program("asm/inst_shift.out")
ram_high = BusRam()

bus = Bus()
bus.attach(ram, starting_page=0x00, ending_page=0x0F)
bus.attach(rom, starting_page=0x10, ending_page=0x1F)
bus.attach(ram_high, starting_page=0x20, ending_page=0xFF)


class InstructionLogicTests(unittest.TestCase):

    def setUp(self):
        self.cpu = CPU(origin=0x1000)
        self.cpu.bus = bus
        self.cpu.ps.flags.pbreak = True
        while True:
            self.cpu.process_instruction()
            if self.cpu.bus.read(self.cpu.registers.program_counter) == 0x00:
                return

    def get_memory_chunk(self, start_range: int, end_range: int) -> List[int]:
        data = list()
        for i in range(start_range, end_range):
            data.append(self.cpu.bus.read(i))
        return data

    def test_compare_stack_output(self) -> None:
        stack_offset = 0x01F4
        stack_labels = "ASL1 ASL2 ASL3 LSR1 LSR2 LSR3 ROL1 ROL2 ROL3 ROR1 ROR2 ROR3".split()[::-1]
        actual_stack_data = "31 31 31 B1 B0 B1 31 31 31 B1 B0 B1"
        actual_stack = [int(i, 16) for i in actual_stack_data.split()]
        mos6502_stack = self.get_memory_chunk(stack_offset, stack_offset + len(actual_stack))

        for i in range(0, len(actual_stack)):
            self.assertEqual(actual_stack[i], mos6502_stack[i], f"Testing {stack_labels[i]} flags...")

    def test_compare_results_output(self) -> None:
        stack_offset = 0x0204
        stack_labels = "ASL1 ASL2 ASL3 LSR1 LSR2 LSR3 ROL1 ROL2 ROL3 ROR1 ROR2 ROR3".split()
        actual_stack_data = "96 EE 92 65 3B 64 96 EE 92 65 3B 64"
        actual_stack = [int(i, 16) for i in actual_stack_data.split()]
        mos6502_stack = self.get_memory_chunk(stack_offset, stack_offset + len(actual_stack))

        for i in range(0, len(actual_stack)):
            self.assertEqual(actual_stack[i], mos6502_stack[i], f"Testing {stack_labels[i]} results...")


if __name__ == "__main__":
    unittest.main()
