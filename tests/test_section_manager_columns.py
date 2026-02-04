import unittest

from test_section_manager_ui import test_treeview_columns


class TestSectionManagerColumns(unittest.TestCase):
    def test_treeview_columns_function(self):
        """Invoke the existing test helper and assert it returns True."""
        result = test_treeview_columns()
        assert result is True


if __name__ == "__main__":
    unittest.main()
