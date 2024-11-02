from rest_framework import serializers
from .models import Book, Customer, Loan
from datetime import date

class BookSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_loaned = serializers.SerializerMethodField()
    days_until_available = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'year_published', 'book_type', 
                 'is_active', 'image', 'image_url', 'is_loaned', 'days_until_available']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None

    def get_is_loaned(self, obj):
        return Loan.objects.filter(
            book=obj,
            is_active=True,
            return_date__isnull=True
        ).exists()

    def get_days_until_available(self, obj):
        active_loan = Loan.objects.filter(
            book=obj,
            is_active=True,
            return_date__isnull=True
        ).first()
        
        if not active_loan:
            return 0

        # Calculate days based on book type
        loan_type_days = {
            1: 10,  # Type 1 - 10 days
            2: 5,   # Type 2 - 5 days
            3: 2    # Type 3 - 2 days
        }
        max_days = loan_type_days.get(obj.book_type, 0)
        days_passed = (date.today() - active_loan.loan_date).days
        days_remaining = max_days - days_passed
        
        return max(0, days_remaining)

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    book_name = serializers.CharField(source='book.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    is_late = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['id', 'customer', 'book', 'loan_date', 'return_date', 
                 'is_active', 'book_name', 'customer_name', 'is_late']

    def get_is_late(self, obj):
        if obj.return_date or not obj.is_active:
            return False
        
        days_passed = (date.today() - obj.loan_date).days
        loan_type_days = {
            1: 10,  # Type 1 - 10 days
            2: 5,   # Type 2 - 5 days
            3: 2    # Type 3 - 2 days
        }
        max_days = loan_type_days.get(obj.book.book_type, 0)
        
        return days_passed > max_days