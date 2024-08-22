from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('api/customers', views.CustomersView, name='Customers'),
    path('api/orders', views.OrdersView, name='Orders'),
    path('api/products', views.ProductView, name='product_list'),
    path('api/stocksource', views.StockSource, name='StockSource'),
]