    processor 6502

    SEG.U vars
    org $0200

full     ds 1
empty    ds 1
highalt  ds 1
lowalt   ds 1
roffset  ds 1
results  ds 32

    SEG

    ORG $1000

prepare:
    LDA #$FF
    STA full
    LDA #$00
    STA empty
    LDX empty
    LDA #$AA
    STA highalt
    LDA #$55
    STA lowalt

verifyAND:
    LDA highalt
    AND lowalt
    CMP full
    PHP
    STA results,X
    INX

verifyOR:
    LDA full
    ORA lowalt
    CMP full
    PHP
    STA results,X
    INX

verifyEOR:
    LDA full
    EOR lowalt
    CMP highalt
    PHP
    STA results,X
    INX

verifyBIT:
    LDA highalt
    BIT lowalt
    PHP
    STA results,X
