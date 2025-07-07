from mos6502.cpu import CPU
from mos6502.bus import Bus, BusRam, BusRom, BusPrinter

# Create RAM bus objects
ram = BusRam()
ram_high = BusRam()

# Create a ROM bus object and load the compiled assembly code
# for the `hello_world` program (hello_world.out)
rom = BusRom()
rom.load_program("hello_world.out")

# Create the "BusPrinter" object that we'll use to print the output
# of the `hello_world.out` program.
printer = BusPrinter()

# Create the bus
bus = Bus()

# Add zero-page RAM to the bus so the CPU can store information to include
# the stack
bus.attach(ram, starting_page=0x00, ending_page=0x0F)

# Add a ROM device starting at 0x1000 and ending at 0x1FFF
bus.attach(rom, starting_page=0x10, ending_page=0x1F)

# This is a custom ROM device that:
# - Writing to 0x2000 will append information to an internal buffer
# - Writing to 0x2001 will print the contents of the buffer to the screen
# - Writing to 0x2002 will clear the internal buffer
#
# Look at `hello_world.asm` for more information
bus.attach(printer, starting_page=0x20, ending_page=0x20)

# Add more RAM on the final page (0xFF00 to 0xFFFF) since all of the interrupt
# vectors live here.
#
# "COP" -> 0xFFF4
# "ABT" -> 0xFFF8
# "NMI" -> 0xFFFA
# "RST" -> 0xFFFC
# "BRK" -> 0xFFFE
bus.attach(ram_high, starting_page=0xFF, ending_page=0xFF)

# Point the CPU to address 0x1000 where the start of ROM is
cpu = CPU(origin = 0x1000)

# Attach the CPU to the bus
cpu.bus = bus

# Run the CPU and halt when encountering the opcode 0x00
cpu.run_program(halt_on=0x00)
