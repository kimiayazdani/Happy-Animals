
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url, include
from . import settings
from rest_framework.authtoken.views import obtain_auth_token
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import static, staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls'), name='rest_framework'),
    # path('post/', include('Post.urls')),
    # path('channel/', include('channel.urls')),
    path('api/v1/account/', include('account_management.urls_v1')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth')
    # path('mainpage/',include('MainPage.urls')),
    # path('notifications/', include('notifications.urls')),
    # path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    # path('search/', include('search.urls')),
    # path('api/auth/oauth/', include('rest_framework_social_oauth2.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += staticfiles_urlpatterns()
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
