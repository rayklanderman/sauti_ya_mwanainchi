from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Bill, Comment

User = get_user_model()

class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.bill = Bill.objects.create(
            title='Test Bill',
            description='Test Description',
            author=self.user,
            status='public_participation'
        )
        self.comment = Comment.objects.create(
            bill=self.bill,
            author=self.user,
            text='Test Comment'
        )
        self.dashboard_url = reverse('user_dashboard')

    def test_dashboard_view_requires_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_dashboard_view_with_login(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')
        self.assertContains(response, 'Test Bill')
        self.assertContains(response, 'Test Comment')

    def test_dashboard_context_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(list(response.context['bills']), [self.bill])
        self.assertEqual(list(response.context['comments']), [self.comment])
