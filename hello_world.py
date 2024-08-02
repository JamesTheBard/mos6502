from mos6502.cpu import CPU
from mos6502.bus import Bus, BusRam, BusRom, BusPrinter

ram = BusRam()
rom = BusRom()
rom.load_program("hello_world.out")
printer = BusPrinter()
ram_high = BusRam()

bus = Bus()
bus.attach(ram, starting_page=0x00, ending_page=0x0F)
bus.attach(rom, starting_page=0x10, ending_page=0x1F)
bus.attach(printer, starting_page=0x20, ending_page=0x20)
bus.attach(ram_high, starting_page=0xFF, ending_page=0xFF)

cpu = CPU(origin = 0x1000)
cpu.bus = bus
cpu.run_program(halt_on=0x00)
