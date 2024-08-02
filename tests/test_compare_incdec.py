from tests.helpers import compare_results_to_memory, setup_cpu

cpu = setup_cpu("tests/asm/inst_compare_incdec.out")
cpu.run_program(halt_on=0x00)


def test_compare_stack_output():
    """Verify that the values on the stack (via PHP/PHA) are correct during execution.
    """
    labels = ("INC/CMP INC/CMP INC/CPX INC/CPX INC/CPY INC/CPY "
              "INCN/CMP INCN/CMP INCN/CPX INCN/CPX INCN/CPY INCN/CPY "
              "DEC/CMP DEC/CMP DEC/CPX DEC/CPX DEC/CPY DEC/CPY "
              "DECN/CMP DECN/CMP DECN/CPX DECN/CPX DECN/CPY DECN/CPY").split()[::-1]
    values_raw = "31 33 31 33 31 33 31 33 31 33 31 33 31 33 31 33 31 33 B0 33 B0 33 B0 33"
    
    compare_results_to_memory(
        address=0x01E8,
        data=values_raw,
        cpu=cpu,
        labels=labels
    )
