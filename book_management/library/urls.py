from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view()),
    path('login/', views.Login.as_view()),
    path('author/', views.AuthorView.as_view()),
    path('book/', views.BooksView.as_view()),
    path('book/<int:id>', views.BooksView.as_view()),
    path('add_review/', views.AddReview.as_view()),
    path('review/<int:author_id>', views.AuthorReview.as_view()),
]