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
    customer_since = models.DateTimeField()
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
    customer_name = models.CharField(max_length=100)
    subtotal = models.CharField(max_length=100)
    shipping_and_handling = models.CharField(max_length=100)
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
    product_id = models.CharField(max_length=100)
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


class Product(models.Model):
    product_id = models.CharField(max_length=255)
    store_view_code = models.CharField(max_length=255, null=True, blank=True)
    attribute_set_code = models.CharField(max_length=255)
    product_type = models.CharField(max_length=255)
    categories = models.CharField(max_length=255, null=True, blank=True)
    product_websites = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    product_online = models.FloatField(null=True, blank=True)
    tax_class_name = models.CharField(max_length=255, null=True, blank=True)
    visibility = models.CharField(max_length=255, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    special_price = models.FloatField(null=True, blank=True)
    url_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    new_from_date = models.DateTimeField()
    new_to_date = models.DateTimeField()
    display_product_options_in = models.CharField(max_length=255, null=True, blank=True)
    map_price = models.CharField(max_length=255, null=True, blank=True)
    msrp_price = models.CharField(max_length=255, null=True, blank=True)
    map_enabled = models.CharField(max_length=255, null=True, blank=True)
    gift_message_available = models.CharField(max_length=255, null=True, blank=True)
    custom_design = models.CharField(max_length=255, null=True, blank=True)
    custom_design_from = models.CharField(max_length=255, null=True, blank=True)
    custom_design_to = models.CharField(max_length=255, null=True, blank=True)
    custom_layout_update = models.CharField(max_length=255, null=True, blank=True)
    page_layout = models.CharField(max_length=255, null=True, blank=True)
    product_options_container = models.CharField(max_length=255, null=True, blank=True)
    msrp_display_actual_price_type = models.CharField(max_length=255, null=True, blank=True)
    country_of_manufacture = models.CharField(max_length=255, null=True, blank=True)
    additional_attributes = models.TextField(null=True, blank=True)
    qty = models.CharField(max_length=255, null=True, blank=True)
    out_of_stock_qty = models.BooleanField(null=True, default=False)
    use_config_min_qty = models.BooleanField(null=True, default=False)
    is_qty_decimal = models.BooleanField(null=True, default=False)
    allow_backorders = models.BooleanField(null=True, default=False)
    use_config_backorders = models.BooleanField(null=True, default=False)
    min_cart_qty = models.BooleanField(null=True, default=False)
    use_config_min_sale_qty = models.BooleanField(null=True, default=False)
    max_cart_qty = models.FloatField(null=True, default=0)
    use_config_max_sale_qty = models.BooleanField(null=True, default=False)
    is_in_stock = models.BooleanField(null=True, default=False)
    notify_on_stock_below = models.BooleanField(null=True, default=False)
    use_config_notify_stock_qty = models.BooleanField(null=True, default=False)
    manage_stock = models.BooleanField(null=True, default=False)
    use_config_manage_stock = models.BooleanField(null=True, default=False)
    use_config_qty_increments = models.BooleanField(null=True, default=False)
    qty_increments = models.BooleanField(null=True, default=False)
    use_config_enable_qty_inc = models.BooleanField(null=True, default=False)
    enable_qty_increments = models.BooleanField(null=True, default=False)
    is_decimal_divided = models.BooleanField(null=True, default=False)
    website_id = models.BooleanField(null=True, default=False)
    related_skus = models.CharField(max_length=255, null=True, blank=True)
    related_position = models.CharField(max_length=255, null=True, blank=True)
    crosssell_skus = models.CharField(max_length=255, null=True, blank=True)
    crosssell_position = models.CharField(max_length=255, null=True, blank=True)
    upsell_skus = models.CharField(max_length=255, null=True, blank=True)
    upsell_position = models.CharField(max_length=255, null=True, blank=True)
    additional_images = models.CharField(max_length=255, null=True, blank=True)
    additional_image_labels = models.CharField(max_length=255, null=True, blank=True)
    hide_from_product_page = models.CharField(max_length=255, null=True, blank=True)
    custom_options = models.CharField(max_length=255, null=True, blank=True)
    bundle_price_type = models.CharField(max_length=255, null=True, blank=True)
    bundle_sku_type = models.CharField(max_length=255, null=True, blank=True)
    bundle_price_view = models.CharField(max_length=255, null=True, blank=True)
    bundle_weight_type = models.CharField(max_length=255, null=True, blank=True)
    bundle_values = models.CharField(max_length=255, null=True, blank=True)
    bundle_shipment_type = models.CharField(max_length=255, null=True, blank=True)
    associated_skus = models.CharField(max_length=255, null=True, blank=True)
    downloadable_links = models.CharField(max_length=255, null=True, blank=True)
    downloadable_samples = models.CharField(max_length=255, null=True, blank=True)
    configurable_variations = models.CharField(max_length=255, null=True, blank=True)
    configurable_variation_labels = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.product_id
    

class Category(models.Model):
    category_id = models.CharField(max_length=255)
    gender_type = models.CharField(max_length=100)
    category_type = models.CharField(max_length=100)
    sub_category_type = models.CharField(max_length=100)
    additional_info = models.CharField(max_length=255)
    category = models.CharField(max_length=512, blank=True) 

    def save(self, *args, **kwargs):
        self.category = f'{self.gender_type}/{self.category_type}/{self.sub_category_type}/{self.additional_info}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category
    

class ProductCategoryIntersection(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_category_intersections')
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    category = models.CharField(max_length=255)
    
    def __str__(self):
        return self.product_id
    

class Inventory(models.Model):
    source_code = models.CharField(max_length=255)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    status = models.BooleanField(default=False)
    quantity = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product_id} - {self.source_code}"
    

class StoreCode(models.Model):
    store_code_id = models.CharField(max_length=255)
    store_view_code = models.CharField(max_length=255)
    
    def __str__(self):
        return self.store_code_id


class StoreCodeProduct(models.Model):
    store_code_id = models.ForeignKey(StoreCode, on_delete=models.CASCADE, related_name='store_code_products')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_code_products')

    def __str__(self):
        return f"{self.store_code_id} - {self.product_id}"
    