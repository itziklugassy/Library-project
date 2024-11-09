
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User
from .models import Book, Customer, Loan
from .serializers import BookSerializer, CustomerSerializer, LoanSerializer
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
@api_view(['POST'])

@permission_classes([AllowAny])
def register_user(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        name = request.data.get('name')
        city = request.data.get('city')
        age = request.data.get('age')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Create regular user
        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=False,
            is_superuser=False
        )
        
        # Create customer profile
        customer = Customer.objects.create(
            user=user,
            name=name,
            city=city,
            age=age,
            is_active=True
        )
        
        return Response({
            'message': 'Registration successful',
            'username': username,
            'customer_id': customer.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(str(e))
        return Response(
            {'error': 'Registration failed'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    try:
        customer = Customer.objects.get(user=request.user)
        return Response({
            'username': request.user.username,
            'is_staff': request.user.is_staff,
            'customer_id': customer.id,
            'name': customer.name,
            'city': customer.city
        })
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.filter(is_active=True)
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Changed to AllowAny to allow public book viewing
  

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=False, methods=['get'])
    def search(self, request):
        name = request.query_params.get('name', '')
        books = self.queryset.filter(name__icontains=name)
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.filter(is_active=True)
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]  # Only admin can manage customers

    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.filter(is_active=True)
        return Customer.objects.none()

    @action(detail=False, methods=['get'])
    def search(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "Not authorized"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        name = request.query_params.get('name', '')
        customers = self.queryset.filter(name__icontains=name)
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        if self.request.user.is_staff:
            return Loan.objects.all()
        try:
            customer = Customer.objects.get(user=self.request.user)
            return Loan.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            return Loan.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            # Get the customer making the loan
            customer = Customer.objects.get(user=request.user)
            book_id = request.data.get('book')
            book = Book.objects.get(id=book_id)

            # Check if book is already loaned
            if Loan.objects.filter(book=book, is_active=True).exists():
                return Response(
                    {'error': 'This book is already loaned'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if customer has too many active loans (optional)
            active_loans = Loan.objects.filter(
                customer=customer,
                is_active=True
            ).count()
            if active_loans >= 5:  # Limit to 5 active loans per customer
                return Response(
                    {'error': 'Maximum active loans reached'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the loan
            loan = Loan.objects.create(
                customer=customer,
                book=book,
                loan_date=timezone.now().date(),
                is_active=True
            )

            serializer = self.get_serializer(loan)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def late_loans(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "Not authorized"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        loans = self.get_queryset().filter(
            return_date__isnull=True,
            is_active=True
        )
        late_loans = [loan for loan in loans if loan.is_late()]
        serializer = self.get_serializer(late_loans, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        loan = self.get_object()
        if not (request.user.is_staff or loan.customer.user == request.user):
            return Response(
                {"error": "Not authorized"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if not loan.is_active:
            return Response(
                {"error": "Book already returned"},
                status=status.HTTP_400_BAD_REQUEST
            )

        loan.return_date = date.today()
        loan.is_active = False
        loan.save()

        return Response({
            'status': 'success',
            'message': 'Book returned successfully'
        })

    @action(detail=True, methods=['get'])
    def loan_details(self, request, pk=None):
        loan = self.get_object()
        if not (request.user.is_staff or loan.customer.user == request.user):
            return Response(
                {"error": "Not authorized"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(loan)
        return Response(serializer.data)