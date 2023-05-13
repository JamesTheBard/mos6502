# Current Progress

## Addressing

| Done | Addressing Mode | Comments |
|:-:|:--|:--|
| :heavy_check_mark: | Implied |  |
| :heavy_check_mark: | Accumulator | Handled via direct access to `A` |
| :heavy_check_mark: | Immediate | Implemented via `_a_immediate()` |
| :heavy_check_mark: | Absolute | Implemented via `_a_absolute()` |
| :heavy_check_mark: | X-Indexed Absolute | Implemented via `_a_indexed_absolute('X')` |
| :heavy_check_mark: | Y-Indexed Absolute | Implemented via `_a_indexed_absolute('Y')` |
| :heavy_check_mark: | Indirect | Implemented via `_a_indirect()` |
| :heavy_check_mark: | Zero Page | Implemented via `_a_zero_page()` |
| :heavy_check_mark: | X-Indexed Zero Page | Implemented via `_a_zero_page_indexed('X')` |
| :heavy_check_mark: | Y-Indexed Zero Page | Implemented via `_a_zero_page_indexed('Y')` |
| :heavy_check_mark: | X-Indexed Zero Page Indirect | Implemented via `_a_x_indexed_zp_indirect()` |
| :heavy_check_mark: | Zero Page Indirect Y-Indexed | Implemented via `_a_zp_indirect_y_indexed()` |

## Bus

The bus is built, but I need to clean it up a bit and document how you attach things to it.  For now, you can create custom `BusObjects` and attach them to the main bus.  There are also two pre-created `BusObjects`: RAM (`BusRam`) and ROM (`BusRom`).

## Stack

| Done | Feature | Comment |
|:-:|:--|:--|
| :heavy_check_mark: | Stack | Completed |
| :heavy_check_mark: | Stack Pointer | Completed |

| Done | Method | Comment |
|:-:|:--|:--|
| :heavy_check_mark: | `_s_push_byte(value)` | Pushes a byte value onto the stack and increments the stack pointer. |
| :heavy_check_mark: | `_s_push_address(address)` | Pushes an address onto the stack and increments the stack pointer twice. |
| :heavy_check_mark: | `_s_pop_byte()` | Pulls a byte from the stack and decrements the stack pointer. |
| :heavy_check_mark: | `_s_pop_address()` | Pulls an address from the stack and decrements the stack pointer twice. |

## Instructions

| Done | Instruction | # of Opcodes | Comment |
|:-:|:-:|:-:|:--|
| :heavy_check_mark: | `ADC` | 8 | Completed (including `decimal` mode) |
| :heavy_check_mark: | `AND` | 8 | Completed |
| :heavy_check_mark: | `ASL` | 5 | Completed |
| :heavy_check_mark: | Branch | 8 | Completed |
| :heavy_check_mark: | `BIT` | 2 | Completed |
|   | `BRK` | |
| :heavy_check_mark: | `CLC` | 1 | Completed |
| :heavy_check_mark: | `CLD` | 1 | Completed |
| :heavy_check_mark: | `CLI` | 1 | Completed |
| :heavy_check_mark: | `CLV` | 1 | Completed |
| :heavy_check_mark: | `CMP` | 8 | Completed |
| :heavy_check_mark: | `CPX` | 2 | Completed |
| :heavy_check_mark: | `CPY` | 2 | Completed |
| :heavy_check_mark: | `DEC` | 4 | Completed |
| :heavy_check_mark: | `DEX` | 1 | Completed |
| :heavy_check_mark: | `DEY` | 1 | Completed |
| :heavy_check_mark: | `EOR` | 8 | Completed |
| :heavy_check_mark: | `INC` | 4 | Completed |
| :heavy_check_mark: | `INX` | 1 | Completed |
| :heavy_check_mark: | `INY` | 1 | Completed |
| :heavy_check_mark: | `JMP` | 2 | Completed |
| :heavy_check_mark: | `JSR` | 1 | Completed |
| :heavy_check_mark: | `LDA` | 8 | Completed |
| :heavy_check_mark: | `LDX` | 5 | Completed |
| :heavy_check_mark: | `LDY` | 5 | Completed |
| :heavy_check_mark: | `LSR` | 5 | Completed |
| :heavy_check_mark: | `NOP` | 1 | Completed |
| :heavy_check_mark: | `ORA` | 8 | Completed |
| :heavy_check_mark: | `PHA` | 1 | Completed |
| :heavy_check_mark: | `PHP` | 1 | Completed |
| :heavy_check_mark: | `PLA` | 1 | Completed |
| :heavy_check_mark: | `PLP` | 1 | Completed |
|   | `ROL` | | |
|   | `ROR` | | |
|   | `RTI` | | |
|   | `RTS` | | |
|   | `SBC` | | |
|   | `SEC` | | |
| :heavy_check_mark: | `SED` | 1 | Completed |
|   | `SEI` | | |
| :heavy_check_mark: | `STA` | 7 | Completed |
|   | `STX` | | |
|   | `STY` | | |
|   | `TAX` | | |
|   | `TAY` | | |
|   | `TSX` | | |
|   | `TXA` | | |
|   | `TXS` | | |
|   | `TYA` | | |