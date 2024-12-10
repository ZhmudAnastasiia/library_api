from .models import Library, Author, Book, LoanStatus, BorrowHistory, BookCategory, BookAtLibrary
from django.contrib.auth.models import User
from rest_framework import serializers, generics
from rest_framework.exceptions import ValidationError

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = ['id', 'library_name', 'library_address']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'author_first_name', 'author_last_name', 'birth_year', 'date_of_death']

class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = ['id', 'book_category_name']

class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    categories = BookCategorySerializer(many=True, read_only=True)
    authors_input = serializers.ListField(child=serializers.CharField(), write_only=True)
    categories_input = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = Book
        fields = ['id', 'book_title', 'published_year', 'authors', 'categories', 'authors_input', 'categories_input']

    def create(self, validated_data):
        authors_data = validated_data.pop('authors_input', [])
        categories_data = validated_data.pop('categories_input', [])

        book = Book.objects.create(**validated_data)

        for author_name in authors_data:
            first_name, last_name = author_name.split(" ", 1)
            try:
                author = Author.objects.get(author_first_name=first_name, author_last_name=last_name)
            except Author.DoesNotExist:
                raise ValidationError(f"Автор {author_name} не знайдений в базі даних.")
            book.authors.add(author)

        for category_name in categories_data:
            try:
                category = BookCategory.objects.get(book_category_name=category_name)
            except BookCategory.DoesNotExist:
                raise ValidationError(f"Категорія {category_name} не знайдена в базі даних.")
            book.categories.add(category)

        return book

class LoanStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanStatus
        fields = ['id', 'status_name']

class BorrowHistorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    book = BookSerializer()
    loan_status = LoanStatusSerializer()

    class Meta:
        model = BorrowHistory
        fields = ['id', 'date_loaned', 'date_returned', 'user', 'book', 'loan_status']

class BookAtLibrarySerializer(serializers.ModelSerializer):
    library = LibrarySerializer()
    book = BookSerializer()

    class Meta:
        model = BookAtLibrary
        fields = ['id', 'library', 'book', 'book_quantity']

