from tests.helpers import setup_cpu

cpu = setup_cpu(program_file="tests/asm/inst_branch.out")
cpu.run_program(0x00)

result_codes = "BCC BCS BEQ BMI BNE BPL BVC BVS".split()


def test_compare_results_output():
    """Verify that all branching instructions execute correctly.
    """
    print("SP:", hex(cpu.registers.stack_pointer))
    value = cpu.bus.read(0x01FF)
    if value:
        print(f"Error in the {result_codes[value + 1]} instruction/opcode!")
    assert cpu.bus.read(0x01FF) == 0x00
