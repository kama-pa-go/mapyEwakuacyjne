from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from mapy import views as mapy_views
from rest_framework.authtoken import views

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Trasy API",
      default_version='v1',
      description="API do zarządzania trasami i ich punktami",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="k_godlewska@interia.pl"),
      license=openapi.License(name="License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include('mapy.urls')),

    path('account/rejestracja/', mapy_views.rejestracja, name='rejestracja'),
    path('account/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),

    path('api/', include('mapy.api_urls'), name='mapy_api'),
    path('api/auth-token/', views.obtain_auth_token, name='api_auth_token'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)