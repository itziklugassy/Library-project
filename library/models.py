from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Book(models.Model):
    BOOK_TYPES = (
        (1, 'Type 1 - 10 days'),
        (2, 'Type 2 - 5 days'),
        (3, 'Type 3 - 2 days'),
    )
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    year_published = models.IntegerField()
    book_type = models.IntegerField(choices=BOOK_TYPES)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='books/', null=True, blank=True)  # Add this line

    def __str__(self):
        return f"{self.name} by {self.author}"

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    age = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    loan_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def is_late(self):
        if not self.return_date and self.is_active:
            days_passed = (timezone.now().date() - self.loan_date).days
            if self.book.book_type == 1:
                return days_passed > 10
            elif self.book.book_type == 2:
                return days_passed > 5
            elif self.book.book_type == 3:
                return days_passed > 2
        return False

    def __str__(self):
        return f"{self.customer.name} - {self.book.name}"