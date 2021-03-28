"""rallz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


from rest_framework.documentation import include_docs_urls

from apps.version_router.urls import urlpatterns_v1

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'api/v1/', include(urlpatterns_v1)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += [
        path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        path(r'docs/', include_docs_urls(title='Jamesway API Guide')),
    ]