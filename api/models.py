from django.db import models
from django.contrib.auth.models import User

class Library(models.Model):
    library_name = models.CharField(max_length=45)
    library_address = models.CharField(max_length=45)                   
    
    def __str__(self):
        return self.library_name

class Author(models.Model):
    author_first_name = models.CharField(max_length=100, null=False, default="Unknown")
    author_last_name = models.CharField(max_length=100, null=False, default="Unknown")
    birth_year = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.author_first_name} {self.author_last_name}"


class BookCategory(models.Model):
    book_category_name = models.CharField(max_length=45)

    def __str__(self):
        return self.book_category_name


class Book(models.Model):
    book_title = models.CharField(max_length=45)
    published_year = models.DateField(null=True, blank=True)
    authors = models.ManyToManyField(Author, related_name="books")  
    categories = models.ManyToManyField(BookCategory, related_name="books") 
    libraries = models.ManyToManyField(Library, through="BookAtLibrary")  

    def __str__(self):
        return self.book_title


class BookAtLibrary(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    book_quantity = models.IntegerField(default=0)


class LoanStatus(models.Model):
    status_name = models.CharField(max_length=45)

    def __str__(self):
        return self.status_name
    


class BorrowHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    date_loaned = models.DateField(null=True, blank=True)
    date_returned = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    loan_status = models.ForeignKey(LoanStatus, on_delete=models.CASCADE)

    def __str__(self):
        return f"Loan record for {self.user} - {self.book}"


