"""core URL Configuration

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
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from django.conf import settings
from django.contrib.auth import views as auth_views #new
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf.urls.static import static
from stores.views import NotFoundPageView, manifestview, firebaseview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', success_url='/dashboard/'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    
    path('', include('stores.urls', namespace='stores')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('notification/', include('notification.urls', namespace='notification')),
    
    
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),

    # pwa
    path('manifest.json', manifestview, name="manifestview"),
    path('firebase-messaging-sw.js', firebaseview),
    # path("", include('pwa.urls')),
    
]
urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
               static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = NotFoundPageView.as_view()
handler500 = NotFoundPageView.as_view()

admin.site.site_header = "Iberry Admin"
admin.site.site_title = "Iberry Admin"
admin.site.index_title = "Welcome to Admin Portal"