from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        "endpoints": {
            "admin": "/admin/",
            "api": "/api/",
            "token": "/api/token/",
            "token_refresh": "/api/token/refresh/",
            "register": "/api/register/",  # Add this
            "users": "/api/users/me/"      # Add this
        },
        "documentation": "Welcome to the Library API. Please use the endpoints above.",
        "status": "API is running"
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('library.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)