from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    isbn = models.CharField(primary_key=True, max_length=20)
    title = models.CharField(max_length=255)
    
    def __str__(self):
        return self.title
    
class Author(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
class BookAuthor(models.Model):
    isbn = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    
    class Meta:
        unique_together=('isbn','author')
        
class Borrower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    card_id = models.AutoField(primary_key=True)
    bname = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    ssn = models.CharField(max_length=11, unique=True)
    
    def __str__(self):
        return f"{self.bname} ({self.card_id})"
    
class BookLoan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    isbn = models.ForeignKey(Book, on_delete=models.CASCADE)
    card_id = models.ForeignKey(Borrower, on_delete=models.CASCADE)
    date_out = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    date_in = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Loan {self.loan_id} - {self.isbn} to {self.card_id}"

class Fine(models.Model):
    loan_id = models.OneToOneField('BookLoan', on_delete=models.CASCADE, primary_key=True)
    fine_amt = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Fine for loan {self.loan_id_id}: ${self.fine_amt} Paid: {self.paid}"