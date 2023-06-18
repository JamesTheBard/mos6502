import os
import sys
import unittest
from typing import List

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from mos6502.bus import Bus, BusRam, BusRom
from mos6502.cpu import CPU
from tests.helper import TestsMixin

ram = BusRam()
rom = BusRom()
rom.load_program("asm/inst_shift.out")
ram_high = BusRam()

bus = Bus()
bus.attach(ram, starting_page=0x00, ending_page=0x0F)
bus.attach(rom, starting_page=0x10, ending_page=0x1F)
bus.attach(ram_high, starting_page=0x20, ending_page=0xFF)


class InstructionShiftTests(unittest.TestCase, TestsMixin):

    def setUp(self):
        self.cpu = CPU(origin=0x1000)
        self.cpu.bus = bus
        self.cpu.ps.flags.pbreak = True
        while True:
            self.cpu.process_instruction()
            if self.cpu.bus.read(self.cpu.registers.program_counter) == 0x00:
                return

    def test_compare_stack_output(self) -> None:
        """Compare actual results from a 6502 running the assembled test code to what the emulator has.
        """
        labels = "ASL1 ASL2 ASL3 LSR1 LSR2 LSR3 ROL1 ROL2 ROL3 ROR1 ROR2 ROR3".split()[::-1]
        values_raw = "31 31 31 B1 B0 B1 31 31 31 B1 B0 B1"
        self.compare_results_to_memory(0x01F4, values_raw, labels)

    def test_compare_results_output(self) -> None:
        """Compare actual results from a 6502 running the assembled test code to what the emulator has.
        """
        labels = "ASL1 ASL2 ASL3 LSR1 LSR2 LSR3 ROL1 ROL2 ROL3 ROR1 ROR2 ROR3".split()
        values_raw = "96 EE 92 65 3B 64 96 EE 92 65 3B 64"
        self.compare_results_to_memory(0x0204, values_raw, labels)


if __name__ == "__main__":
    unittest.main()
