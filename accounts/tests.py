import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Profile

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
    def test_profile_creation(self):
        """Test that a profile is automatically created when a user is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)
        
    def test_profile_str_representation(self):
        """Test the string representation of a profile."""
        expected = f"{self.user.username}'s profile"
        self.assertEqual(str(self.user.profile), expected)
        
    def test_profile_fields(self):
        """Test that profile fields can be updated."""
        profile = self.user.profile
        profile.bio = "This is a test bio."
        profile.website = "https://example.com"
        profile.social_github = "https://github.com/testuser"
        profile.save()
        
        # Refresh from database
        profile.refresh_from_db()
        
        self.assertEqual(profile.bio, "This is a test bio.")
        self.assertEqual(profile.website, "https://example.com")
        self.assertEqual(profile.social_github, "https://github.com/testuser")

if __name__ == '__main__':
    unittest.main()
