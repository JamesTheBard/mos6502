import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mos6502.cpu import CPU
from mos6502.bus import Bus, BusRam, BusRom

start_addr = 0x1000
with open("asm/addressing.out", "rb") as f:
    data = f.read()

bus = Bus()
bus_ram = BusRam(offset=0x0000, name="Static RAM")
bus_rom = BusRom(offset=0x1000, data=data, name="Program ROM")
bus_ram_2 = BusRam(offset=0xFF00, name="Test RAM")

bus.attach(0x0000, 0x0FFF, bus_ram)
bus.attach(0x1000, 0x1FFF, bus_rom)
bus.attach(0x2000, 0xFFFF, bus_ram_2)

class AddressingTestCase(unittest.TestCase):

    def setUp(self):
        self.cpu = CPU(starting_address=0x1000)
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
