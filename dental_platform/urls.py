from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from dashboard.views import HomeView
from users.views import CustomLoginView

admin.site.site_header = 'UDH ADMINISTRATION'
admin.site.site_title = 'UDH ADMINISTRATION'
admin.site.index_title = 'UDH ADMINISTRATION'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', include('dashboard.urls')),
    path('', include('users.urls')),
    path('', include('notes.urls')),
    path('', include('quizzes.urls')),
    path('past-papers/', include('papers.urls')),
    path('contribute/', include('contributions.urls')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
