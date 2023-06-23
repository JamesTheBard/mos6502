from typing import List, Optional, Union
from pathlib import Path

from mos6502.bus import Bus, BusRam, BusRom
from mos6502.cpu import CPU


def get_memory_chunk(start_range: int, end_range: int, cpu: CPU) -> List[int]:
    """Retrieve a contiguous chunk of memory from the Bus.

    Args:
        start_range (int): Beginning address to read.
        end_range (int): Ending address to read.

    Returns:
        List[int]: The bytes retreived from the bus converted to ints.
    """
    data = list()
    for i in range(start_range, end_range):
        data.append(cpu.bus.read(i))
    return data


def compare_results_to_memory(results_offset: int, results_data: Union[List[int], str], cpu: CPU, labels: Union[List[str], None] = None) -> int:
    """Given a list of values and a set of optional labels, compare them to values in emulator memory.

    Args:
        results_offset (int): The offset in memory to compare.
        results_data (Union[List[int], str]): The values to compare as either a list of integers or a space-delimited string of hex values.
    """
    if type(results_data) == str:
        results_data = [int(i, 16) for i in results_data.split()]

    results_data_emul = get_memory_chunk(
        results_offset, results_offset + len(results_data), cpu)

    for i in range(0, len(results_data)):
        if labels:
            print(f"- Test: {labels[i]}...")
        assert results_data[i] == results_data_emul[i]


def setup_cpu(program_file: Union[Path, str]):
    ram = BusRam()
    rom = BusRom()
    rom.load_program(program_file)
    ram_high = BusRam()

    bus = Bus()
    bus.attach(ram, starting_page=0x00, ending_page=0x0F)
    bus.attach(rom, starting_page=0x10, ending_page=0x1F)
    bus.attach(ram_high, starting_page=0x20, ending_page=0xFF)

    cpu = CPU(origin=0x1000)
    cpu.bus = bus
    return cpu
