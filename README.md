# General Information

The emulator _requires_ Python 3.10 or later.  The assembly written in this repository requires `dasm` because it's the easiest one I could find to install on my laptop when I started this project.

## Requirements

- The `uv` Python package manager
- Python 3.10 or later
- `dasm` if you want to compile the assembly code contained in the repository

## Compiling 6502 Assembly

The `dasm` settings are pretty straightforward.  The output needs to be written raw (`-f3`) which is why we need to change the default format (`-f1`) which adds a two-byte origin in little-endian order (as per the documentation).  We set the origin manually in code, so this extra information isn't really needed.  For more information, check out the `dasm` [documentation](https://raw.githubusercontent.com/dasm-assembler/dasm/master/docs/dasm.pdf).

```
$ dasm hello_world.asm -f3 -ohello_world.out
```

# Current Progress

## Addressing

| Done | Tests | Addressing Mode | Comments |
|:-:|:-:|:--|:--|
| :heavy_check_mark: | :heavy_check_mark: | Implied |  |
| :heavy_check_mark: | :heavy_check_mark: | Accumulator | Handled via direct access to `A` |
| :heavy_check_mark: | :heavy_check_mark: | Immediate | Implemented via `_a_immediate()` |
| :heavy_check_mark: | :heavy_check_mark: | Absolute | Implemented via `_a_absolute()` |
| :heavy_check_mark: | :heavy_check_mark: | X-Indexed Absolute | Implemented via `_a_indexed_absolute('X')` |
| :heavy_check_mark: | :heavy_check_mark: | Y-Indexed Absolute | Implemented via `_a_indexed_absolute('Y')` |
| :heavy_check_mark: | | Indirect | Implemented via `_a_indirect()` |
| :heavy_check_mark: | :heavy_check_mark: | Zero Page | Implemented via `_a_zero_page()` |
| :heavy_check_mark: | :heavy_check_mark: | X-Indexed Zero Page | Implemented via `_a_zero_page_indexed('X')` |
| :heavy_check_mark: | :heavy_check_mark: | Y-Indexed Zero Page | Implemented via `_a_zero_page_indexed('Y')` |
| :heavy_check_mark: | :heavy_check_mark: | X-Indexed Zero Page Indirect | Implemented via `_a_x_indexed_zp_indirect()` |
| :heavy_check_mark: | :heavy_check_mark: | Zero Page Indirect Y-Indexed | Implemented via `_a_zp_indirect_y_indexed()` |

## Bus

The bus is built, but I need to clean it up a bit and document how you attach things to it.  For now, you can create custom `BusObjects` and attach them to the main bus.  There are also two pre-created `BusObjects`: RAM (`BusRam`) and ROM (`BusRom`).  Also, you can attach the same object to the bus at a different location by setting the `mirror` option to `True` when attaching it to the bus.

## Stack

| Done | Feature | Comment |
|:-:|:--|:--|
| :heavy_check_mark: | Stack | Completed |
| :heavy_check_mark: | Stack Pointer | Completed |

| Done | Method | Comment |
|:-:|:--|:--|
| :heavy_check_mark: | `_s_push_byte(value: int)` | Pushes a byte value onto the stack and increments the stack pointer. |
| :heavy_check_mark: | `_s_push_address(address: int)` | Pushes an address onto the stack and increments the stack pointer twice. |
| :heavy_check_mark: | `_s_pop_byte()` | Pulls a byte from the stack and decrements the stack pointer. |
| :heavy_check_mark: | `_s_pop_address()` | Pulls an address from the stack and decrements the stack pointer twice. |

## Instructions

### Documented

| Done | Tests | Instruction | # of Opcodes | Comment |
|:-:|:-:|:-:|:-:|:--|
| :heavy_check_mark: | :heavy_check_mark: | `ADC` | 8 | Completed (including `decimal` mode) |
| :heavy_check_mark: | :heavy_check_mark: | `AND` | 8 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `ASL` | 5 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `BCC` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `BCS` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `BEQ` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `BMI` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `BNE` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `BPL` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `BVC` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `BVS` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `BIT` | 2 | Completed |
| :heavy_check_mark: | | `BRK` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `CLC` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `CLD` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `CLI` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `CLV` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `CMP` | 8 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `CPX` | 2 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `CPY` | 2 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `DEC` | 4 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `DEX` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `DEY` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `EOR` | 8 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `INC` | 4 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `INX` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `INY` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `JMP` | 2 | Completed |
| :heavy_check_mark: | | `JSR` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `LDA` | 8 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `LDX` | 5 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `LDY` | 5 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `LSR` | 5 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `NOP` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `ORA` | 8 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `PHA` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `PHP` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `PLA` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `PLP` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `ROL` | 5 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `ROR` | 5 | Completed |
| :heavy_check_mark: | | `RTI` | 1 | Completed |
| :heavy_check_mark: | | `RTS` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `SBC` | 8 | Completed (including `decimal` mode) |
| :heavy_check_mark: | :heavy_check_mark: | `SEC` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `SED` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `SEI` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `STA` | 7 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `STX` | 3 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `STY` | 3 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `TAX` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `TAY` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `TSX` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `TXA` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `TXS` | 1 | Completed |
| :heavy_check_mark: | :heavy_check_mark: | `TYA` | 1 | Completed |

### Undocumented

All of the undocumented/illegal opcodes have been implemented _except_ for the unstable ones (`ANE`, `LXA`, `SHA`, `SHX`, `SHY`, `TAS`).  These will likely stay unimplented due to the complexity of even trying to simulated some of the potential issues they cause.  Testing for undocumented/illegal opcodes will have to wait until I have the ability to either find a very accurate emulator to test my results against or building an actual MOS6502 testbed.

| Done | Tests | Instruction | # of Opcodes | Comment |
|:-:|:-:|:-:|:-:|:--|
| :heavy_check_mark: | | `ANC` | 7 | Completed |
| :x:                | | `ANE` | 1 | Unstable instruction, not implemented |
| :heavy_check_mark: | | `ARR` | 1 | Completed (including `decimal` mode) |
| :heavy_check_mark: | | `ASR` | 1 | Completed |
| :heavy_check_mark: | | `DCP` | 7 | Completed |
| :heavy_check_mark: | | `ISB` | 7 | Completed (including `decimal` mode) |
| :x:                | | `JAM` | 12 | Not implemented |
| :heavy_check_mark: | | `LAS` | 1 | Completed |
| :heavy_check_mark: | | `LAX` | 6 | Completed |
| :x:                | | `LXA` | 1 | Unstable instruction, not implemented |
| :heavy_check_mark: | | `NOP` | 27 | Completed |
| :heavy_check_mark: | | `RLA` | 7 | Completed |
| :heavy_check_mark: | | `RRA` | 7 | Completed (including `decimal` mode) |
| :heavy_check_mark: | | `SAX` | 4 | Completed |
| :heavy_check_mark: | | `SBX` | 1 | Completed |
| :x:                | | `SHA` | 2 | Unstable instruction, not implemented |
| :x:                | | `SHX` | 1 | Unstable instruction, not implemented |
| :x:                | | `SHY` | 1 | Unstable instruction, not implemented |
| :heavy_check_mark: | | `SLO` | 7 | Completed |
| :heavy_check_mark: | | `SRE` | 7 | Completed |
| :x:                | | `TAS` | 1 | Unstable instruction, not implemented |


## Testing

The project uses `pytest` to run through all of the tests in the `tests` directory.  This is currently the sole external dependency of the project, and can be installed `uv sync`.

To run all of the tests, simply run `pytest` at the root of the repository.
