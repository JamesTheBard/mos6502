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
        # print(f"{cpu.current_instruction[0]:2X}", f"{cpu.registers.A:2X}", cpu.registers.register_output())
except Exception as e:
    print()
    print("ERROR")
    print("=" * 50)
    print(f"PC: {cpu.registers.program_counter - 1:4X}")
    print(f"X : {cpu.registers.X:4X}")
    print(f"A : {cpu.registers.A:4X}")
    raise(e)