# Registers
#===================================================
# A, X, Y - 8-bit
# Stack: 0x0100 -> 0x01ff
# SP: (ff - len(stuff on stack))
# PC: Current line number of executing code
#
# Flags:
#===================================================
# 7  bit  0
# ---- ----
# NVss DIZC
# |||| ||||
# |||| |||+- Carry
# |||| ||+-- Zero
# |||| |+--- Interrupt Disable
# |||| +---- Decimal
# ||++------ No CPU effect, see: the B flag
# |+-------- Overflow
# +--------- Negative

instr_6502 = {
    "adc": [0x61, 0x65, 0x69, 0x6D, 0x71, 0x75, 0x79, 0x7D],
    "and": [0x21, 0x25, 0x29, 0x2D, 0x31, 0x35, 0x39, 0x3D],
    "asl": [0x06, 0x0A, 0x0E, 0x16, 0x1E],
    "branch": [0x90, 0xB0, 0xF0, 0x30, 0xD0, 0x10, 0x50, 0x70],
    "bit": [0x24, 0x2C],
    "brk": [0x00],
    "clc": [0x18],
    "cld": [0xD8],
    "cli": [0x58],
    "clv": [0xB8],
    "cmp": [0xC1, 0xC5, 0xC9, 0xCD, 0xD1, 0xD5, 0xD9, 0xDD],
    "cpx": [0xE0, 0xE4, 0xEC],
    "cpy": [0xC0, 0xC4, 0xCC],
    "dec": [0xC6, 0xCE, 0xD6, 0xDE],
    "dex": [0xCA],
    "dey": [0x88],
    "eor": [0x41, 0x45, 0x49, 0x4D, 0x51, 0x55, 0x59, 0x5D],
    "inc": [0xE6, 0xEE, 0xF6, 0xFE],
    "inx": [0xE8],
    "iny": [0xC8],
    "jmp": [0x4C, 0x6C],
    "jsr": [0x20],
    "lda": [0xA1, 0xA5, 0xA9, 0xAD, 0xB1, 0xB5, 0xB9, 0xBD],
    "ldx": [0xA2, 0xA6, 0xAE, 0xB6, 0xBE],
    "ldy": [0xA0, 0xA4, 0xAC, 0xB4, 0xBC],
    "lsr": [0x46, 0x4A, 0x4E, 0x56, 0x5E],
    "nop": [0xEA],
    "ora": [0x01, 0x05, 0x09, 0x0D, 0x11, 0x15, 0x19, 0x1D],
    "pha": [0x48],
    "php": [0x08],
    "pla": [0x68],
    "plp": [0x28],
    "rol": [0x26, 0x2A, 0x2E, 0x36, 0x3E],
    "ror": [0x66, 0x6A, 0x6E, 0x76, 0x7E],
    "rti": [0x40],
    "rts": [0x60],
    "sbc": [0xE1, 0xE5, 0xE9, 0xED, 0xF1, 0xF5, 0xF9, 0xFD],
    "sec": [0x38],
    "sed": [0xF8],
    "sei": [0x78],
    "sta": [0x81, 0x85, 0x8D, 0x91, 0x95, 0x99, 0x9D],
    "stx": [0x86, 0x8E, 0x96],
    "sty": [0x84, 0x8C, 0x94],
    "tax": [0xAA],
    "tay": [0xA8],
    "tsx": [0xBA],
    "txa": [0x8A],
    "txs": [0x9A],
    "tya": [0x98],
}

# Illegal opcodes
instr_6502_illegal = {
    "anc": [0x0B, 0x2B],
    "arr": [0x6B],
    "asr": [0x4B],
    "dcp": [0xC7, 0xD7, 0xCF, 0xDF, 0xDB, 0xC3, 0xD3],
    "isb": [0xE7, 0xF7, 0xEF, 0xFF, 0xFB, 0xE3, 0xF3],
    "las": [0xBB],
    "lax": [0xA7, 0xAF, 0xBF, 0xA3, 0xB3, 0xB7],
    # "lxa": [0xAB],
    # "nop": [0x80, 0x04, 0x14, 0x0C, 0x1C],
    "rla": [0x27, 0x37, 0x2F, 0x3F, 0x3B, 0x23, 0x33],
    "rra": [0x67, 0x77, 0x6F, 0x7F, 0x7B, 0x63, 0x73],
    "sax": [0x87, 0x8F, 0x83, 0x97],
    "sbx": [0xCB],
    # "sha": [0x9F, 0x93],
    # "shs": [0x9B],
    # "shx": [0x9E],
    # "shy": [0x9C],
    "slo": [0x07, 0x17, 0x0F, 0x1F, 0x1B, 0x03, 0x13],
    "sre": [0x47, 0x57, 0x4F, 0x5F, 0x5B, 0x43, 0x53],
}

def generate_inst_map(include_illegal: bool = False) -> dict:
    """Generate a map of opcodes and its associated instruction. This is used by the CPU to determine which method to use.

    Args:
        include_illegal (bool): Include the illegal opcodes in the instruction map for processing.

    Returns:
        dict: A map of opcodes to their associated instruction.
    """
    new = dict()
    i_6502 = instr_6502
    if include_illegal:
        keys = set(instr_6502).union(instr_6502_illegal)
        i_6502 = dict((k, instr_6502.get(k, []) + instr_6502_illegal.get(k, [])) for k in keys)
        
    i_6502 = {i: list(set(j)) for i, j in i_6502.items()}
    for inst, opcodes in i_6502.items():
        for opcode in opcodes:
            new[opcode] = inst
    return dict(sorted(new.items()))
