from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookViewSet, 
    CustomerViewSet, 
    LoanViewSet, 
    register_user, 
    get_user_info
)

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'loans', LoanViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_user, name='register'),
    path('users/me/', get_user_info, name='user-info'),
]