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
rom.load_program("asm/inst_logic.out")
ram_high = BusRam()

bus = Bus()
bus.attach(ram, starting_page=0x00, ending_page=0x0F)
bus.attach(rom, starting_page=0x10, ending_page=0x1F)
bus.attach(ram_high, starting_page=0x20, ending_page=0xFF)


class InstructionLogicTests(unittest.TestCase, TestsMixin):

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
        labels = "AND ORA EOR BIT".split()[::-1]
        values_raw = "73 33 33 30"
        self.compare_results_to_memory(0x01FC, values_raw, labels)

    def test_compare_results_output(self) -> None:
        """Compare actual results from a 6502 running the assembled test code to what the emulator has.
        """
        labels_raw = "AND ORA EOR BIT"
        values_raw = "00 FF AA AA"
        self.compare_results_to_memory(0x0205, values_raw, labels_raw)


if __name__ == "__main__":
    unittest.main()
