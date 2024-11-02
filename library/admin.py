from django.contrib import admin
from .models import Book, Customer, Loan

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'year_published', 'book_type', 'is_active')
    search_fields = ('name', 'author')
    list_filter = ('book_type', 'is_active')
    # Remove the fields line and let Django automatically handle the form fields

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'age', 'is_active')
    search_fields = ('name', 'city')
    list_filter = ('is_active',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('customer', 'book', 'loan_date', 'return_date', 'is_active')
    list_filter = ('is_active', 'loan_date', 'return_date')
    search_fields = ('customer__name', 'book__name')