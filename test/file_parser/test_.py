import unittest
import os
import pymerger

filepath = os.path.dirname(__file__) + "/seeyou.py"
output = pymerger.parse(filepath)


class Parser(unittest.TestCase):

    def test_name_in_parsed_file(self):
        name = "seeyou"
        self.assertTrue(output['name'] == name)

    def test_filepath_in_parsed_file(self):
        self.assertTrue(output["filepath"] == filepath)

    def test_imports_in_parsed_file(self):
        compare_object = [
            {'name': 'something', 'asname': 'something'},
            {'name': 'somethingelse', 'asname': 'otherelse'}
        ]
        self.assertListEqual(compare_object, output["imports"])

    def test_from_imports_in_parsed_file(self):
        compare_object = [
            {'name': 'otherthing', 'asname': 'otherthing', 'module': 'somewhere'},
            {'name': 'the', 'asname': 'rainbow', 'module': 'over'}
        ]
        self.assertListEqual(compare_object, output["from_imports"])

    def test_definitions(self):
        compare_object = {'otherelse', 'func', 'inst', 'var3',
                          'otherthing', 'var', 'something', 'var2', 'clas', 'rainbow'}
        self.assertSetEqual(compare_object, output["definitions"])


if __name__ == '__main__':
    unittest.main()
