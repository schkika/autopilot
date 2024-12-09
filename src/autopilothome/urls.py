"""
URL configuration for autopilothome project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from . import views
admin.site.site_header = 'Autopilot administracija'

urlpatterns = [
    path('', views.home_view, name="home"),
    # Test views
    path('error', views.error_view, name="error"),
    path('editor/<int:id>/<int:pk>', views.editor, name="editor"),
    path('editor/<int:id>/<int:pk>/<str:assemble>', views.editor, name="editor"),
    path('buckets', views.bucket_list_view, name="buckets"),
    path('file', views.send_file, name="send-file"),
    path('acceptpdf', views.accept_pdf, name="accept-pdf"),
    path('login-autocad-user', views.login_autocad_user, name="login-autocad-user"),
    path('logout-autocad-user', views.logout_autocad_user, name="logout-autocad-user"),
    path('check-autocad-user', views.check_autocad_user, name="check-autocad-user"),
    path('user-files', views.user_files, name="user-files"),
    # End test views
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('main/', include('main.urls', namespace='main')),
    path('download-elaborat-primer', views.download_elaborat_primer, name='download-elaborat-primer'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.TE_URL,
                          document_root=settings.STATIC_ROOT)
