import unittest
import os
import pymerger


class Comments(unittest.TestCase):

    def test_remove_comments(self):
        input_filepath = os.path.dirname(__file__) + "/bisection.py"
        compare_filepath = os.path.dirname(__file__) + "/bisection_no_comms.py"
        input_file = open(input_filepath, "r", encoding='UTF-8').read()
        compare_file = open(compare_filepath, "r", encoding='UTF-8').read()

        output = pymerger.remove_comments(input_file)
        compare = pymerger.remove_comments(compare_file)
        output_lines = output.split("\n")
        compare_lines = compare.split("\n")

        i = 0
        while i < len(output_lines):
            self.assertEqual(output_lines[i].strip(), compare_lines[i].strip())
            i += 1


if __name__ == '__main__':
    unittest.main()
