from django.contrib import admin 
from .models import Book, Author, BookAuthor, Borrower, BookLoan, Fine

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(BookAuthor)
admin.site.register(Borrower)
admin.site.register(BookLoan)
admin.site.register(Fine)
