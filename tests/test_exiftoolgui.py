import unittest
import subprocess
from unittest.mock import patch, MagicMock
from exiftoolgui.exiftoolgui import ExifToolGUI
class TestExifToolGUI(unittest.TestCase):
    @patch('subprocess.run')
    def setUp(self, mock_run):
        mock_run.return_value.stdout = "12.34\n"
        mock_run.return_value.returncode = 0

        self.mock_tk = MagicMock()
        self.mock_ttk = MagicMock()
        self.mock_filedialog = MagicMock()
        self.mock_messagebox = MagicMock()
        self.mock_scrolledtext = MagicMock()

        self.module_patcher = patch.multiple(
            'exiftoolgui.exiftoolgui',
            tk=self.mock_tk,
            ttk=self.mock_ttk,
            filedialog=self.mock_filedialog,
            messagebox=self.mock_messagebox,
            scrolledtext=self.mock_scrolledtext
        )
        self.module_patcher.start()

        self.mock_string_var = MagicMock()
        self.app = ExifToolGUI(master=MagicMock(), string_var_class=self.mock_string_var)

    def tearDown(self):
        self.module_patcher.stop()

    def test_check_exiftool(self):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = "12.34\n"
            mock_run.return_value.returncode = 0
            version = ExifToolGUI.check_exiftool()
            self.assertEqual(version, "12.34")

        with patch('subprocess.run', side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                ExifToolGUI.check_exiftool()

        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'exiftool')):
            with self.assertRaises(RuntimeError):
                ExifToolGUI.check_exiftool()

    @patch('subprocess.run')
    def test_run_exiftool(self, mock_run):
        mock_run.return_value.stdout = "Test output"
        result = self.app.run_exiftool(["test.jpg"])
        self.assertEqual(result, "Test output")
        mock_run.assert_called_with(['exiftool', "test.jpg"], capture_output=True, text=True, check=True)


    def test_pretty_print_json(self):
        input_text = 'Tag1: {"key": "value"}\nTag2: Not JSON'
        expected_output = 'Tag1:\n{\n  "key": "value"\n}\nTag2: Not JSON'
        result = self.app.pretty_print_json(input_text)
        self.assertEqual(result, expected_output)

    def test_browse_file(self):
        self.mock_filedialog.askopenfilename.return_value = "test.jpg"
        with patch.object(self.app, 'run_exiftool', return_value="EXIF data"):
            self.app.browse_file()
            self.assertEqual(self.app.current_file, "test.jpg")
            self.app.run_exiftool.assert_called_once_with(["test.jpg"])

    def test_apply_edit(self):
        self.app.current_file = "test.jpg"
        self.app.tag_entry = MagicMock()
        self.app.tag_entry.get.return_value = "TestTag"
        self.app.value_entry = MagicMock()
        self.app.value_entry.get.return_value = "TestValue"
        with patch.object(self.app, 'run_exiftool'):
            self.app.apply_edit()
            self.app.run_exiftool.assert_called_once_with(['-TestTag=TestValue', 'test.jpg'])

        # Test error when no file is selected
        self.app.current_file = None
        self.app.apply_edit()
        self.mock_messagebox.showerror.assert_called_once_with("Error", "No image selected")

    def test_select_image_for_edit(self):
        self.mock_filedialog.askopenfilename.return_value = "test.jpg"
        self.app.select_image_for_edit()
        self.assertEqual(self.app.current_file, "test.jpg")

    def test_select_image_for_remove(self):
        self.mock_filedialog.askopenfilename.return_value = "test.jpg"
        self.app.select_image_for_remove()
        self.assertEqual(self.app.current_file, "test.jpg")

    def test_remove_all_exif(self):
        self.app.current_file = "test.jpg"
        with patch.object(self.app, 'run_exiftool'):
            self.app.remove_all_exif()
            self.app.run_exiftool.assert_called_once_with(['-all=', '-overwrite_original', 'test.jpg'])

        # Test error when no file is selected
        self.app.current_file = None
        self.app.remove_all_exif()
        self.mock_messagebox.showerror.assert_called_once_with("Error", "No image selected")

    def test_select_directory(self):
        self.mock_filedialog.askdirectory.return_value = "/test/directory"
        self.app.select_directory()
        self.assertEqual(self.app.batch_directory, "/test/directory")

    def test_batch_process(self):
        self.app.batch_directory = "/test/directory"
        self.app.batch_operation = MagicMock()
        self.app.batch_operation.get.return_value = "view"
        with patch.object(self.app, 'run_exiftool', return_value="EXIF data"):
            self.app.batch_process()
            self.app.run_exiftool.assert_called_once_with(['-recurse', '/test/directory'])

        self.app.batch_operation.get.return_value = "remove"
        with patch.object(self.app, 'run_exiftool'):
            self.app.batch_process()
            self.app.run_exiftool.assert_called_once_with(['-all=', '-overwrite_original', '-recurse', '/test/directory'])

        # Test error when no directory is selected
        self.app.batch_directory = None
        self.app.batch_process()
        self.mock_messagebox.showerror.assert_called_once_with("Error", "No directory selected")

if __name__ == '__main__':
    unittest.main()
