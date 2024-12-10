from django.urls import path
from . import views
from .views import LoginUserView

urlpatterns = [
    path('api/register/', views.RegisterUserView.as_view(), name='register-api'),
    path('register/', views.register, name='register'),
    path('api/login/', LoginUserView.as_view(), name='login-api'),
    path('login/', views.login_page, name='login_page'),
    path('libraries/<int:library_id>/books/', views.library_books_html, name='library-books'),
    path('api/libraries/<int:library_id>/books/', views.LibraryBookListView.as_view(), name='library-books-api'),
    path('<int:library_id>/add-book/', views.add_book, name='add_book'),
   
    path('user/borrow-history/', views.BorrowHistoryListView.as_view(), name='user_borrow_history'),
    path('user/borrow-history/<int:book_id>/', views.BorrowHistoryCreateView.as_view(), name='user_borrow_history_create'),
    path('borrow-history/', views.borrow_history_html, name='borrow_history_html'),
    path('borrow-history/<int:borrow_id>/return/', views.ReturnBookView.as_view(), name='return_book'),

    path('libraries/', views.library_list_html, name='library_list_html'),
    path('api/libraries/', views.LibraryListView.as_view(), name='library_list_api'),

    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),

    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),


    path('loan-status/', views.LoanStatusListView.as_view(), name='loan-status-list'),
    path('loan-status/<int:pk>/', views.LoanStatusDetailView.as_view(), name='loan-status-detail'),

    path('borrow_history/', views.BorrowHistoryListView.as_view(), name='borrow_history_list'),
    path('borrow-history/<int:pk>/', views.BorrowHistoryDetailView.as_view(), name='borrow-history-detail'),

    path('book-categories/', views.BookCategoryListView.as_view(), name='book-category-list'),
    path('book-categories/<int:pk>/', views.BookCategoryDetailView.as_view(), name='book-category-detail'),
]
