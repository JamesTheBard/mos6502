    processor 6502

    SEG.U vars
    ORG $0080

zperror ds 1

    SEG

    ORG $1000

branchOnCarryClear:
    CLC
    LDA #$00
    LDX #$01
    BCC branchOnCarrySet
    JMP failed 

branchOnCarrySet:
    INX
    SEC
    BCS branchOnResultZero
    JMP failed

branchOnResultZero:
    INX
    LDA #$00
    BEQ branchOnResultMinus
    JMP failed

branchOnResultMinus:
    INX
    LDA #$FE
    BMI branchOnResultNotZero
    JMP failed

branchOnResultNotZero:
    INX
    LDA #$07
    BNE branchOnResultPlus
    JMP failed

branchOnResultPlus:
    INX
    LDA #$07
    BPL branchOnOverflowClear
    JMP failed

branchOnOverflowClear:
    INX
    LDA #$01
    ADC #$10
    BVC branchOnCarrySet
    JMP failed

branchOnOverflowSet:
    INX
    LDA #$FF
    ADC #$01
    BVS completed
    JMP failed

failed:
    TXA
    PHA

completed: