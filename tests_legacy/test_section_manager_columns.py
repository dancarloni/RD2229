import unittest

from test_section_manager_ui import test_treeview_columns


class TestSectionManagerColumns(unittest.TestCase):
    def test_treeview_columns_function(self):
        """Invoke the existing test helper; it should not raise exceptions."""
        test_treeview_columns()


if __name__ == "__main__":
    unittest.main()
