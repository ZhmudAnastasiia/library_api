from django.contrib import admin
from .models import (
    Library, Author, BookCategory, Book, 
    BookAtLibrary, LoanStatus, BorrowHistory
)

class BookAtLibraryInline(admin.TabularInline):
    model = BookAtLibrary
    extra = 1

class BorrowHistoryInline(admin.TabularInline):
    model = BorrowHistory
    extra = 1

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ("library_name", "library_address")
    search_fields = ("library_name", "library_address")
    inlines = [BookAtLibraryInline]

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("author_first_name", "author_last_name", "birth_year", "date_of_death")
    search_fields = ("author_first_name", "author_last_name")


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("book_category_name",)
    search_fields = ("book_category_name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("book_title", "published_year")
    list_filter = ("categories", "authors") 
    search_fields = ("book_title", "authors__author_first_name", "authors__author_last_name")
    filter_horizontal = ("authors", "categories")
    inlines = [BookAtLibraryInline, BorrowHistoryInline]


@admin.register(LoanStatus)
class LoanStatusAdmin(admin.ModelAdmin):
    list_display = ("status_name",)
    search_fields = ("status_name",)


@admin.register(BorrowHistory)
class BorrowHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "date_loaned", "date_returned", "loan_status")
    list_filter = ("loan_status", "date_loaned", "date_returned")
    search_fields = ("user__username", "book__book_title") 