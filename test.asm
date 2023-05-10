    processor 6502
    org $1000

START:
    ldx #00

loadchars:
    lda message,x
    beq print
    sta $2000
    inx
    jmp loadchars

message dc "Hello, world!", 0

print:
    lda #01
    sta $2001
