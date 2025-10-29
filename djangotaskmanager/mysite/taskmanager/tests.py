from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from taskmanager.views import (
    RegisterView,
    ProjectCreateView,
    ProjectListView,
    ProjectDetailView,
    ProjectUpdateView,
)

# Create your tests here.
# class RegisterViewTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.register_url = reverse('register')
#         self.dashboard_url = reverse('dashboard')
#         self.valid_data = {
#             'username': 'testuser12345',
#             'password1': 'testpassword123456789',
#             'password2': 'testpassword123456789'
#         }
#     def 