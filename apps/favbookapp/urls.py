from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('registration', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('books', views.books),
    path('add_books', views.add_books),
    path('books/<int:bookid>', views.book_click),
    path('editbook/<int:bookid>',views.edit_book),
    path('delete/<int:bookid>', views.delete_book),
    path('like/<int:bookid>', views.like_book),
    path('unlike/<int:bookid>', views.unlike_book),
]