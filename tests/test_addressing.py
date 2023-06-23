from tests.helpers import setup_cpu

cpu = setup_cpu("tests/asm/addressing.out")
cpu.run_program()


def test_absolute():
    """Test the absolute addressing method in the CPU.
    """
    assert cpu.bus.read(0x2000) == 0x57


def test_absolute_indexing():
    """Test absolute indexing addressing methods (X/Y) in the CPU.
    """
    assert cpu.bus.read(0x2001) == 0x57
    assert cpu.bus.read(0x2002) == 0x57


def test_zero_page():
    """Test the zero page addressing method in the CPU.
    """
    assert cpu.bus.read(0x2003) == 0x57


def test_zero_page_indexed():
    """Test zero page indexed addressing methods (X/Y) in the CPU.
    """
    assert cpu.bus.read(0x2004) == 0x57
    assert cpu.bus.read(0x0022) == 0x02


def test_zero_page_indirect():
    """Test the zero page indirect addressing methods (X-Indexed ZP/ZP Indirect Y-Indexed) in the CPU.
    """
    assert cpu.bus.read(0x2005) == 0x57
    assert cpu.bus.read(0x2006) == 0x57
