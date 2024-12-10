from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.urls import reverse
from .models import Library, Author, BookCategory

class LibraryListViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")

        self.token = Token.objects.create(user=self.user)

        self.libraries_url = reverse('library_list_api')

    def test_get_libraries(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.get(self.libraries_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_post_valid_library(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        valid_payload = {"library_name": "Library Name", "library_address": "Library Location"}
        response = self.client.post(self.libraries_url, data=valid_payload)

        if response.status_code != status.HTTP_201_CREATED:
            print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_post_invalid_library(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        invalid_payload = {"name": "", "location": ""}
        response = self.client.post(self.libraries_url, data=invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AddBookTestCase(APITestCase):
    def setUp(self):
        self.library = Library.objects.create(library_name="Test Library", library_address="123 Test St")
        self.author = Author.objects.create(author_first_name="John", author_last_name="Doe")
        self.category = BookCategory.objects.create(book_category_name="Fiction")

        self.user = User.objects.create_user(username="testuser", password="testpassword")

        self.token = Token.objects.create(user=self.user)

        self.client = APIClient()

        self.url = reverse('add_book', args=[self.library.id])
        
    def test_add_book_invalid_library(self):
        self.client.force_authenticate(user=self.user, token=self.token)

        invalid_library_id = 9999
        invalid_url = reverse('add_book', args=[invalid_library_id])

        data = {
            'book_title': 'Test Book',
            'published_year': 2024,
            'authors_input': ['John Doe'],
            'categories_input': ['Fiction']
            }

        response = self.client.post(invalid_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_add_book_invalid_data(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        
        data = {
            'book_title': '',
            'published_year': 2024,
            'authors_input': ['John Doe'],
            'categories_input': ['Fiction']
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_book_non_existent_author(self):
        self.client.force_authenticate(user=self.user, token=self.token)

        data = {
            'book_title': 'Test Book',
            'published_year': 2024,
            'authors_input': ['Non Existent Author'],
            'categories_input': ['Fiction']
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_book_non_existent_category(self):
        self.client.force_authenticate(user=self.user, token=self.token)

        data = {
            'book_title': 'Test Book',
            'published_year': 2024,
            'authors_input': ['John Doe'],
            'categories_input': ['Non Existent Category']
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
