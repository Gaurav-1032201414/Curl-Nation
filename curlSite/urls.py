from django.urls import path
from . import views

urlpatterns = [
    
    ## Basic Urls
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('update_sync_settings/', views.update_sync_settings, name='update_sync_settings'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('sync_data/', views.sync_data, name='sync_data'),
    path('logout/', views.logout, name='logout'),
    
    # Organization Urls
    
    ## Department Urls
    path('add_department/', views.add_department, name='add_department'),
    path('department_data/<int:department_id>/', views.department_data, name='department_data'),
    path('all_departments/', views.all_departments, name='all_departments'),
    path('delete_department/<int:department_id>/', views.delete_department, name='delete_department'),
    
    ## Location Urls
    path('add_location/', views.add_location, name='add_location'),
    path('location_data/<int:location_id>/', views.location_data, name='location_data'),
    path('all_locations/', views.all_locations, name='all_locations'),
    path('delete_location/<int:location_id>/', views.delete_location, name='delete_location'),
    
    ## Employee Management Urls
    path('add_employee/', views.add_employee, name='add_employee'),
    path('all_employees/', views.all_employees, name='all_employees'),
    path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    
    ## Role Management Urls
    path('add_role/', views.add_role, name='add_role'),
    path('all_roles/', views.all_roles, name='all_roles'),
    path('delete_role/<int:role_id>/', views.delete_role, name='delete_role'),
    
    ## Warehouse Management Urls
    path('add_warehouse/', views.add_warehouse, name='add_warehouse'),
    path('update_warehouse/<int:warehouse_id>/', views.update_warehouse, name='update_warehouse'),
    path('delete_warehouse/<int:warehouse_id>/', views.delete_warehouse, name='delete_warehouse'),
    path('all_warehouses/', views.all_warehouses, name='all_warehouses'),
    path('warehouse/<int:warehouse_id>/', views.get_warehouse, name='get_warehouse'),
    
    ## Store Management Urls
    path('add_store/', views.add_store, name='add_store'),
    path('update_store/<int:store_id>/', views.update_store, name='update_store'),
    path('delete_store/<int:store_id>/', views.delete_store, name='delete_store'),
    path('all_stores/', views.all_stores, name='all_stores'),
    path('store/<str:store_name>/', views.get_store, name='get_store'),
    path('store_with_products/', views.get_store_with_products, name='get_store_with_products'),
    
    ## Activity Log Url
    path('activity_log/', views.view_activity_log, name='view_activity_log'),

]