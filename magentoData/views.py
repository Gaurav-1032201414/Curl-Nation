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

DATABASE_URL = "postgresql://u4nngd66js0305:p90781a79b839c61737c07944104e13be1b802de28342499ed0cc39fd3eeb1fb9@ccpa7stkruda3o.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d3k968ks4p4b6u?sslmode=require"

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
            
            
            if 'customer_since' not in df.columns or df['customer_since'].isnull().all():
                df['customer_since'] = pd.Timestamp.now()

            # Upsert the data into the Customers table
            engine = create_engine(DATABASE_URL)
            df.set_index('customer_id', inplace = True)
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
            
            
            
            # num_rows = len(df)
            return JsonResponse({'message': f'Orders processed and saved successfully, rows found.'}, status=200)

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
                'msrp_price', 'map_enabled', 'gift_message_available', 'msrp_display_actual_price_type', 'country_of_manufacture', 'additional_attributes', 'qty',
                'out_of_stock_qty', 'additional_images', 'additional_image_labels'
            ]

            product_df = df[product_columns].drop_duplicates(subset=['product_id'])
            
            for _, row in product_df.iterrows():
                Product.objects.create(
                    product_id=row['product_id'],
                    attribute_set_code=row['attribute_set_code'],
                    product_type=row['product_type'],
                    product_websites=row['product_websites'],
                    name=row['name'],
                    product_online=row['product_online'],
                    tax_class_name=row['tax_class_name'],
                    visibility=row['visibility'],
                    price=row['price'],
                    special_price=row['special_price'],
                    url_key=row['url_key'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    new_from_date=row['new_from_date'],
                    new_to_date=row['new_to_date'],
                    display_product_options_in=row['display_product_options_in'],
                    map_price=row['map_price'],
                    msrp_price=row['msrp_price'],
                    map_enabled=row['map_enabled'],
                    gift_message_available=row['gift_message_available'],
                    msrp_display_actual_price_type=row['msrp_display_actual_price_type'],
                    country_of_manufacture=row['country_of_manufacture'],
                    additional_attributes=row['additional_attributes'],
                    qty=row['qty'],
                    out_of_stock_qty=row['out_of_stock_qty'],
                    additional_images=row['additional_images'],
                    additional_image_labels=row['additional_image_labels']
                )
            
            intersection_column = ["product_id", "categories"]
            intersection_df = df[intersection_column].dropna(subset=['categories'])
            intersection_df['categories'] = intersection_df['categories'].str.split(',')

            intersection_df = intersection_df.explode('categories').reset_index(drop=True)

            for _, row in intersection_df.iterrows():
                ProductCategoryIntersection.objects.create(
                    product_id=row['product_id'],
                    category=row['categories']
                )
            
            store_code = ["product_id", "store_view_code"]
            store_code_df = df[store_code]
            store_code_df['store_view_code'] = store_code_df['store_view_code'].fillna('')

            for _, row in store_code_df.iterrows():
                StoreCodeProduct.objects.create(
                    product_id=row['product_id'],
                    store_code_id=row['store_view_code']
                )

            return JsonResponse({"message": "Data upserted successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)


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