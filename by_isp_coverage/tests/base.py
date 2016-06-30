import os
import unittest

BASE_DIR = os.path.dirname(__file__)

PAGES_DIR = os.path.join(BASE_DIR, "pages")


class TestCaseBase(unittest.TestCase):

    def read_page(self, page_name, encoding="utf-8"):
        """Reads HTML page located in pages folder
        and returns its content"""
        full_path = os.path.join(PAGES_DIR, page_name)
        with open(full_path, "r", encoding=encoding) as f:
            return f.read()


if __name__ == '__main__':
    unittest.main()
