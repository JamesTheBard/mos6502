    processor 6502

    SEG.U vars
    ORG $0080

zpresults ds 16

    SEG

    ORG $1000

begin:
    LDA #$3F
    LDX #$00
    PHA
    PHA
    LDA #$00
    PLA
    STA zpresults,X
    ADC #$70
    PHP
    PHP
    LDA #$00
    PLP
    INX
    STA zpresults,X

flags:
    LDA #$CF
    PHA
    PLP
    PHP
    CLC
    CLD
    CLI
    CLV
    PHP
    LDA #$00
    PHA
    PLP
    PHP
    SEC
    SED
    SEI
    PHP
