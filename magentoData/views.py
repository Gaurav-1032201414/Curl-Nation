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
from sqlalchemy.engine.url import URL
import dj_database_url

DATABASE_URL = "postgres://u4nngd66js0305:p90781a79b839c61737c07944104e13be1b802de28342499ed0cc39fd3eeb1fb9@ccpa7stkruda3o.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d3k968ks4p4b6u"


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
            df['Customer Since'] = df['Customer Since'].apply(parse_datetime)
            df = df.rename(columns={
                'ID': 'customer_id',
                'Name': 'name',
                'Email': 'email',
                'Group': 'group',
                'Phone': 'phone',
                'ZIP': 'zip',
                'Country': 'country',
                'State/Province': 'state',
                'Customer Since': 'customer_since',
                'Web Site': 'web_site',
                'Confirmed email': 'confirmed_email',
                'Account Created in': 'account_created_in',
                'Billing Address': 'billing_address',
                'Shipping Address': 'shipping_address',
                'Date of Birth': 'date_of_birth',
                'Tax VAT Number': 'tax_vat_number',
                'Gender': 'gender',
                'Street Address': 'street_address',
                'City': 'city',
                'Fax': 'fax',
                'VAT Number': 'vat_number',
                'Company': 'company',
                'Billing Firstname': 'billing_firstname',
                'Billing Lastname': 'billing_lastname',
                'Account Lock': 'account_lock',
                'Mailchimp': 'mailchimp',
                'Tier': 'tier',
                'Rewards Balance': 'rewards_balance',
                # Add more column mappings here as needed
            })
            
            df.set_index('customer_id', inplace = True)
            
            if 'customer_since' not in df.columns or df['customer_since'].isnull().all():
                df['customer_since'] = pd.Timestamp.now()

            # Upsert the data into the Customers table
            engine = create_engine(DATABASE_URL)
            pangres.upsert(df=df, con=engine, table_name='magentoData_customers', if_row_exists='update', create_table=False)
            
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
                pangres.upsert(df=order_df, con=cursor.connection, table_name='magentoData_orders', if_row_exists='update', create_table=False)

            # Upsert Order Products
            with connection.cursor() as cursor:
                pangres.upsert(df=order_product_df, con=cursor.connection, table_name='magentoData_orderproductintersection', if_row_exists='update', create_table=False)
            
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

            engine = create_engine(DATABASE_URL)

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
            pangres.upsert(con=engine, df=product_df, table_name='magentoData_product', if_row_exists='update', index_col='product_id')

            # Category Handling
            category_column = 'categories'
            Categories = df[category_column].dropna().tolist()
            category_list = list(set([item for sublist in Categories for item in str(sublist).split(',')]))
            categories_list = list(set([category.replace("Default Category/Categories/", "") for category in category_list]))
            split_categories = [category.split('/', 3) for category in categories_list]

            # Create category DataFrame
            category_df = pd.DataFrame(split_categories, columns=['Main Type', 'Category Type', 'Sub-Category Type', 'Additional Info'])
            category_df.fillna('', inplace=True)
            category_df['category_id'] = range(1, len(category_df) + 1)

            pangres.upsert(con=engine, df=category_df, table_name='magentoData_category', if_row_exists='update', index_col='category_id')

            # Intersection Handling
            intersection_data = []
            for _, row in category_df.iterrows():
                for product_id in product_df['product_id']:
                    intersection_data.append({'product_id': product_id, 'category_id': row['category_id'], 'category': row['Category Type']})

            intersection_df = pd.DataFrame(intersection_data).drop_duplicates()
            pangres.upsert(con=engine, df=intersection_df, table_name='magentoData_productcategoryintersection', if_row_exists='update')

            # Store code handling
            store_codes = df['store_view_code'].dropna().unique()
            store_code_df = pd.DataFrame({'store_code_view': list(store_codes)})
            store_code_df['store_code_id'] = range(1, len(store_code_df) + 1)
            store_code_df.set_index('store_code_id', inplace=True)

            # Upsert Store Code Data
            pangres.upsert(con=engine, df=store_code_df, table_name='magentoData_storecode', if_row_exists='update', index_col='store_code_id')

            # Prepare product_storecode data
            product_storecode_data = []
            for product_id in product_df['product_id']:
                for store_code in store_codes:
                    store_code_id = store_code_df[store_code_df['store_code_view'] == store_code].index[0]
                    product_storecode_data.append({'product_id': product_id, 'store_code_id': store_code_id})

            product_storecode_df = pd.DataFrame(product_storecode_data).drop_duplicates()
            pangres.upsert(con=engine, df=product_storecode_df, table_name='magentoData_storecodeproduct', if_row_exists='update')

            return JsonResponse({"message": "Data upserted successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


# @csrf_exempt
# def StockSource(request):
#     if request.method == "POST":
#         try:
#             print(f"Raw request body: {request.body.decode('utf-8')}")

#             if request.content_type == 'application/json':
#                 payload = json.loads(request.body.decode('utf-8'))
#                 sanitized_payload = sanitize_multiline_text(payload)
                
#                 print(f"Sanitized Payload: {sanitized_payload}")
                
#                 csv_data = sanitized_payload.get('csv_data')
#                 if csv_data:
#                     csv_io = StringIO(csv_data)
#                     df = pd.read_csv(csv_io)
#                     print(f"DataFrame from CSV: {df}")
#                 else:
#                     df = pd.json_normalize(sanitized_payload)
#                     print(f"DataFrame from JSON: {df}")
            
#             elif request.content_type == 'text/csv':
#                 csv_data = request.body.decode('utf-8')
#                 csv_io = StringIO(csv_data)
#                 df = pd.read_csv(csv_io)
#                 print(f"DataFrame from CSV: {df}")
            
#             else:
#                 return JsonResponse({'error': 'Unsupported content type'}, status=415)


#             print(df)
            
#             df = df.rename(columns={
#                 'Source Code': 'source_code',
#                 'Sku': 'sku',
#                 'Status': 'status',
#                 'Quantity': 'quantity',
#                 # Add more column mappings here as needed
#             })
            
#             df.rename(columns={"sku": "product_id"}, inplace=True)
#             df["inventory_id"] = "I" + df["source_code"] + df["product_id"]
#             df["status"] = df["status"].astype(bool)
            
#             df.set_index('product_id', inplace = True)
            
#             print(f"DataFrame: {df.head}")

#             engine = create_engine(DATABASE_URL)
#             pangres.upsert(df=df, con=engine, table_name='magentoData_inventory', if_row_exists='update', create_table=False)
            

#             return JsonResponse({"message": "Inventory created or updated successfully."}, status=201)

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)

#     else:
#         return JsonResponse({"error": "Invalid HTTP method."}, status=405)


@csrf_exempt
def StockSource(request):
    if request.method == "POST":
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

            print(df)
            
            df = df.rename(columns={
                'Source Code': 'source_code',
                'Sku': 'product_id_id',
                'Status': 'status',
                'Quantity': 'quantity',
            })
            
            df["inventory_id"] = "I" + df["source_code"] + df["product_id_id"]
            df["status"] = df["status"].astype(bool)
            
            print(f"DataFrame: {df.head()}")

            engine = create_engine(DATABASE_URL)

            df.to_sql('magentoData_inventory', con=engine, if_exists='append', index=False)

            return JsonResponse({"message": "Inventory created or updated successfully."}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid HTTP method."}, status=405)