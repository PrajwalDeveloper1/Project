import unittest

from app import normalize_phone


class NormalizePhoneTests(unittest.TestCase):
    def test_valid_phone_format(self):
        self.assertEqual(normalize_phone("+91", "9876543210"), "+91 987 654 3210")

    def test_valid_phone_with_common_separators_and_leading_one(self):
        self.assertEqual(normalize_phone("+1", "1 (987) 654-3210"), "+1 987 654 3210")
        self.assertEqual(normalize_phone("+1", "987 654 3210"), "+1 987 654 3210")

    def test_invalid_phone_length_raises(self):
        with self.assertRaises(ValueError):
            normalize_phone("+1", "12345")

    def test_invalid_non_digits_raises(self):
        with self.assertRaises(ValueError):
            normalize_phone("+44", "abc-def-ghij")


if __name__ == "__main__":
    unittest.main()
