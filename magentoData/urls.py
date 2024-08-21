from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('api/customers', views.CustomersView, name='Customers'),
    path('api/orders', views.OrdersView, name='Orders'),
    path('api/products', views.ProductView, name='product_list'),
    path('api/products/<str:product_id>', views.ProductView, name='product_detail'),
    path('api/categorys', views.CategoryView, name='category_list'),
    path('api/categorys/<int:category_id>', views.CategoryView, name='category_detail'),
    path('api/product-category', views.ProductCategoryIntersectionView, name='product_category_list'),
    path('api/inventory', views.StockSource, name='StockSource'),
]