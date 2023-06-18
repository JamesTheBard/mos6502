import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from mos6502.bus import Bus, BusRam, BusRom
from mos6502.cpu import CPU
from tests.helper import TestsMixin


ram = BusRam()
rom = BusRom()
rom.load_program("asm/inst_adc.out")
ram_high = BusRam()

bus = Bus()
bus.attach(ram, starting_page=0x00, ending_page=0x0F)
bus.attach(rom, starting_page=0x10, ending_page=0x1F)
bus.attach(ram_high, starting_page=0x20, ending_page=0xFF)


class InstructionAdcSbcTests(unittest.TestCase, TestsMixin):

    def setUp(self):
        self.cpu = CPU(origin=0x1000)
        self.cpu.bus = bus
        self.cpu.ps.flags.pbreak = True
        while True:
            self.cpu.process_instruction()
            if self.cpu.current_instruction[0] == 0x00:
                return

    def test_adc_flags_binary(self):
        values_raw = "71 71 B0 B0 31 B0 F0 30"
        self.compare_results_to_memory(0x01F8, values_raw)

    def test_adc_values_binary(self):
        values_raw = "60 A0 E0 20 A1 E0 20 61"
        self.compare_results_to_memory(0x0203, values_raw)

    def test_adc_flags_decimal(self):
        values_raw = "F9 F9 39 39 B9 39 79 38"
        self.compare_results_to_memory(0x01F0, values_raw)

    def test_adc_values_decimal(self):
        values_raw = "60 00 41 81 01 41 81 C1"
        self.compare_results_to_memory(0x020B, values_raw)

    def test_sbc_flags_binary(self):
        values_raw = "B0 33 71 71 30 F0 33 31"
        self.compare_results_to_memory(0x01E8, values_raw)

    def test_sbc_values_binary(self):
        values_raw = "40 00 C0 7F 7F 40 00 C0"
        self.compare_results_to_memory(0x0213, values_raw)

    def test_sbc_flags_decimal(self):
        values_raw = "B8 3B 79 79 38 F8 3B 39"
        self.compare_results_to_memory(0x01E0, values_raw)

    def test_sbc_values_decimal(self):
        values_raw = "39 00 60 19 79 40 00 60"
        self.compare_results_to_memory(0x21B, values_raw)


if __name__ == "__main__":
    unittest.main()
