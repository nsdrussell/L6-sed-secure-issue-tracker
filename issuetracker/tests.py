from django.test import TestCase
from datetime import datetime, timedelta
from django.utils import timezone
from .models import User, Category, Issue, Comment
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            password="test_password",
            nickname="Test User",
            is_admin=False,
            change_password_after=datetime.now(timezone.utc) + timedelta(days=30),
            datetime_created=datetime.now(timezone.utc),
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "test_user")
        self.assertEqual(self.user.password, "test_password")
        self.assertEqual(self.user.nickname, "Test User")
        self.assertFalse(self.user.is_admin)
        self.assertTrue(self.user.change_password_after > datetime.now(timezone.utc))

    def test_user_is_admin_checkbox(self):
        self.assertEqual(self.user.is_admin_checkbox(), "")

        admin_user = User.objects.create(
            username="admin_user",
            password="admin_password",
            nickname="Admin User",
            is_admin=True,
            change_password_after=datetime.now(timezone.utc),
            datetime_created=datetime.now(timezone.utc),
        )

        self.assertEqual(admin_user.is_admin_checkbox(), "checked")


class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            password="test_password",
            nickname="Test User",
            is_admin=False,
            change_password_after=datetime.now(timezone.utc) + timedelta(days=30),
            datetime_created=datetime.now(timezone.utc),
        )
        self.category = Category.objects.create(
            name="Test Category",
            author=self.user,
            datetime_created=datetime.now(timezone.utc),
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.author, self.user)


class IssueModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            password="test_password",
            nickname="Test User",
            is_admin=False,
            change_password_after=datetime.now(timezone.utc) + timedelta(days=30),
            datetime_created=datetime.now(timezone.utc),
        )
        self.category = Category.objects.create(
            name="Test Category",
            author=self.user,
            datetime_created=datetime.now(timezone.utc),
        )
        self.issue = Issue.objects.create(
            title="Test Issue",
            parent_category=self.category,
            description="Test Issue Description",
            author=self.user,
            datetime_created=datetime.now(timezone.utc),
        )

    def test_issue_creation(self):
        self.assertEqual(self.issue.title, "Test Issue")
        self.assertEqual(self.issue.parent_category, self.category)
        self.assertEqual(self.issue.description, "Test Issue Description")
        self.assertEqual(self.issue.author, self.user)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            password="test_password",
            nickname="Test User",
            is_admin=False,
            change_password_after=datetime.now(timezone.utc) + timedelta(days=30),
            datetime_created=datetime.now(timezone.utc),
        )
        self.category = Category.objects.create(
            name="Test Category",
            author=self.user,
            datetime_created=datetime.now(timezone.utc),
        )
        self.issue = Issue.objects.create(
            title="Test Issue",
            parent_category=self.category,
            description="Test Issue Description",
            author=self.user,
            datetime_created=datetime.now(timezone.utc),
        )
        self.comment = Comment.objects.create(
            parent_issue=self.issue,
            text="Test Comment",
            author=self.user,
            datetime_created=datetime.now(timezone.utc),
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.parent_issue, self.issue)
        self.assertEqual(self.comment.text, "Test Comment")
        self.assertEqual(self.comment.author, self.user)

    def test_get_title_and_text(self):
        expected_text = f'Issue: {self.issue.title}\r\n>\r\nComment: Test Comment'
        self.assertEqual(self.comment.get_title_and_text(), expected_text)





class ViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            password=make_password("test_password"),
            nickname="Test User",
            is_admin=False,
            change_password_after=datetime.now(timezone.utc) + timedelta(days=30),
            datetime_created=datetime.now(timezone.utc),
        )

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")

        # Test user registration
        data = {
            'username': 'new_user',
            'password': 'NewPassword1!',
            'confirm_password': 'NewPassword1!',
            'is_admin': False,
            'nickname': 'New User',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertEqual(User.objects.count(), 2)  # Two users in total now

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")

        # Test user login
        data = {
            'username': 'test_user',
            'password': 'test_password',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page after logout

