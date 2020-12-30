from django.urls import path, include


from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("results/", views.results, name = "results"),
    path("randompage/", views.randompage, name = "randompage"),
    path("newpage/", views.newpage, name = "newpage"),
    path("test/", views.test, name = "test"),    
    path("edit/<str:edit_title>/", views.edit, name = "edit"),
    path("<str:title>/", views.entry, name = "entry")
]
