    processor 6502

    SEG.U vars
    org $0200

acounter ds 1
mcounter ds 1
rcounter ds 1
results  ds 32
decimal  ds 1

    SEG

    ORG $1000

    CLD
    LDX #$00
    STX acounter
    STX mcounter
    STX rcounter
    STX decimal
    JMP adcOperations

accum   dc.b $50,$90,$00
memory  dc.b $10,$50,$90,$D0,$00

adcOperations:
    LDX acounter
    LDA accum,X
    BEQ adcFinal
    LDX mcounter
    LDY memory,X
    BEQ incrementAdcAccum
    ADC memory,X
    PHP
    LDX rcounter
    STA results,X
    INC rcounter
    INC mcounter
    JMP adcOperations

incrementAdcAccum:
    LDX #$00
    STX mcounter
    INC acounter
    JMP adcOperations

adcFinal:
    LDX decimal
    BNE sbcInit
    SED
    CLC
    LDX #$00
    STX acounter
    STX mcounter
    INC decimal
    JMP adcOperations

sbcInit:
    LDX #$00
    STX acounter
    STX mcounter
    STX decimal
    CLD

sbcOperations:
    LDX acounter
    LDA accum,X
    BEQ sbcFinal
    LDX mcounter
    LDY memory,X
    BEQ incrementSbcAccum
    SBC memory,X
    PHP
    LDX rcounter
    STA results,X
    INC rcounter
    INC mcounter
    JMP sbcOperations

incrementSbcAccum:
    LDX #$00
    STX mcounter
    INC acounter
    JMP sbcOperations

sbcFinal:
    LDX decimal
    BNE quit
    SED
    CLC
    LDX #$00
    STX acounter
    STX mcounter
    INC decimal
    JMP sbcOperations

quit:
    NOP