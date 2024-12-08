from django.urls import path, include
from api.spectacular.urls import urlpatterns as doc_urls

app_name = 'api'

urlpatterns = [
    path('users/', include('apps.users.urls', namespace='authentication')),
    path('comments/', include('apps.comments.urls', namespace='comments')),
    path('news/', include('apps.news.urls', namespace='news')),
    path('schedule/', include('apps.schedule.urls', namespace='schedule')),
    path('order/', include('apps.order.urls', namespace='order')),
]

urlpatterns += doc_urls
