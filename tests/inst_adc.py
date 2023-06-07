import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from mos6502.bus import Bus, BusRam, BusRom
from mos6502.cpu import CPU

ram = BusRam()
rom = BusRom()
rom.load_program("asm/inst_adc.out")
ram_high = BusRam()

bus = Bus()
bus.attach(ram, starting_page=0x00, ending_page=0x0F)
bus.attach(rom, starting_page=0x10, ending_page=0x1F)
bus.attach(ram_high, starting_page=0x20, ending_page=0xFF)


class InstructionAdcSbcTests(unittest.TestCase):

    def setUp(self):
        self.cpu = CPU(origin=0x1000)
        self.cpu.bus = bus
        self.cpu.ps.flags.pbreak = True
        self.status_location = 0x01FF
        self.result_location = 0x0203
        while True:
            self.cpu.process_instruction()
            if self.cpu.current_instruction[0] == 0x00:
                return

    def compare_flags(self, offset: int, values: list, verbose: bool = False):
        memory = range(self.status_location - (offset * 8),
                       self.status_location - ((offset + 1) * 8), -1)
        for idx, i in enumerate(memory):
            v = self.cpu.bus.read(i)
            if verbose:
                print(f"{v:08b} {values[idx]:08b} {values[idx] ^ v:08b}")
            self.assertEqual(v, values[idx])

    def compare_values(self, offset: int, values: list, verbose: bool = False):
        memory = range(self.result_location + (offset * 8),
                       self.result_location + ((offset + 1) * 8))
        for idx, i in enumerate(memory):
            v = self.cpu.bus.read(i)
            if verbose:
                print(f"{v:02X} {values[idx]:02X}")
            self.assertEqual(v, values[idx])

    def test_adc_flags_binary(self):
        values = [int(i, 16) for i in "71 71 B0 B0 31 B0 F0 30".split()[::-1]]
        self.compare_flags(
            offset=0,
            values=values,
        )

    def test_adc_values_binary(self):
        values = [int(i, 16) for i in "60 A0 E0 20 A1 E0 20 61".split()]
        self.compare_values(
            offset=0,
            values=values
        )

    def test_adc_flags_decimal(self):
        values = [int(i, 16) for i in "F9 F9 39 39 B9 39 79 38".split()[::-1]]
        self.compare_flags(
            offset=1,
            values=values,
        )

    def test_adc_values_decimal(self):
        values = [int(i, 16) for i in "60 00 41 81 01 41 81 C1".split()]
        self.compare_values(
            offset=1,
            values=values,
        )

    def test_sbc_flags_binary(self):
        values = [int(i, 16) for i in "B0 33 71 71 30 F0 33 31".split()[::-1]]
        self.compare_flags(
            offset=2,
            values=values,
        )

    def test_sbc_values_binary(self):
        values = [int(i, 16) for i in "40 00 C0 7F 7F 40 00 C0".split()]
        self.compare_values(
            offset=2,
            values=values,
        )

    def test_sbc_flags_decimal(self):
        values = [int(i, 16) for i in "B8 3B 79 79 38 F8 3B 39".split()[::-1]]
        self.compare_flags(
            offset=3,
            values=values,
        )

    def test_sbc_values_decimal(self):
        values = [int(i, 16) for i in "39 00 60 19 79 40 00 60".split()]
        self.compare_values(
            offset=3,
            values=values,
        )


if __name__ == "__main__":
    unittest.main()