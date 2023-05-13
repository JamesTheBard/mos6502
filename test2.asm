    processor 6502
    org $1000

START:
    LDA #$10
    JSR quicktest

quicktest:
    NOP
    NOP
