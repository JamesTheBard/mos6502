from pathlib import Path
from typing import List, Union

from mos6502.bus import Bus, BusRam, BusRom
from mos6502.cpu import CPU


def get_memory_chunk(start_range: int, end_range: int, cpu: CPU) -> List[int]:
    """Retrieve a contiguous chunk of memory from the Bus.

    Args:
        start_range (int): Beginning address to read.
        end_range (int): Ending address to read.
        cpu (CPU): The CPU object being inspected.

    Returns:
        List[int]: The bytes retreived from the bus converted to ints.
    """
    data = list()
    for i in range(start_range, end_range):
        data.append(cpu.bus.read(i))
    return data


def compare_results_to_memory(results_offset: int, results_data: Union[List[int], str], cpu: CPU, labels: Union[List[str], None] = None) -> None:
    """Given a list of values and a set of optional labels, compare them to values in emulator memory.

    Args:
        results_offset (int): The offset in memory to compare.
        results_data (Union[List[int], str]): The values to compare as either a list of integers or a space-delimited string of hex values.
        cpu (CPU): The CPU object being inspected.
        labels (Union[List[str], None], optional): A list of labels associated with each value compared. Defaults to None.
    """

    if type(results_data) == str:
        results_data = [int(i, 16) for i in results_data.split()]

    results_data_emul = get_memory_chunk(
        results_offset, results_offset + len(results_data), cpu)

    for i in range(0, len(results_data)):
        if labels:
            print(f"+ [TEST:0x{results_offset + i:04X}] <{labels[i]}> 0x{results_data[i]:02X} (Real) <=> 0x{results_data_emul[i]:02X} (Emul)")
        else:
            print(f"+ [TEST:0x{results_offset + i:04X}] 0x{results_data[i]:02X} (Real) <=> 0x{results_data_emul[i]:02X} (Emul)")
        assert results_data[i] == results_data_emul[i]


def setup_cpu(program_file: Union[Path, str]) -> CPU:
    """Setup a default testing configuration to include bus settings, CPU settings, and assembled program to load into the ROM.

    Args:
        program_file (Union[Path, str]): The assembled 6502 program to load into ROM.

    Returns:
        CPU: The newly instantiated CPU object to execute code on.
    """
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
