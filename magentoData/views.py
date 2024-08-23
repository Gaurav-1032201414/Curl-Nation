import json
import pandas as pd
import pangres
from io import StringIO
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *  
from django.utils import timezone
import numpy as np
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_datetime
from django.db import connection
from django.conf import settings
from sqlalchemy import create_engine
import dj_database_url

DATABASE_URL = ("postgresql://utpl21rqpbenn:pd5913d12a2e87244ec562dbe5b8d93ce03bbb8fffc159496a053122d71e93a57@ccpa7stkruda3o.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d3eke1ul6shd79?sslmode=require")


def sanitize_multiline_text(data):
    if isinstance(data, dict):
        return {k: sanitize_multiline_text(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_multiline_text(v) for v in data]
    elif isinstance(data, str):
        return data.replace('\n', '\\n')
    return data

def parse_datetime(date_str):
    input_format = "%b %d, %Y %I:%M:%S %p"  # Format: "May 23x, 2024 10:00:45 PM"
    try:
        naive_datetime = datetime.strptime(date_str, input_format)
        return timezone.make_aware(naive_datetime, timezone.get_current_timezone())
    except ValueError:
        return None

# Handle customer data upsert
@csrf_exempt
def CustomersView(request):
    if request.method == 'POST':
        try:
            print(f"Raw request body: {request.body.decode('utf-8')}")

            if request.content_type == 'application/json':
                payload = json.loads(request.body.decode('utf-8'))
                sanitized_payload = sanitize_multiline_text(payload)
                
                print(f"Sanitized Payload: {sanitized_payload}")
                
                csv_data = sanitized_payload.get('csv_data')
                if csv_data:
                    csv_io = StringIO(csv_data)
                    df = pd.read_csv(csv_io)
                    print(f"DataFrame from CSV: {df}")
                else:
                    df = pd.json_normalize(sanitized_payload)
                    print(f"DataFrame from JSON: {df}")
            
            elif request.content_type == 'text/csv':
                csv_data = request.body.decode('utf-8')
                csv_io = StringIO(csv_data)
                df = pd.read_csv(csv_io)
                print(f"DataFrame from CSV: {df}")
            
            else:
                return JsonResponse({'error': 'Unsupported content type'}, status=415)

            # DataFrame processing
            df['customer_since'] = df['Customer Since'].apply(parse_datetime)
            df = df.rename(columns={
                'ID': 'customer_id',
                'Name': 'name',
                'Email': 'email',
                # Add more column mappings here as needed
            })

            # Upsert the data into the Customers table
            with connection.cursor() as cursor:
                pangres.upsert(df=df, con=cursor.connection, table_name='yourapp_customers', if_row_exists='update', create_table=False)
            
            num_rows = len(df)
            return JsonResponse({'message': f'Data processed and saved successfully, {num_rows} rows found.'}, status=200)
        
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return HttpResponse("This endpoint only accepts POST requests.", status=405)


@csrf_exempt
def OrdersView(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                payload = json.loads(request.body.decode('utf-8'))
                sanitized_payload = sanitize_multiline_text(payload)

                csv_data = sanitized_payload.get('csv_data')
                if csv_data:
                    csv_io = StringIO(csv_data)
                    df = pd.read_csv(csv_io)
                else:
                    df = pd.json_normalize(sanitized_payload)
            
            elif request.content_type == 'text/csv':
                csv_data = request.body.decode('utf-8')
                csv_io = StringIO(csv_data)
                df = pd.read_csv(csv_io)
            
            else:
                return JsonResponse({'error': 'Unsupported content type'}, status=415)
            
            # DataFrame processing
            df = df.replace({None: np.nan})

            order_df = df[[
                "ID", "Purchase Point", "Purchase Date", "Bill-to Name", "Ship-to Name", 
                "Grand Total (Base)", "Grand Total (Purchased)", "Status", "Billing Address", 
                "Shipping Address", "Shipping Information", "Customer Email", "Customer Group", 
                "Subtotal", "Shipping and Handling", "Customer Name", "Payment Method", 
                "Total Refunded", "Allocated sources", "Pickup Location Code", "Phone Number", 
                "Order Note", "App Order"
            ]].copy()
            
            order_df = order_df.rename(
                columns={
                    "ID": "order_id",
                    "Purchase Point": "purchase_point",
                    "Purchase Date": "purchase_date",
                    "Bill-to Name": "bill_to_name",
                    "Ship-to Name": "ship_to_name",
                    "Grand Total (Base)": "grand_total_base",
                    "Grand Total (Purchased)": "grand_total_purchased",
                    "Status": "status",
                    "Billing Address": "billing_address",
                    "Shipping Address": "shipping_address",
                    "Shipping Information": "shipping_information",
                    "Customer Email": "customer_email",
                    "Customer Group": "customer_group",
                    "Subtotal": "subtotal",
                    "Shipping and Handling": "shipping_and_handling",
                    "Customer Name": "customer_name",
                    "Payment Method": "payment_method",
                    "Total Refunded": "total_refunded",
                    "Allocated sources": "allocated_sources",
                    "Pickup Location Code": "pickup_location_code",
                    "Phone Number": "phone_number",
                    "Order Note": "order_note",
                    "App Order": "app_order",
                }
            )

            order_product_df = df[[
                "ID", "Sku", "Quantity", "Price", "Barcode", "Zip Code", 
                "City", "Country", "Mailchimp Sync", "Braintree Transaction Source"
            ]].copy()
            
            order_product_df = order_product_df.rename(
                columns={
                    "ID": "order_id",
                    "Sku": "product_id",
                    "Quantity": "quantity",
                    "Price": "price",
                    "Barcode": "barcode",
                    "Zip Code": "zip_code",
                    "City": "city",
                    "Country": "country",
                    "Mailchimp Sync": "mailchimp_sync",
                }
            )
            
            # Upsert Orders
            with connection.cursor() as cursor:
                pangres.upsert(df=order_df, con=cursor.connection, table_name='yourapp_orders', if_row_exists='update', create_table=False)

            # Upsert Order Products
            with connection.cursor() as cursor:
                pangres.upsert(df=order_product_df, con=cursor.connection, table_name='yourapp_orderproductintersection', if_row_exists='update', create_table=False)
            
            num_rows = len(df)
            return JsonResponse({'message': f'Orders processed and saved successfully, {num_rows} rows found.'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return HttpResponse("This endpoint only accepts POST requests.", status=405)


@csrf_exempt
def ProductView(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            df = pd.DataFrame(data)
            df.rename(columns={"sku": "product_id"}, inplace=True)

            product_columns = [
                'product_id', 'attribute_set_code', 'product_type', 'product_websites',
                'name', 'product_online', 'tax_class_name', 'visibility', 'price', 'special_price', 'url_key',
                'created_at', 'updated_at', 'new_from_date', 'new_to_date', 'display_product_options_in', 'map_price',
                'msrp_price', 'map_enabled', 'gift_message_available', 'custom_design', 'custom_design_from',
                'custom_design_to', 'custom_layout_update', 'page_layout', 'product_options_container',
                'msrp_display_actual_price_type', 'country_of_manufacture', 'additional_attributes', 'qty',
                'out_of_stock_qty', 'use_config_min_qty', 'is_qty_decimal', 'allow_backorders', 'use_config_backorders',
                'min_cart_qty', 'use_config_min_sale_qty', 'max_cart_qty', 'use_config_max_sale_qty', 'is_in_stock',
                'notify_on_stock_below', 'use_config_notify_stock_qty', 'manage_stock', 'use_config_manage_stock',
                'use_config_qty_increments', 'qty_increments', 'use_config_enable_qty_inc', 'enable_qty_increments',
                'is_decimal_divided', 'website_id', 'related_skus', 'related_position', 'crosssell_skus',
                'crosssell_position', 'upsell_skus', 'upsell_position', 'additional_images', 'additional_image_labels',
                'hide_from_product_page', 'custom_options', 'bundle_price_type', 'bundle_sku_type', 'bundle_price_view',
                'bundle_weight_type', 'bundle_values', 'bundle_shipment_type', 'associated_skus', 'downloadable_links',
                'downloadable_samples', 'configurable_variations', 'configurable_variation_labels'
            ]

            # Upsert Product Data
            product_df = df[product_columns].drop_duplicates(subset=['product_id'])
            product_df.set_index('product_id', inplace=True)
            pangres.upsert(con=connection, df=product_df, table_name='magentoData_product', if_row_exists='update')

            category_column = 'categories'
            Categories = df[category_column].dropna().tolist()
            category_list = list(set([item for sub in Categories for item in str(sub).split(',')]))
            categories_list = list(set([category.replace("Default Category/Categories/", "") for category in category_list]))
            split_categories = [category.split('/', 3) for category in categories_list]
            
            # Create category DataFrame
            category_df = pd.DataFrame(split_categories, columns=['Main Type', 'Category Type', 'Sub-Category Type', 'Additional Info'])
            category_df.fillna('', inplace=True)

            category_df['category_id'] = range(1, len(category_df) + 1)

            category_df.set_index('category_id', inplace=True)
            pangres.upsert(con=connection, df=category_df, table_name='magentoData_category', if_row_exists='update')

            intersection_data = []
            for _, row in category_df.iterrows():
                for product_id in product_df.index:
                    intersection_data.append({'product_id': product_id, 'category_id': row.name, 'category': row['Category Type']})

            intersection_df = pd.DataFrame(intersection_data).drop_duplicates()
            pangres.upsert(con=connection, df=intersection_df, table_name='magentoData_productcategoryintersection', if_row_exists='update')

            # Store code handling
            store_codes = df['store_view_code'].dropna().unique()
            store_code_df = pd.DataFrame(store_codes, columns=['store_code_view'])
            store_code_df['store_code_id'] = range(1, len(store_code_df) + 1)

            # Upsert Store Code Data
            store_code_df.set_index('store_code_id', inplace=True)
            pangres.upsert(con=connection, df=store_code_df, table_name='magentoData_storecode', if_row_exists='update')

            # Prepare product_storecode data
            product_storecode_data = []
            for product_id in product_df.index:
                for store_code in store_codes:
                    store_code_id = store_code_df[store_code_df['store_code_view'] == store_code].index[0]
                    product_storecode_data.append({'product_id': product_id, 'store_code_id': store_code_id})

            product_storecode_df = pd.DataFrame(product_storecode_data).drop_duplicates()
            pangres.upsert(con=connection, df=product_storecode_df, table_name='magentoData_storecodeproduct', if_row_exists='update')

            return JsonResponse({"message": "Data upserted successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@csrf_exempt
def StockSource(request):
    if request.method == "POST":
        try:
            source_code = request.POST.get('source_code')
            product_id = request.POST.get('sku')
            status = request.POST.get('status')
            quantity = request.POST.get('quantity')

            data = {
                'source_code': [source_code],
                'product_id': [product_id],
                'status': [bool(status)],
                'quantity': [quantity]
            }
            df = pd.DataFrame(data)
            
            # db_url = dj_database_url.config('postgres://utpl21rqpbenn:pd5913d12a2e87244ec562dbe5b8d93ce03bbb8fffc159496a053122d71e93a57@ccpa7stkruda3o.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d3eke1ul6shd79') # , conn_max_age=600, ssl_require=True
            
            # db_url = dj_database_url.parse(
            #     'postgres://utpl21rqpbenn:pd5913d12a2e87244ec562dbe5b8d93ce03bbb8fffc159496a053122d71e93a57@ccpa7stkruda3o.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d3eke1ul6shd79',
            #     conn_max_age=600,
            #     ssl_require=True
            # )
            
            engine = create_engine(DATABASE_URL)

            pangres.upsert(
                con=engine,
                df=df,
                table_name='magentoData_inventory',
                if_row_exists='update'
            )

            return JsonResponse({"message": "Inventory created or updated successfully."}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid HTTP method."}, status=405)
