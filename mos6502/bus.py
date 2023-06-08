from typing import List, Dict, Union, Tuple
from pathlib import Path


class BusObject:
    """The base BusObject that bus objects should be based on
    """

    offset: Dict[int, bool]
    name: str
    data: dict

    def __init__(self, default_read_value: int = 0x00):
        self.offsets = dict()
        self.default_read_value = default_read_value
        self.name = "BusDefault"
        self.data = dict()

    def _get_offset(self, address: int) -> Tuple[int, bool]:
        """Get the actual offset of the bus object and whether this address is "mirrored" or not.

        Args:
            address (int): The address being accessed.
        """
        offset = sorted([i for i in self.offsets.keys() if i <= address])[0]
        mirror = self.offsets[offset]
        return (offset, mirror)

    def read(self, address: int) -> int:
        """Read the value at the relative address on the bus object

        Args:
            address (int): The relative address to read

        Returns:
            int: The value at the address
        """
        offset, _ = self._get_offset(address)
        address -= offset
        try:
            return self.data[address]
        except KeyError:
            return self.default_read_value

    def write(self, address: int, value: int):
        """Write value to the relative address on the bus object

        Args:
            address (int): The relative address of the value
            value (int): The value/byte to write
        """
        offset, _ = self._get_offset(address)
        address -= offset
        value &= 0xFF
        self.data[address] = value

    def __repr__(self):
        offsets = [f"0x{i:04x}" for i in sorted(self.offsets.keys())]
        return f'BusObject("{self.name}", offset={offsets})'


class BusRom(BusObject):
    """A ROM object that can hold program data and be attached to the 6502 bus.

    Args:
        offset (int): Used by the bus to set the offset when being attached
        default_read_value (int): The value to return when no data is found at the address. Defaults to 0x00.
    """
    
    def __init__(self, default_read_value: int = 0x00):
        super().__init__(default_read_value)
        self.name = "BusROM"

    def write(self, address: int, value: int):
        """Write the value to the given address

        Args:
            address (int): The address to write
            value (int): The value to write to the address
        """
        pass

    def load_program(self, filename: Union[str, Path], address: int = 0):
        """Load an assembled 6502 from a file into ROM

        Args:
            filename (Union[str, Path]): The path to the assembled 6502 file
            address (int, optional): Relative address to load the file. Defaults to 0x00.
        """
        filename = Path(filename)
        with filename.open("rb") as f:
            data = f.read()
        for byte in data:
            self.data[address] = byte
            address += 1


class BusRam(BusObject):
    """A RAM object that can be read/written to and can be attached to the 6502 bus

    Args:
        offset (int): Used by the bus to set the offset when being attached
        default_read_value (int): The value to return when no data is found at the address. Defaults to 0x00.
    """

    def __init__(self, default_read_value: int = 0):
        super().__init__(default_read_value)
        self.name = "BusRAM"


class BusPrinter(BusObject):
    """A simple bus object that can be written to and print out accumulated data to the screen.

    Args:
        offset (int): Used by the bus to set the offset when being attached
        default_read_value (int): The value to return when no data is found at the address. Defaults to 0x00.
    """

    def __init__(self, default_read_value: int = 0):
        super().__init__()
        self.name = "BusPrinter"
        self.queue = list()

    def read(self, address: int) -> int:
        """Read the value at the relative address on the bus object

        Args:
            address (int): The relative address to read

        Returns:
            int: The value at the address
        """
        offset, mirror = self._get_offset(address)
        address -= offset
        try:
            return self.data[address]
        except KeyError:
            return self.default_read_value

    def write(self, address: int, value: int):
        """Write a value to the relate address.  Writing to $XX00 adds the value written to the queue, writing to $XX01 prints the queue to the screen, and writing to $XX02 clears the queue.

        Args:
            address (int): The relative address to write.
            value (int): The value to write to the address.
        """
        offset, mirror = self._get_offset(address)
        address -= offset
        if address >= 0x0003:
            return
        self.data[address] = value
        match address:
            case 0x0000:
                self.queue.append(value)
            case 0x0001:
                print(f"PRINTER: {''.join([chr(i) for i in self.queue])}")
                self.queue = dict()
            case 0x0002:
                self.queue = dict()


class Bus:
    """A basic implementation of the 6502 bus.

    Returns:
        default_read_value (int): The default return value for reads when there is no data.
    """

    bus_objects: Dict[int, BusObject]

    def __init__(self):
        self.bus_objects = {i: None for i in range(0, 0xFF)}
        self.default_read_value = 0xFF

    def read(self, address: int) -> int:
        """Read a value off of the bus.

        Args:
            address (int): The address to read

        Returns:
            int: The value at the address on the bus
        """
        if not (bus_object := self.bus_objects[address >> 8]):
            return self.default_read_value
        return bus_object.read(address)

    def write(self, address: int, value: int) -> None:
        """Write a value to the bus.

        Args:
            address (int): The address to write
            value (int): The value to write
        """
        if not (bus_object := self.bus_objects[address >> 8]):
            return
        bus_object.write(address, value)

    def attach(self, bus_object: BusObject, starting_page: int, ending_page: int, mirror: bool = False):
        """Attach a bus object to the bus.

        Args:
            bus_object (BusObject): The bus object to attach
            starting_page (int): The starting page the bus object will attach at
            ending_page (int): The last page the bus object with attach to
            mirror (bool, optional): Whether this is a mirror-copy or not. Defaults to False.
        """
        bus_object.offsets[(starting_page & 0xFF) << 8] = mirror
        for i in range(starting_page, ending_page + 1):
            self.bus_objects[i] = bus_object

    def reset_bus(self):
        """Remove all bus objects from the bus.
        """
        for i in self.bus_objects.keys():
            self.bus_objects[i] = None

    def get_bus_objects(self) -> List[BusObject]:
        """Return all of the bus objects attached to the bus.

        Returns:
            List[BusObject]: A list of currently connected BusObjects
        """
        objects = set(self.bus_objects.values())
        objects.discard(None)
        return list(objects)
