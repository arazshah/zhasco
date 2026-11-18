from django.urls import path

from careers import views

app_name = "careers"
urlpatterns = [
    path("careers/", views.job_list, name="list"),
    path("careers/apply/", views.general_application, name="apply"),
    path("careers/<int:pk>/", views.job_detail, name="detail"),
]
