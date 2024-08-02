from tests.helpers import compare_results_to_memory, setup_cpu

cpu = setup_cpu("tests/asm/inst_shift.out")
cpu.run_program(halt_on=0x00)


def test_compare_stack_output():
    """Compare actual results from a 6502 running the assembled test code to what the emulator has.
    """
    labels = "ASL1 ASL2 ASL3 LSR1 LSR2 LSR3 ROL1 ROL2 ROL3 ROR1 ROR2 ROR3".split()[
        ::-1]
    values_raw = "31 31 31 B1 B0 B1 31 31 31 B1 B0 B1"
    compare_results_to_memory(0x01F4, values_raw, cpu, labels)


def test_compare_results_output():
    """Compare actual results from a 6502 running the assembled test code to what the emulator has.
    """
    labels = "ASL1 ASL2 ASL3 LSR1 LSR2 LSR3 ROL1 ROL2 ROL3 ROR1 ROR2 ROR3".split()
    values_raw = "96 EE 92 65 3B 64 96 EE 92 65 3B 64"
    compare_results_to_memory(0x0204, values_raw, cpu, labels)
