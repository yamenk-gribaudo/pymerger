import unittest
import os
from contextlib import redirect_stdout
import io
import pymerger


class Merger(unittest.TestCase):

    def test_collition_and_ciruclar_dependencies(self):
        filepath = os.path.dirname(__file__) + \
            "/collition_and_ciruclar_dependencies/**"
        f = io.StringIO()
        with redirect_stdout(f):
            pymerger.merge([filepath])
        out = f.getvalue()

        self.assertIn("DEFINITION COLLITIONS", out)
        self.assertIn("CIRCULAR DEPENDENCIES", out)

    def test_collition_and_no_ciruclar_dependencies(self):
        filepath = os.path.dirname(__file__) + \
            "/collition_and_no_ciruclar_dependencies/**"
        f = io.StringIO()
        with redirect_stdout(f):
            pymerger.merge([filepath])
        out = f.getvalue()

        self.assertIn("DEFINITION COLLITIONS", out)
        self.assertNotIn("CIRCULAR DEPENDENCIES", out)

    def test_no_collition_and_ciruclar_dependencies(self):
        filepath = os.path.dirname(__file__) + \
            "/no_collition_and_ciruclar_dependencies/**"
        f = io.StringIO()
        with redirect_stdout(f):
            pymerger.merge([filepath])
        out = f.getvalue()

        self.assertNotIn("DEFINITION COLLITIONS", out)
        self.assertIn("CIRCULAR DEPENDENCIES", out)

    def test_no_collition_and_no_ciruclar_dependencies(self):
        filepath = os.path.dirname(
            __file__) + "/no_collition_and_no_ciruclar_dependencies/**"
        f = io.StringIO()
        with redirect_stdout(f):
            pymerger.merge([filepath])
        out = f.getvalue()

        self.assertNotIn("DEFINITION COLLITIONS", out)
        self.assertNotIn("CIRCULAR DEPENDENCIES", out)


if __name__ == '__main__':
    unittest.main()
