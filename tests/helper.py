from typing import Union, List, Optional


class TestsMixin:

    def get_memory_chunk(self, start_range: int, end_range: int) -> List[int]:
        """Retrieve a contiguous chunk of memory from the Bus.

        Args:
            start_range (int): Beginning address to read.
            end_range (int): Ending address to read.

        Returns:
            List[int]: The bytes retreived from the bus converted to ints.
        """
        data = list()
        for i in range(start_range, end_range):
            data.append(self.cpu.bus.read(i))
        return data

    def compare_results_to_memory(self, results_offset: int, results_data: Union[List[int], str], results_labels: Optional[Union[List[str], str]] = None) -> None:
        """Given a list of values and a set of optional labels, compare them to values in emulator memory.

        Args:
            results_offset (int): The offset in memory to compare.
            results_data (Union[List[int], str]): The values to compare as either a list of integers or a space-delimited string of hex values.
            results_labels (Optional[Union[List[str], str]], optional): The labels to show for each comparison as either a list of strings, or a space-delimited string of labels. Defaults to None.
        """
        if type(results_data) == str:
            results_data = [int(i, 16) for i in results_data.split()]
        if results_labels:
            if type(results_labels) == str:
                results_labels = results_labels.split()

        results_data_emul = self.get_memory_chunk(results_offset, results_offset + len(results_data))

        for i in range(0, len(results_data)):
            if results_labels:
                label = results_labels[i]
                self.assertEqual(results_data[i], results_data_emul[i], f"Testing {results_labels[i]} values...")
            else:
                self.assertEqual(results_data[i], results_data_emul[i])
    