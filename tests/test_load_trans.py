from tests.helpers import setup_cpu, compare_results_to_memory

cpu = setup_cpu("tests/asm/inst_load_trans.out")
cpu.run_program(halt_on=0x00)

def test_compare_results_output():
    """Verify that stored results match actual results.
    """
    labels = "STA TAX/STX TYA/TAX/STY TXA/STA TSX/STX".split()
    values_raw = "77 77 55 03 EF"

    compare_results_to_memory(
        address=0x0080,
        data=values_raw,
        cpu=cpu,
        labels=labels
    )

def test_compare_stack_output() -> None:
    """Verify that stack results match actual stack values.
    """
    values_raw = "B0 B0 00 00 00 00 00 00 00 00 00 00 30 30 30 30 30"
    
    compare_results_to_memory(
        address=0x01EF,
        data=values_raw,
        cpu=cpu
    )
