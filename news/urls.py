from django.urls import path

from news import views

app_name = "news"
urlpatterns = [
    path("news/", views.post_list, name="list"),
    path("news/<int:pk>/", views.post_detail, name="detail"),
]
