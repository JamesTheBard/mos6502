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
rom.load_program("asm/inst_compare_incdec.out")
ram_high = BusRam()

bus = Bus()
bus.attach(ram, starting_page=0x00, ending_page=0x0F)
bus.attach(rom, starting_page=0x10, ending_page=0x1F)
bus.attach(ram_high, starting_page=0x20, ending_page=0xFF)


class InstructionCompareIncDecTests(unittest.TestCase):

    def setUp(self):
        self.cpu = CPU(origin=0x1000)
        self.cpu.bus = bus
        self.cpu.ps.flags.pbreak = True
        while True:
            self.cpu.process_instruction()
            if self.cpu.bus.read(self.cpu.registers.program_counter) == 0x00:
                return

    def get_memory_chunk(self, start_range: int, end_range: int) -> List[int]:
        """Retrieve a contiguous chunk of memory from the Bus.

        Args:
            start_range (int): Beginning address to read.
            end_range (int): Ending address to read.

        Returns:
            List[int]: The bytes retreived from the bus converted to ints.
        """
        data = list()
        for i in range(start_range, end_range):
            data.append(self.cpu.bus.read(i))
        return data

    def test_compare_stack_output(self) -> None:
        results_offset = 0x01E8
        results_labels = "INC INC INC INC INC INC INCN INCN INCN INCN INCN INCN DEC DEC DEC DEC DEC DEC DECN DECN DECN DECN DECN DECN".split()[::-1]
        results_data = "31 33 31 33 31 33 31 33 31 33 31 33 31 33 31 33 31 33 B0 33 B0 33 B0 33".split()
        results_data = [int(i, 16) for i in results_data]
        results_data_emul = self.get_memory_chunk(results_offset, results_offset + len(results_data))

        for i in range(0, len(results_data)):
            self.assertEqual(results_data[i], results_data_emul[i], f"Testing {results_labels[i]} values...")

    
if __name__ == "__main__":
    unittest.main()
