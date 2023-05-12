from rich.traceback import install
from instructions import generate_inst_map
from bus import Bus, BusRom, BusRam, BusPrinter
from cpu import CPU

install(show_locals=False)

start_addr = 0x1000
with open("a.out", "rb") as f:
    data = f.read()

bus = Bus()
bus_ram = BusRam(offset=0x0000, name="Static RAM")
bus_rom = BusRom(offset=0x1000, data=data, name="Program ROM")
bus_printer = BusPrinter(offset=0x2000, name="Printer")

bus.attach(0x0000, 0x0FFF, bus_ram)
bus.attach(0x1000, 0x1FFF, bus_rom)
bus.attach(0x2000, 0x20FF, bus_printer)


print("Currently attached buses")
print("=======================================================")
[print(i) for i in bus.objects]
print()

print(f"Starting program location: {start_addr:#x}")
print()

for i in range(0x30):
    b = bus.read(i + 0x1000)
    print(f'{b:02X}', end=' ', flush=True)
    if not (i + 1) % 16:
        print()
print()

cpu = CPU(starting_address=0x1000)
cpu.bus = bus
try:
    for i in range(200):
        cpu.process_instruction()
        inst_str = ' '.join([f"{i:02X}" for i in cpu.current_instruction])
        print(f"{cpu.current_instruction_pc:04X} | {inst_str:<8} | {cpu.registers.A:02X} {cpu.registers.X:02X} {cpu.registers.Y:02X} |", cpu.registers.register_output())
except Exception as e:
    print()
    print("ERROR")
    print("=" * 50)
    print(f"PC: {cpu.registers.program_counter - 1:4X}")
    print(f"AC: 0x{cpu.registers.A:02X}")
    print(f"XR: 0x{cpu.registers.X:02X}")
    print(f"YR: 0x{cpu.registers.Y:02X}")
    print()
    print(cpu.registers.header)
    print(cpu.registers.register_output())
    raise(e)