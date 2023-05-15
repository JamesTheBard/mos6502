    processor 6502
    org $1000

START:
    LDA #$10
    JSR quicktest
    JMP quit

quicktest:
    NOP
    NOP
    ROL
    LDA #126
    ROL
    CLC
    LDA #$FF
    ROL
    SEC
    LDA #$FF
    ROL
    RTS

quit:
    NOP