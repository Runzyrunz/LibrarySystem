from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_books, name='search'),
    path('checkout/', views.checkout_book, name='checkout'),
    path('checkin/', views.checkin_book, name='checkin'),
    path('borrower/', views.add_borrower, name='add_borrower'),
    path('fines/', views.view_fines, name='fines'),
    path('home/', views.borrower_home, name='borrower_home'),
    path('batch_checkout/', views.batch_checkout, name='batch_checkout'),

]
