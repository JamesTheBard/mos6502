from tests.helpers import compare_results_to_memory, setup_cpu

cpu = setup_cpu("tests/asm/inst_adc.out")
cpu.run_program(halt_on=0x00)


def test_adc_flags_binary_mode():
    """Verify that the correct flags are set after ADC in binary mode.
    """
    values_raw = "71 71 B0 B0 31 B0 F0 30"
    compare_results_to_memory(0x01F8, values_raw, cpu)


def test_adc_values_binary():
    """Verify that the correct results are given after ADC in binary mode.
    """
    values_raw = "60 A0 E0 20 A1 E0 20 61"
    compare_results_to_memory(0x0203, values_raw, cpu)


def test_adc_flags_decimal():
    """Verify that the correct flags are set after ADC in decimal mode.
    """
    values_raw = "F9 F9 39 39 B9 39 79 38"
    compare_results_to_memory(0x01F0, values_raw, cpu)


def test_adc_values_decimal():
    """Verify that the correct results are given after ADC in decimal mode.
    """
    values_raw = "60 00 41 81 01 41 81 C1"
    compare_results_to_memory(0x020B, values_raw, cpu)


def test_sbc_flags_binary():
    """Verify that the correct flags are set after SBC in binary mode.
    """
    values_raw = "B0 33 71 71 30 F0 33 31"
    compare_results_to_memory(0x01E8, values_raw, cpu)


def test_sbc_values_binary():
    """Verify that the correct results are given after SBC in binary mode.
    """
    values_raw = "40 00 C0 7F 7F 40 00 C0"
    compare_results_to_memory(0x0213, values_raw, cpu)


def test_sbc_flags_decimal():
    """Verify that the correct flags are set after SBC in decimal mode.
    """
    values_raw = "B8 3B 79 79 38 F8 3B 39"
    compare_results_to_memory(0x01E0, values_raw, cpu)


def test_sbc_values_decimal():
    """Verify that the correct results are given after SBC in decimal mode.
    """
    values_raw = "39 00 60 19 79 40 00 60"
    compare_results_to_memory(0x21B, values_raw, cpu)
