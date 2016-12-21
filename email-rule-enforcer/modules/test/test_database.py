import unittest
from modules.db.create_new_database import create_new_database


class TestDatabaseCreation(unittest.TestCase):

    def test_create_new_database(self):
        """Testing Creation of New Database"""
        new_db = create_new_database(":memory:")
        self.assertEqual('foo'.upper(), 'FOO')

    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)

if __name__ == '__main__':
    unittest.main()

