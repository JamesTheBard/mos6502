    processor 6502
    org $1000

START:
    SED
    LDA #$10
    ADC #$12
    LDA #$1A
    ADC #$10
    LDA #$90
    ADC #$10
    CLD
    LDA #$10
    ADC #$12
    LDA #$1A
    ADC #$10
    LDA #$90
    ADC #$10

BITTEST:
    LDA #$23
    STA $0030
    STA $0200
    BIT $30
    BIT $0200
    LDA #$40
    STA $0030
    STA $0200
    LDA #$23
    BIT $30
    BIT $0200

COMPARE:
    LDX #$15
    CPX #$14
    CPX #$15
    CPX #$16
    