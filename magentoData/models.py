from django.db import models
from django.utils import timezone

class Customers(models.Model):
    customer_id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    group = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    customer_since = models.DateTimeField(null=True, blank=True)
    web_site = models.CharField(max_length=100)
    confirmed_email = models.CharField(max_length=225)
    account_created_in = models.CharField(max_length=100)
    billing_address = models.TextField()
    shipping_address = models.TextField()
    date_of_birth = models.CharField(max_length=100)
    tax_vat_number = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    fax = models.CharField(max_length=100)
    vat_number = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    billing_firstname = models.CharField(max_length=100)
    billing_lastname = models.CharField(max_length=100)
    account_lock = models.CharField(max_length=100)
    mailchimp = models.CharField(max_length=100)
    tier = models.CharField(max_length=100)
    rewards_balance = models.CharField(max_length=100)

    def __str__(self):
        return self.email


class Product(models.Model):
    product_id = models.CharField(max_length=255, primary_key=True)
    attribute_set_code = models.CharField(max_length=255)
    product_type = models.CharField(max_length=255)
    product_websites = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    price = models.FloatField(null=True, blank=True)
    special_price = models.FloatField(null=True, blank=True)
    url_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    new_from_date = models.DateTimeField()
    new_to_date = models.DateTimeField()
    map_price = models.CharField(max_length=255, null=True, blank=True)
    msrp_price = models.CharField(max_length=255, null=True, blank=True)
    country_of_manufacture = models.CharField(max_length=255, null=True, blank=True)
    qty = models.CharField(max_length=255, null=True, blank=True)
    out_of_stock_qty = models.BooleanField(null=True, default=False)
    additional_images = models.CharField(max_length=255, null=True, blank=True)
    additional_image_labels = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.product_id
    

class Orders(models.Model):
    order_id = models.CharField(max_length=100, primary_key=True)
    purchase_point = models.CharField(max_length=100)
    purchase_date = models.CharField(max_length=100)
    bill_to_name = models.CharField(max_length=100)
    ship_to_name = models.CharField(max_length=100)
    grand_total_base = models.CharField(max_length=100)
    grand_total_purchased = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    billing_address = models.TextField() 
    shipping_address = models.TextField()
    shipping_information = models.CharField(max_length=100)
    customer_email = models.EmailField(max_length=100)
    customer_group = models.CharField(max_length=100)
    subtotal = models.CharField(max_length=100)
    shipping_and_handling = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=100)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='orders', to_field='email')
    payment_method = models.CharField(max_length=100)
    total_refunded = models.CharField(max_length=100)
    allocated_sources = models.CharField(max_length=100)
    pickup_location_code = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    order_note = models.CharField(max_length=100)
    app_order = models.CharField(max_length=100)

    def __str__(self):
        return self.order_id



class OrderProductIntersection(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    quantity = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    mailchimp_sync = models.CharField(max_length=100)
    braintree_transaction_source = models.CharField(max_length=100)
    

    def __str__(self):
        return self.product_id
    

class ProductCategoryIntersection(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_category_intersections')
    category = models.CharField(max_length=255)
    
    def __str__(self):
        return self.product_id
    

class Inventory(models.Model):
    inventory_id = models.CharField(max_length=100, primary_key=True)
    source_code = models.CharField(max_length=255)
    product_id_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    status = models.BooleanField(default=False)
    quantity = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product_id} - {self.source_code}"
    

class StoreCodeProduct(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_code_products')
    store_view_code = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.store_code_id} - {self.product_id}"
    