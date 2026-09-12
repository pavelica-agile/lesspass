import unittest
from unittest.mock import patch, MagicMock

from lesspass.fzf_selector import is_fzf_available, select_profile_with_fzf


class TestFzfSelector(unittest.TestCase):
    def test_is_fzf_available_true(self):
        with patch("shutil.which", return_value="/usr/bin/fzf"):
            self.assertTrue(is_fzf_available())

    def test_is_fzf_available_false(self):
        with patch("shutil.which", return_value=None):
            self.assertFalse(is_fzf_available())

    def test_select_profile_with_fzf_no_profiles(self):
        result = select_profile_with_fzf([])
        self.assertIsNone(result)

    @patch("shutil.which", return_value=None)
    def test_select_profile_with_fzf_no_fzf_installed(self, mock_which):
        profiles = [
            {"site": "github.com", "login": "user@email.com", "lowercase": True, "uppercase": True, "digits": True, "symbols": True, "length": 16, "counter": 1, "exclude": ""}
        ]
        result = select_profile_with_fzf(profiles)
        self.assertIsNone(result)

    @patch("shutil.which", return_value="/usr/bin/fzf")
    @patch("subprocess.run")
    def test_select_profile_with_fzf_user_cancelled(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        profiles = [
            {"site": "github.com", "login": "user@email.com", "lowercase": True, "uppercase": True, "digits": True, "symbols": True, "length": 16, "counter": 1, "exclude": ""}
        ]
        result = select_profile_with_fzf(profiles)
        self.assertIsNone(result)

    @patch("shutil.which", return_value="/usr/bin/fzf")
    @patch("subprocess.run")
    def test_select_profile_with_fzf_selection(self, mock_run, mock_which):
        profiles = [
            {"site": "github.com", "login": "user@email.com", "lowercase": True, "uppercase": True, "digits": True, "symbols": True, "length": 16, "counter": 1, "exclude": ""},
            {"site": "example.org", "login": "admin", "lowercase": True, "uppercase": True, "digits": True, "symbols": False, "length": 20, "counter": 1, "exclude": ""}
        ]

        # Mock fzf returning the first profile formatted
        expected_line = "github.com                     │ user@email.com            │ L:16 C:1  │ luds"
        mock_run.return_value = MagicMock(returncode=0, stdout=expected_line + "\n")

        result = select_profile_with_fzf(profiles)

        # Should return the first profile
        self.assertIsNotNone(result)
        self.assertEqual(result["site"], "github.com")

    @patch("shutil.which", return_value="/usr/bin/fzf")
    @patch("subprocess.run")
    def test_select_profile_with_fzf_keyboard_interrupt(self, mock_run, mock_which):
        mock_run.side_effect = KeyboardInterrupt()
        profiles = [
            {"site": "github.com", "login": "user@email.com", "lowercase": True, "uppercase": True, "digits": True, "symbols": True, "length": 16, "counter": 1, "exclude": ""}
        ]
        result = select_profile_with_fzf(profiles)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
