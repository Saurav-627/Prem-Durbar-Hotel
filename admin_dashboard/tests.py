from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from payments.models.payment_processor import PaymentProcessor
from settings_manager.models.currency import Currency

User = get_user_model()

class DashboardAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a standard user and a staff user
        # pyrefly: ignore [missing-attribute]
        self.user = User.objects.create_user(
            username='guestuser', 
            password='guestpassword',
            email='guest@example.com',
            is_staff=False,
            is_superuser=False
        )
        # pyrefly: ignore [missing-attribute]
        self.staff_user = User.objects.create_user(
            username='staffuser', 
            password='staffpassword',
            email='staff@example.com',
            is_staff=True,
            is_superuser=False
        )

    def test_anonymous_redirect(self):
        """Anonymous user trying to access /admin/ should redirect to login."""
        response = self.client.get(reverse('admin_dashboard:home'))
        # pyrefly: ignore [missing-attribute]
        self.assertEqual(response.status_code, 302)
        # pyrefly: ignore [missing-attribute]
        self.assertIn(reverse('admin_dashboard:login'), response.url)

    def test_non_staff_denied(self):
        """Non-staff authenticated user should get PermissionDenied (403)."""
        self.client.login(username='guestuser', password='guestpassword')
        response = self.client.get(reverse('admin_dashboard:home'))
        # pyrefly: ignore [missing-attribute]
        self.assertEqual(response.status_code, 403)

    def test_staff_access_granted(self):
        """Staff/superuser authenticated user should access /admin/ home successfully (200)."""
        self.client.login(username='staffuser', password='staffpassword')
        response = self.client.get(reverse('admin_dashboard:home'))
        # pyrefly: ignore [missing-attribute]
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard/home.html')

    def test_login_page_renders(self):
        """Login page should load successfully (200) for anonymous user."""
        response = self.client.get(reverse('admin_dashboard:login'))
        # pyrefly: ignore [missing-attribute]
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard/login.html')


class PaymentProcessorTests(TestCase):
    def setUp(self):
        self.client = Client()
        # pyrefly: ignore [missing-attribute]
        self.staff_user = get_user_model().objects.create_user(
            username='staffuser', 
            password='staffpassword',
            email='staff@example.com',
            is_staff=True
        )
        self.client.login(username='staffuser', password='staffpassword')
        
        # Ensure we have active currencies
        self.usd = Currency.objects.create(name="US Dollar", iso_code="USD", symbol="$", is_published=True, sequence=1)
        self.npr = Currency.objects.create(name="Nepalese Rupee", iso_code="NPR", symbol="Rs.", is_published=True, sequence=2)

    def test_settings_processors_context(self):
        """Settings page should render processors context tab successfully."""
        response = self.client.get(reverse('admin_dashboard:settings_dashboard') + "?tab=processors")
        self.assertEqual(response.status_code, 200)
        self.assertIn('processors', response.context)

    def test_payment_processor_crud(self):
        """Test payment processor CRUD flow."""
        # 1. Create
        create_url = reverse('admin_dashboard:processor_create')
        data = {
            'name': 'Stripe Gateway',
            'code': 'stripe',
            'apply_tax': True,
            'is_published': True,
            'payment_currencies': [self.usd.id, self.npr.id]
        }
        response = self.client.post(create_url, data)
        self.assertEqual(response.status_code, 302) # Redirects to settings list
        
        processor = PaymentProcessor.objects.filter(code='stripe').first()
        self.assertIsNotNone(processor)
        self.assertEqual(processor.name, 'Stripe Gateway')
        self.assertTrue(processor.apply_tax)
        self.assertTrue(processor.is_published)
        self.assertEqual(processor.payment_currencies.count(), 2)

        # 2. Update
        update_url = reverse('admin_dashboard:processor_edit', args=[processor.id])
        data = {
            'name': 'Updated Stripe',
            'code': 'stripe',
            'apply_tax': False,
            'is_published': False,
            'payment_currencies': [self.usd.id]
        }
        response = self.client.post(update_url, data)
        self.assertEqual(response.status_code, 302)
        
        processor.refresh_from_db()
        self.assertEqual(processor.name, 'Updated Stripe')
        self.assertFalse(processor.apply_tax)
        self.assertFalse(processor.is_published)
        self.assertEqual(processor.payment_currencies.count(), 1)
        self.assertEqual(processor.payment_currencies.first(), self.usd)

        # 3. Delete
        delete_url = reverse('admin_dashboard:processor_delete', args=[processor.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(PaymentProcessor.objects.filter(code='stripe').first())
