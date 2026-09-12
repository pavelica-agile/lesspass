import os
import tempfile
import unittest

from lesspass.csv_storage import (
    load_profiles,
    search_profiles,
    format_profile_display,
)
from lesspass.password import generate_password


class TestCSVStorage(unittest.TestCase):
    def setUp(self):
        # Create a temporary CSV file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        self.temp_file.write("site,login,lowercase,uppercase,digits,symbols,length,counter,exclude\n")
        self.temp_file.write("github.com,user@email.com,true,true,true,true,16,1,\n")
        self.temp_file.write("example.org,admin,true,true,true,false,20,1,\n")
        self.temp_file.write("bank.com,myaccount,true,true,true,true,24,1,!@#\n")
        self.temp_file.write("github.work.com,work@company.com,true,true,true,true,16,2,\n")
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_load_profiles(self):
        profiles = load_profiles(self.temp_file.name)
        self.assertEqual(len(profiles), 4)

    def test_load_profiles_nonexistent_file(self):
        profiles = load_profiles("/nonexistent/file.csv")
        self.assertEqual(profiles, [])

    def test_profile_structure(self):
        profiles = load_profiles(self.temp_file.name)
        profile = profiles[0]

        self.assertEqual(profile["site"], "github.com")
        self.assertEqual(profile["login"], "user@email.com")
        self.assertTrue(profile["lowercase"])
        self.assertTrue(profile["uppercase"])
        self.assertTrue(profile["digits"])
        self.assertTrue(profile["symbols"])
        self.assertEqual(profile["length"], 16)
        self.assertEqual(profile["counter"], 1)
        self.assertEqual(profile["exclude"], "")

    def test_profile_with_exclude(self):
        profiles = load_profiles(self.temp_file.name)
        bank_profile = profiles[2]
        self.assertEqual(bank_profile["site"], "bank.com")
        self.assertEqual(bank_profile["exclude"], "!@#")

    def test_profile_no_symbols(self):
        profiles = load_profiles(self.temp_file.name)
        example_profile = profiles[1]
        self.assertEqual(example_profile["site"], "example.org")
        self.assertFalse(example_profile["symbols"])

    def test_search_profiles_single_match(self):
        matches = search_profiles(self.temp_file.name, "bank")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["site"], "bank.com")

    def test_search_profiles_multiple_matches(self):
        matches = search_profiles(self.temp_file.name, "github")
        self.assertEqual(len(matches), 2)
        sites = [m["site"] for m in matches]
        self.assertIn("github.com", sites)
        self.assertIn("github.work.com", sites)

    def test_search_profiles_no_match(self):
        matches = search_profiles(self.temp_file.name, "nonexistent")
        self.assertEqual(len(matches), 0)

    def test_search_profiles_case_insensitive(self):
        matches = search_profiles(self.temp_file.name, "GITHUB")
        self.assertEqual(len(matches), 2)

    def test_search_profiles_empty_pattern(self):
        matches = search_profiles(self.temp_file.name, "")
        self.assertEqual(len(matches), 4)

    def test_format_profile_display(self):
        profiles = load_profiles(self.temp_file.name)
        display = format_profile_display(profiles[0])

        self.assertIn("github.com", display)
        self.assertIn("user@email.com", display)
        self.assertIn("L:16", display)
        self.assertIn("C:1", display)
        self.assertIn("luds", display)  # lowercase, uppercase, digits, symbols

    def test_format_profile_display_no_symbols(self):
        profiles = load_profiles(self.temp_file.name)
        display = format_profile_display(profiles[1])

        self.assertIn("lud", display)  # lowercase, uppercase, digits (no symbols)
        self.assertNotIn("luds", display)

    def test_format_profile_display_with_exclude(self):
        profiles = load_profiles(self.temp_file.name)
        display = format_profile_display(profiles[2])

        self.assertIn("exclude:!@#", display)

    def test_password_generation_from_profile(self):
        profiles = load_profiles(self.temp_file.name)
        profile = profiles[0]
        password = generate_password(profile, "testmaster123")

        # Password should be generated and match expected length
        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, str)

    def test_password_consistency(self):
        # Same profile + same master password should always generate same password
        profiles = load_profiles(self.temp_file.name)
        profile = profiles[0]
        master = "testmaster123"

        password1 = generate_password(profile, master)
        password2 = generate_password(profile, master)

        self.assertEqual(password1, password2)

    def test_password_different_counter(self):
        # Different counter should generate different password
        profiles = load_profiles(self.temp_file.name)
        profile1 = profiles[0]  # counter = 1
        profile2 = profiles[3]  # counter = 2
        master = "testmaster123"

        # Make profiles identical except counter
        profile2["site"] = profile1["site"]
        profile2["login"] = profile1["login"]
        profile2["length"] = profile1["length"]
        profile2["lowercase"] = profile1["lowercase"]
        profile2["uppercase"] = profile1["uppercase"]
        profile2["digits"] = profile1["digits"]
        profile2["symbols"] = profile1["symbols"]
        profile2["exclude"] = profile1["exclude"]

        password1 = generate_password(profile1, master)
        password2 = generate_password(profile2, master)

        self.assertNotEqual(password1, password2)


if __name__ == "__main__":
    unittest.main()
