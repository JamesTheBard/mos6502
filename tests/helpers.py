from pathlib import Path
from typing import List, Union

from mos6502.bus import Bus, BusRam, BusRom
from mos6502.cpu import CPU


def get_memory_chunk_by_address(start_range: int, end_range: int, cpu: CPU) -> List[int]:
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

def get_memory_chunk_by_size(start_range: int, size: int, cpu: CPU) -> List[int]:
    """Retrieve a contiguous chunk of memory from the Bus given an address and a length in bytes.

    Args:
        start_range (int): Beginning address to read.
        size (int): Size of the memory chunk to read in bytes.
        cpu (CPU): The CPU object being inspected.

    Returns:
        List[int]: The bytes retreived from the bus converted to ints.
    """
    data = list()
    for i in range(start_range, start_range + size):
        data.append(cpu.bus.read(i))
    return data

def compare_results_to_memory(address: int, data: Union[List[int], str], cpu: CPU, labels: Union[List[str], None] = None) -> None:
    """Given a list of values and a set of optional labels, compare them to values in emulator memory.

    Args:
        address (int): The address in memory to compare.
        data (Union[List[int], str]): The values to compare as either a list of integers or a space-delimited string of hex values.
        cpu (CPU): The CPU object being inspected.
        labels (Union[List[str], None], optional): A list of labels associated with each value compared. Defaults to None.
    """

    if type(data) == str:
        data = [int(i, 16) for i in data.split()]

    data_emul = get_memory_chunk_by_size(
        address, len(data), cpu)

    for i in range(0, len(data)):
        if labels:
            print(f"+ [TEST:0x{address + i:04X}] <{labels[i]}> 0x{data[i]:02X} (Real) <=> 0x{data_emul[i]:02X} (Emul)")
        else:
            print(f"+ [TEST:0x{address + i:04X}] 0x{data[i]:02X} (Real) <=> 0x{data_emul[i]:02X} (Emul)")
        assert data[i] == data_emul[i]


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
