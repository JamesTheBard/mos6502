from exceptions import BusOffsetNotPageAlignedError, BusOffsetOutsideAddressSpaceError, BusAddressError


class BusMixin:

    def verify_offset(self, offset):
        if offset % 2**8:
            raise BusOffsetNotPageAlignedError()
        if offset > 0xFFFF or offset < 0:
            raise BusOffsetOutsideAddressSpaceError()
        return offset


class BusObject(BusMixin):

    def __init__(self, name, offset):
        self.name = "Generic Bus Device"
        self.offset = self.verify_offset(offset)

    def read(self, address: int) -> int:
        pass

    def write(self, address: int) -> int:
        pass

    def __repr__(self):
        return f'BusObject("{self.name}", offset="0x{self.offset:04x}")'


class BusRam(BusObject):
    def __init__(self, offset: int, name: str = None, empty_value: int = 0x00):
        super().__init__(name, offset)
        self.name = name if name else "Random Access Memory"
        self.data = dict()
        self.empty_value = empty_value

    def read(self, address: int) -> int:
        try:
            return self.data[address]
        except KeyError:
            return self.empty_value

    def write(self, address: int, data: int) -> None:
        self.data[address] = data


class BusRom(BusObject):
    def __init__(self, offset: int, data: list, name: str = None, empty_value: int = 0x00):
        super().__init__(name, offset)
        self.name = name if name else "Read-Only Memory"
        self.data = data
        self.empty_value = empty_value

    def read(self, address: int) -> int:
        address -= self.offset
        try:
            return (self.data[address])
        except IndexError:
            return self.empty_value


class BusPrinter(BusObject):
    def __init__(self, offset: int, name: str = None, empty_value: int = 0x00):
        super().__init__(name, offset)
        self.name = name if name else "Screen Printer"
        self.queue = list()
        self.data = dict()
        self.empty_value = empty_value

    def read(self, address: int) -> int:
        address -= self.offset
        try:
            return (self.data[address])
        except KeyError:
            return self.empty_value
    
    def write(self, address: int, data: int):
        address -= self.offset
        self.data[address] = data
        if address == 0x00:
            self.queue.append(data)
        if address == 0x01:
            print("PRINTER:", ''.join([chr(i) for i in self.queue]))
            self.queue = []
        if address == 0x02:
            self.queue = []


class Bus(BusMixin):

    def __init__(self):
        self.objects = dict()

    def attach(self, start_addr: int, end_addr: int, bus_object: BusObject):
        self.verify_offset(start_addr)
        # self.verify_offset(end_addr + 1)
        start_page, end_page = start_addr >> 8, end_addr >> 8
        addr_range = set(range(start_page, end_page + 1))
        if not set.intersection(set(addr_range), *[set(i) for i in self.objects.values()]) or len(self.objects) == 0:
            self.objects[bus_object] = addr_range
        else:
            raise (BusAddressError)

    def read(self, address: int):
        if bus_object := self.get_object_from_address(address):
            return bus_object.read(address)
        return 0x00

    def write(self, address: int, data: int):
        if bus_object := self.get_object_from_address(address):
            bus_object.write(address, data)

    def get_object_from_address(self, address: int) -> BusObject:
        page = address >> 8
        try:
            return [k for k, v in self.objects.items() if page in v][0]
        except IndexError:
            return None

    def __repr__(self):
        return f'Bus(objects={len(self.objects)})'
