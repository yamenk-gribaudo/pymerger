import unittest
import pymerger

class Circular_dependencies(unittest.TestCase):

    def test_not_circular_dependency(self):
        input_ = [
            {'parents': ["a"], 'dependencies':["b"]}, 
            {'parents': ["b"], 'dependencies':["c"]},
            {'parents': ["c"], 'dependencies':[]}
        ]
        output = pymerger.find_circular_dependencies(input_)
        self.assertEqual(0, len(output))
        
    def test_circular_dependency(self):
        input_ = [
            {'parents': ["a"], 'dependencies':["b"]}, 
            {'parents': ["b"], 'dependencies':["a"]}
        ]
        output = pymerger.find_circular_dependencies(input_)
        self.assertEqual(3, len(output))

    def test_no_parents(self):
        input_ = [
            {'dependencies':["b"]}, 
        ]
        self.assertRaises(TypeError, pymerger.find_circular_dependencies, input_)

    def test_is_dependency_but_not_parent(self):
        input_ = [
            {'parents': ["a"], 'dependencies':["b"]}, 
            {'parents': ["b"], 'dependencies':["c"]},
        ]
        output = pymerger.find_circular_dependencies(input_)
        self.assertEqual(0, len(output))


    def test_parent_with_multiple_dependencies(self):
        input_ = [
            {'parents': ["a"], 'dependencies':["b","c","d"]}, 
            {'parents': ["b"], 'dependencies':["c"]},
            {'parents': ["c"], 'dependencies':["d","e"]},
            {'parents': ["d"], 'dependencies':["e", "f"]},
            {'parents': ["e"], 'dependencies':["b", "a"]},
        ]
        output = pymerger.find_circular_dependencies(input_)
        self.assertEqual(4, len(output))

if __name__ == '__main__':
    unittest.main()
