
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
]

# Serve user-uploaded media files (product images).
# django.conf.urls.static.static() only works when DEBUG=True, so we register
# an explicit route that also works in production. NOTE: on free hosts the
# filesystem is ephemeral, so these files are lost on redeploy/restart — see
# the deploy guide for a persistent (Cloudinary) option.
urlpatterns += [
    re_path(
        r'^media/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),
]
