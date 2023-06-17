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
rom.load_program("asm/inst_branch.out")
ram_high = BusRam()

bus = Bus()
bus.attach(ram, starting_page=0x00, ending_page=0x0F)
bus.attach(rom, starting_page=0x10, ending_page=0x1F)
bus.attach(ram_high, starting_page=0x20, ending_page=0xFF)


class InstructionBranchingTests(unittest.TestCase):

    def setUp(self):
        self.cpu = CPU(origin=0x1000)
        self.cpu.bus = bus
        self.cpu.ps.flags.pbreak = True
        self.result_codes = "BCC BCS BEQ BMI BNE BPL BVC BVS".split()
        while True:
            self.cpu.process_instruction()
            if self.cpu.bus.read(self.cpu.registers.program_counter) == 0x00:
                return

    def test_compare_results_output(self) -> None:
        value = self.cpu.bus.read(0x01FF)
        self.assertEqual(value, 0x00, f"Issue with the f{self.result_codes[value + 1]} instruction.")


if __name__ == "__main__":
    unittest.main()
