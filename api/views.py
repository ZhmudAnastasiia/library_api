from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Library, Author, Book, LoanStatus, BorrowHistory, BookCategory, BookAtLibrary
from .serializers import LibrarySerializer, AuthorSerializer, BookSerializer, LoanStatusSerializer, BorrowHistorySerializer, BookCategorySerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from datetime import datetime
from rest_framework.decorators import api_view


class LoginUserView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'message': 'Login successful!',
                'access_token': access_token
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Invalid credentials!'
            }, status=status.HTTP_400_BAD_REQUEST)

def login_page(request):
    return render(request, 'api/login.html')

        
def register(request):
    return render(request, 'api/register.html')


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            print(f"User '{user.username}' registered successfully")

            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        else:
            print(f"Registration failed: {serializer.errors}")  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LibraryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        libraries = Library.objects.all()
        serializer = LibrarySerializer(libraries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LibrarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def library_list_html(request):
    return render(request, 'api/library_list.html')

def library_books_html(request, library_id):
    return render(request, 'api/library_book.html', {'library_id': library_id})

class LibraryBookListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, library_id):
        try:
            library = Library.objects.get(id=library_id)
            books = Book.objects.filter(libraries=library)
            serializer = BookSerializer(books, many=True)
            return Response(serializer.data)

        except Library.DoesNotExist:
            return Response({"detail": "Library not found."}, status=status.HTTP_404_NOT_FOUND)

class AddBookView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_book(request, library_id):
    try:
        library = Library.objects.get(id=library_id)
    except Library.DoesNotExist:
        return Response({"detail": "Бібліотеку не знайдено."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        serializer = BookSerializer(data=request.data)

        if serializer.is_valid():
            book = serializer.save()
            BookAtLibrary.objects.create(library=library, book=book)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BorrowHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        borrow_history = BorrowHistory.objects.filter(user=request.user)
        serializer = BorrowHistorySerializer(borrow_history, many=True)
        return Response(serializer.data)


class BorrowHistoryCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)

            loan_status = LoanStatus.objects.first()
            user = request.user

            current_date = datetime.now().date()

            borrow_history = BorrowHistory.objects.create(
                book=book,
                user=user,
                loan_status=loan_status,
                date_loaned=current_date,
                date_returned=request.data.get('date_returned', None)
            )

            serializer = BorrowHistorySerializer(borrow_history)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, borrow_id):
        try:
            borrow_record = BorrowHistory.objects.get(id=borrow_id)

            if borrow_record.date_returned is None:
                borrow_record.date_returned = datetime.now().date()  
                borrow_record.save()
                return Response({'message': 'Книга успішно повернена!'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Книга вже повернена!'}, status=status.HTTP_400_BAD_REQUEST)

        except BorrowHistory.DoesNotExist:
            return Response({'message': 'Запис не знайдений!'}, status=status.HTTP_404_NOT_FOUND)

def borrow_history_html(request):
    if not request.user.is_authenticated:
        return render(request, 'api/borrow_history.html', {'error': 'Authentication required'})

    borrow_history = BorrowHistory.objects.filter(user=request.user)

    return render(request, 'api/borrow_history.html', {'borrow_history': borrow_history})

class AuthorListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthorDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AuthorSerializer(author, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        author.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# В'юшки для моделі Book
class BookListView(APIView):
    
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
# В'юшки для моделі LoanStatus
class LoanStatusListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        statuses = LoanStatus.objects.all()
        serializer = LoanStatusSerializer(statuses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LoanStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoanStatusDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            status = LoanStatus.objects.get(pk=pk)
        except LoanStatus.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LoanStatusSerializer(status)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            status = LoanStatus.objects.get(pk=pk)
        except LoanStatus.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LoanStatusSerializer(status, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            status = LoanStatus.objects.get(pk=pk)
        except LoanStatus.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        status.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BorrowHistoryDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            history = BorrowHistory.objects.get(pk=pk)
        except BorrowHistory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BorrowHistorySerializer(history)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            history = BorrowHistory.objects.get(pk=pk)
        except BorrowHistory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BorrowHistorySerializer(history, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            history = BorrowHistory.objects.get(pk=pk)
        except BorrowHistory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        history.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# В'юшки для моделі BookCategory
class BookCategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        categories = BookCategory.objects.all()
        serializer = BookCategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookCategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            category = BookCategory.objects.get(pk=pk)
        except BookCategory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookCategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            category = BookCategory.objects.get(pk=pk)
        except BookCategory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            category = BookCategory.objects.get(pk=pk)
        except BookCategory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


