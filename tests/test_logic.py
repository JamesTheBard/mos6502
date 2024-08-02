from tests.helpers import compare_results_to_memory, setup_cpu

cpu = setup_cpu("tests/asm/inst_logic.out")
cpu.run_program(halt_on=0x00)


def test_compare_stack_output():
    """Compare actual results from a 6502 running the assembled test code to what the emulator has.
    """
    labels = "AND ORA EOR BIT".split()[::-1]
    values_raw = "73 33 33 30"

    compare_results_to_memory(
        address=0x01FC,
        data=values_raw,
        cpu=cpu,
        labels=labels
    )


def test_compare_results_output():
    """Compare actual results from a 6502 running the assembled test code to what the emulator has.
    """
    labels = "AND ORA EOR BIT".split()
    values_raw = "00 FF AA AA"
    
    compare_results_to_memory(
        address=0x0205,
        data=values_raw,
        cpu=cpu,
        labels=labels
    )
