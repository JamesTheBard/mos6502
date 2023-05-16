    processor 6502
    org $1000

absolute:
    LDA #$47
    STA $0300
    LDA #$10
    ADC $0300
    STA $2000  ; Store result in 0x2000 for absolute addressing

absoluteIndexed:
    LDA #$47
    STA $0300
    STA $0301
    LDA #$10
    LDX #$01
    LDY #$01
    ADC $0300,X
    STA $2001
    LDA #$10
    ADC $0300,Y
    STA $2002

zeropage:
    LDA #$47
    STA $0010
    LDA #$10
    ADC $10
    STA $2003

zeropageIndexed:
    LDA #$47
    STA $0012
    LDX #$02
    LDA #$10
    ADC $10,X
    STA $2004
    LDY #$02
    STX $20,Y

zeropageIndirectX:
    LDA #$05
    STA $0032
    LDA #$03
    STA $0033
    LDA #$10
    STA $0305
    LDA #$47
    LDX #$02
    ADC ($30,X)
    STA $2005

zeropageIndirectY:
    LDA #$10
    STA $0307
    LDY #$02
    LDA #$47
    ADC ($32),Y
    STA $2006

