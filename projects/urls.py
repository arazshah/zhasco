from django.urls import path

from projects import views

app_name = "projects"
urlpatterns = [
    path("projects/", views.project_list, name="list"),
    path("projects/<int:pk>/", views.project_detail, name="detail"),
    path("services/", views.service_list, name="services"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("api/provinces/<slug:slug>/", views.province_api, name="province_api"),
]
