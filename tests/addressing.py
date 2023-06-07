import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mos6502.cpu import CPU
from mos6502.bus import Bus, BusRam, BusRom

ram = BusRam()
rom = BusRom()
rom.load_program("asm/addressing.out")
ram_high = BusRam()

bus = Bus()
bus.attach(ram, starting_page=0x00, ending_page=0x0F)
bus.attach(rom, starting_page=0x10, ending_page=0x1F)
bus.attach(ram_high, starting_page=0x20, ending_page=0xFF)


class AddressingTestCase(unittest.TestCase):

    def setUp(self):
        self.cpu = CPU(origin=0x1000)
        self.cpu.bus = bus
        while True:
            self.cpu.process_instruction()
            if self.cpu.current_instruction[0] == 0x00:
                return

    def test_absolute(self):
        self.assertEqual(self.cpu.bus.read(0x2000), 87, msg="Verify Absolute")
    
    def test_absolute_indexing(self):
        self.assertEqual(self.cpu.bus.read(0x2001), 87, msg="Verify X-Indexed Absolute")
        self.assertEqual(self.cpu.bus.read(0x2002), 87, msg="Verify Y-Indexed Absolute")

    def test_zero_page(self):
        self.assertEqual(self.cpu.bus.read(0x2003), 87, msg="Verify Zero Page")

    def test_zero_page_indexed(self):
        self.assertEqual(self.cpu.bus.read(0x2004), 87, msg="Verify X-Indexed Zero Page")
        self.assertEqual(self.cpu.bus.read(0x0022), 2, msg="Verify Y-Indexed Zero Page")

    def test_zero_page_indirect(self):
        self.assertEqual(self.cpu.bus.read(0x2005), 87, msg="Verify X-Indexed Zero Page Indirect")
        self.assertEqual(self.cpu.bus.read(0x2006), 87, msg="Verify Zero Page Indirect Y-Indexed")

if __name__ == "__main__":
    unittest.main()
