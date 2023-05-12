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
