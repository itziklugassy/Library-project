from rest_framework import serializers
from .models import Book, Customer, Loan

class BookSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'year_published', 'book_type', 
                 'is_active', 'image', 'image_url']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    book_name = serializers.CharField(source='book.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'customer', 'book', 'loan_date', 'return_date', 
                 'is_active', 'book_name', 'customer_name']