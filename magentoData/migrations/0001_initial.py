# Generated by Django 5.1 on 2024-09-02 15:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customers',
            fields=[
                ('customer_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('group', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=100)),
                ('zip', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('customer_since', models.DateTimeField(blank=True, null=True)),
                ('web_site', models.CharField(max_length=100)),
                ('confirmed_email', models.CharField(max_length=225)),
                ('account_created_in', models.CharField(max_length=100)),
                ('billing_address', models.TextField()),
                ('shipping_address', models.TextField()),
                ('date_of_birth', models.CharField(max_length=100)),
                ('tax_vat_number', models.CharField(max_length=100)),
                ('gender', models.CharField(max_length=100)),
                ('street_address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('fax', models.CharField(max_length=100)),
                ('vat_number', models.CharField(max_length=100)),
                ('company', models.CharField(max_length=100)),
                ('billing_firstname', models.CharField(max_length=100)),
                ('billing_lastname', models.CharField(max_length=100)),
                ('account_lock', models.CharField(max_length=100)),
                ('mailchimp', models.CharField(max_length=100)),
                ('tier', models.CharField(max_length=100)),
                ('rewards_balance', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('attribute_set_code', models.CharField(max_length=255)),
                ('product_type', models.CharField(max_length=255)),
                ('product_websites', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(max_length=255)),
                ('product_online', models.FloatField(blank=True, null=True)),
                ('tax_class_name', models.CharField(blank=True, max_length=255, null=True)),
                ('visibility', models.CharField(blank=True, max_length=255, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('special_price', models.FloatField(blank=True, null=True)),
                ('url_key', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('new_from_date', models.DateTimeField()),
                ('new_to_date', models.DateTimeField()),
                ('display_product_options_in', models.CharField(blank=True, max_length=255, null=True)),
                ('map_price', models.CharField(blank=True, max_length=255, null=True)),
                ('msrp_price', models.CharField(blank=True, max_length=255, null=True)),
                ('map_enabled', models.CharField(blank=True, max_length=255, null=True)),
                ('gift_message_available', models.CharField(blank=True, max_length=255, null=True)),
                ('msrp_display_actual_price_type', models.CharField(blank=True, max_length=255, null=True)),
                ('country_of_manufacture', models.CharField(blank=True, max_length=255, null=True)),
                ('additional_attributes', models.TextField(blank=True, null=True)),
                ('qty', models.CharField(blank=True, max_length=255, null=True)),
                ('out_of_stock_qty', models.BooleanField(default=False, null=True)),
                ('max_cart_qty', models.FloatField(default=0, null=True)),
                ('additional_images', models.CharField(blank=True, max_length=255, null=True)),
                ('additional_image_labels', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('order_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('purchase_point', models.CharField(max_length=100)),
                ('purchase_date', models.CharField(max_length=100)),
                ('bill_to_name', models.CharField(max_length=100)),
                ('ship_to_name', models.CharField(max_length=100)),
                ('grand_total_base', models.CharField(max_length=100)),
                ('grand_total_purchased', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=100)),
                ('billing_address', models.TextField()),
                ('shipping_address', models.TextField()),
                ('shipping_information', models.CharField(max_length=100)),
                ('customer_email', models.EmailField(max_length=100)),
                ('customer_group', models.CharField(max_length=100)),
                ('subtotal', models.CharField(max_length=100)),
                ('shipping_and_handling', models.CharField(max_length=100)),
                ('customer_name', models.CharField(max_length=100)),
                ('payment_method', models.CharField(max_length=100)),
                ('total_refunded', models.CharField(max_length=100)),
                ('allocated_sources', models.CharField(max_length=100)),
                ('pickup_location_code', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=100)),
                ('order_note', models.CharField(max_length=100)),
                ('app_order', models.CharField(max_length=100)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='magentoData.customers', to_field='email')),
            ],
        ),
        migrations.CreateModel(
            name='OrderProductIntersection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.CharField(max_length=100)),
                ('price', models.CharField(max_length=100)),
                ('barcode', models.CharField(max_length=100)),
                ('zip_code', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('country', models.CharField(max_length=100)),
                ('mailchimp_sync', models.CharField(max_length=100)),
                ('braintree_transaction_source', models.CharField(max_length=100)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='magentoData.orders')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='magentoData.product')),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('inventory_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('source_code', models.CharField(max_length=255)),
                ('status', models.BooleanField(default=False)),
                ('quantity', models.CharField(max_length=255)),
                ('product_id_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventories', to='magentoData.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategoryIntersection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=255)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_category_intersections', to='magentoData.product')),
            ],
        ),
        migrations.CreateModel(
            name='StoreCodeProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_view_code', models.CharField(max_length=255)),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='store_code_products', to='magentoData.product')),
            ],
        ),
    ]
