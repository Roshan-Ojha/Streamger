from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .views import FillContent,Contents



urlpatterns = [
    path('fill_contents/<str:content_type>',FillContent.as_view(),name="fill_content"),
    path('content/',Contents.as_view(),name="add_content")

]
