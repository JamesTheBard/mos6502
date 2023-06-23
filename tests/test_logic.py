from tests.helpers import compare_results_to_memory, setup_cpu

cpu = setup_cpu("tests/asm/inst_logic.out")
cpu.run_program()


def test_compare_stack_output():
    """Compare actual results from a 6502 running the assembled test code to what the emulator has.
    """
    labels = "AND ORA EOR BIT".split()[::-1]
    values_raw = "73 33 33 30"
    compare_results_to_memory(0x01FC, values_raw, cpu, labels)


def test_compare_results_output():
    """Compare actual results from a 6502 running the assembled test code to what the emulator has.
    """
    labels = "AND ORA EOR BIT".split()
    values_raw = "00 FF AA AA"
    compare_results_to_memory(0x0205, values_raw, cpu, labels)
