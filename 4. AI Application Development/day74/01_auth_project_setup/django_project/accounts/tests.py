import re

from django.test import Client, TestCase
from django.urls import reverse

from .models import CustomerUser


class SignupViewTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main.html')
        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertContains(response, f'href="{reverse("signup")}"')

    def test_home_page_shows_logout_link_for_authenticated_user(self):
        user = CustomerUser.objects.create_user(
            username='tester',
            password='StrongPass123!',
            nickname='테스터',
        )

        self.client.force_login(user)
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '테스터')
        self.assertContains(response, f'href="{reverse("logout")}"')

    def test_signup_page_renders(self):
        response = self.client.get(reverse('signup'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_signup_success_page_renders(self):
        response = self.client.get(reverse('signup_success'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup_success.html')

    def test_signup_creates_user(self):
        response = self.client.post(reverse('signup'), {
            'username': 'tester',
            'email': 'tester@example.com',
            'nickname': '테스터',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })

        self.assertRedirects(response, reverse('signup_success'))
        self.assertTrue(
            CustomerUser.objects.filter(
                username='tester',
                email='tester@example.com',
                nickname='테스터',
            ).exists()
        )


class AuthViewTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertIn('no-cache', response.headers['Cache-Control'])
        self.assertIn('no-store', response.headers['Cache-Control'])

    def test_login_post_passes_with_fresh_csrf_token(self):
        CustomerUser.objects.create_user(
            username='tester',
            password='StrongPass123!',
            nickname='테스터',
        )
        client = Client(enforce_csrf_checks=True)
        response = client.get(reverse('login'))
        token_match = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"',
            response.content.decode('utf-8'),
        )

        self.assertIsNotNone(token_match)
        response = client.post(reverse('login'), {
            'username': 'tester',
            'password': 'StrongPass123!',
            'csrfmiddlewaretoken': token_match.group(1),
        })

        self.assertRedirects(response, reverse('home'))

    def test_logout_redirects_home(self):
        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, reverse('home'))

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("profile")}',
        )

    def test_profile_page_renders_for_authenticated_user(self):
        user = CustomerUser.objects.create_user(
            username='tester',
            password='StrongPass123!',
            nickname='테스터',
            email='tester@example.com',
        )

        self.client.force_login(user)
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, 'tester')
        self.assertContains(response, '테스터')
        self.assertContains(response, 'tester@example.com')

    def test_password_change_requires_login(self):
        response = self.client.get(reverse('password_change'))

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("password_change")}',
        )

    def test_password_change_page_renders_for_authenticated_user(self):
        user = CustomerUser.objects.create_user(
            username='tester',
            password='StrongPass123!',
            nickname='테스터',
        )

        self.client.force_login(user)
        response = self.client.get(reverse('password_change'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_change.html')
        self.assertContains(response, '비밀번호 변경')

    def test_password_change_updates_password_and_keeps_session(self):
        user = CustomerUser.objects.create_user(
            username='tester',
            password='StrongPass123!',
            nickname='테스터',
        )

        self.client.login(username='tester', password='StrongPass123!')
        response = self.client.post(reverse('password_change'), {
            'old_password': 'StrongPass123!',
            'new_password1': 'NewStrongPass456!',
            'new_password2': 'NewStrongPass456!',
        }, follow=True)
        user.refresh_from_db()

        self.assertRedirects(response, reverse('profile'))
        self.assertTrue(user.check_password('NewStrongPass456!'))
        self.assertContains(response, '비밀번호가 성공적으로 변경되었습니다.')
        self.assertContains(response, 'tester')
