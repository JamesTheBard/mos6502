    processor 6502
    org $1000

START:
    CLC
    LDA #$50
    SBC #$F0
    CLC
    LDA #$50
    SBC #$B0
    CLC
    LDA #$50
    SBC #$70
    CLC
    LDA #$50
    SBC #$30
    CLC
    LDA #$D0
    SBC #$F0
    CLC
    LDA #$D0
    SBC #$B0
    CLC
    LDA #$D0
    SBC #$70
    CLC
    LDA #$D0
    SBC #$30
    NOP