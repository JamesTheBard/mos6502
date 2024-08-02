from tests.helpers import compare_results_to_memory, setup_cpu

cpu = setup_cpu("tests/asm/inst_stack_flags.out")
cpu.run_program(halt_on=0x00)


def test_compare_results_output():
    """Verify that the stack/flags opcode results are correct.
    """
    labels = "0x0080 0x0081".split()
    values_raw = "3F 00"

    compare_results_to_memory(
        address=0x0080,
        data=values_raw,
        cpu=cpu,
        labels=labels
    )

def test_compare_stack_output():
    """Verify that the stack/flags stack output values are correct.
    """
    values_raw = "3D 30 B2 FF F0 3F"

    compare_results_to_memory(
        address=0x01FA,
        data=values_raw,
        cpu=cpu
    )
