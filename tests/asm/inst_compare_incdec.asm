    processor 6502

    SEG.U vars
    ORG $0080

accumulator ds 1
badvalue    ds 1

    SEG

    ORG $1000

increment:
    LDA #$3F
    STA badvalue
    LDA #$00
    STA accumulator
    LDX #$00
    LDY #$00
    INC accumulator
    LDA accumulator
    INX
    INY
    CMP accumulator
    PHP
    CMP badvalue
    PHP
    CPX accumulator
    PHP
    CPX badvalue
    PHP
    CPY accumulator
    PHP
    CPY badvalue
    PHP

incrementNegative:
    LDA #$7F
    STA accumulator
    LDX accumulator
    LDY accumulator
    INC accumulator
    LDA accumulator
    INX
    INY
    CMP accumulator
    PHP
    CMP badvalue
    PHP
    CPX accumulator
    PHP
    CPX badvalue
    PHP
    CPY accumulator
    PHP
    CPY badvalue
    PHP

decrement:
    LDX accumulator
    LDY accumulator
    DEC accumulator
    LDA accumulator
    DEX
    DEY
    CMP accumulator
    PHP
    CMP badvalue
    PHP
    CPX accumulator
    PHP
    CPX badvalue
    PHP
    CPY accumulator
    PHP
    CPY badvalue
    PHP

decrementNegative:
    LDA #$81
    STA accumulator
    LDX accumulator
    LDY accumulator
    DEC accumulator
    LDA accumulator
    DEX
    DEY
    CMP accumulator
    PHP
    CMP badvalue
    PHP
    CPX accumulator
    PHP
    CPX badvalue
    PHP
    CPY accumulator
    PHP
    CPY badvalue
    PHP
