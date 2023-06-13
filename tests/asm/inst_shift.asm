    processor 6502

    SEG.U vars
    org $0200

random1  ds 1
random2  ds 1
random3  ds 1
roffset  ds 1
results  ds 32

    SEG

    ORG $1000

prepareData:
    LDA #$CB
    STA random1
    LDA #$77
    STA random2
    LDA #$C9
    STA random3
    LDX #$00

prepareCounter:
    LDY #$00

testASL:
    CPY #$03
    BEQ prepareLSR
    LDA random1,Y
    ASL
    PHP
    STA results,X
    INX
    INY
    JMP testASL

prepareLSR:
    LDY #$00

testLSR:
    CPY #$03
    BEQ prepareROL
    LDA random1,Y
    LSR
    PHP
    STA results,X
    INX
    INY
    JMP testLSR

prepareROL:
    LDY #$00

testROL:
    CPY #$03
    BEQ prepareROR
    LDA random1,Y
    ROL
    PHP
    STA results,X
    INX
    INY
    JMP testROL

prepareROR:
    LDY #$00

testROR:
    CPY #$03
    BEQ finish
    LDA random1,Y
    ROR
    PHP
    STA results,X
    INX
    INY
    JMP testROR

finish: