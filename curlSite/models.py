from django.db import models
from django.contrib.auth.models import User

from magentoData.models import Product

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True)
    full_name = models.CharField(max_length=100, blank=True)
    otp = models.CharField(max_length=6, blank=True)
    sync_to_shopify = models.BooleanField(default=False) 
    sync_to_other_source = models.BooleanField(default=False) 

    def __str__(self):
        return self.user.username
    
    
class Department(models.Model):
    name = models.CharField(max_length=100)
    department_id = models.AutoField(primary_key=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def number_of_employees(self):
        return self.employee_set.count()

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, related_name='managed_locations')
    location_id = models.AutoField(primary_key=True)
    manager_contact = models.CharField(max_length=15)
    manager_email = models.EmailField()
    date_added = models.DateTimeField(auto_now_add=True)

    def number_of_employees(self):
        return self.employee_set.count()

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100)
    access_control_1 = models.BooleanField(default=False)
    access_control_2 = models.BooleanField(default=False)
    access_control_3 = models.BooleanField(default=False)
    access_control_4 = models.BooleanField(default=False)
    access_control_5 = models.BooleanField(default=False)
    access_control_6 = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    employee_id = models.AutoField(primary_key=True)
    contact = models.CharField(max_length=15)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    departments = models.ManyToManyField(Department, blank=True)
    locations = models.ManyToManyField(Location, blank=True)
    email = models.EmailField(unique=True)
    address = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    contact_person_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name
    
    
class ActivityLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    employee_name = models.CharField(max_length=255)
    module_name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=50)
    employee_role = models.CharField(max_length=100)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.module_name} - {self.activity_type} - {self.timestamp}"
    
    

class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    products = models.ManyToManyField(Product, blank=True)
    contact_person_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name