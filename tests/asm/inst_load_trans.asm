    processor 6502

    SEG.U vars
    ORG $0080

zpresults ds 16

    SEG

    ORG $1000

nonStackStuff:
    LDX #$00
    LDY #$01
    LDA #$77
    STA zpresults,X
    PHP
    INX
    TAX
    STX zpresults,Y
    PHP
    TYA
    TAX
    LDA #$55
    PHP
    TAY
    INX
    STY zpresults,X
    PHP
    INX
    TXA
    STA zpresults,X
    PHP

stackStuff:
    TXA
    TAY
    INY
    LDX #$F0
    TXS
    PHP
    TSX
    STX zpresults,Y
    PHP
