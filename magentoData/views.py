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

            num_rows = len(df)
            for index, row in df.iterrows():
                try:
                    customer_since_str = row.get('Customer Since', '')
                    customer_since = parse_datetime(customer_since_str)
                    
                    customer = Customers(
                        customer_id=row.get('ID', ''),
                        name=row.get('Name', 'Unknown'), 
                        email=row.get('Email', ''),
                        group=row.get('Group', ''),
                        phone=row.get('Phone', ''),
                        zip=row.get('ZIP', ''),
                        country=row.get('Country', ''),
                        state=row.get('State/Province', ''),
                        customer_since= customer_since,
                        web_site=row.get('Web Site', ''),
                        confirmed_email=row.get('Confirmed email', ''),
                        account_created_in=row.get('Account Created in', ''),
                        billing_address=row.get('Billing Address', ''),
                        shipping_address=row.get('Shipping Address', ''),
                        date_of_birth=row.get('Date of Birth', ''),
                        tax_vat_number=row.get('Tax VAT Number', ''),
                        gender=row.get('Gender', ''),
                        street_address=row.get('Street Address', ''),
                        city=row.get('City', ''),
                        fax=row.get('Fax', ''),
                        vat_number=row.get('VAT Number', ''),
                        company=row.get('Company', ''),
                        billing_firstname=row.get('Billing Firstname', ''),
                        billing_lastname=row.get('Billing Lastname', ''),
                        account_lock=row.get('Account Lock', ''),
                        mailchimp=row.get('Mailchimp', ''),
                        tier=row.get('Tier', ''),
                        rewards_balance=row.get('Rewards Balance', ''),
                    )
                    customer.save()
                except Exception as e:
                    print(f"Error saving customer: {e}")

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
            
            num_rows = len(df)
            
            # Order DataFrame
            order_df = df[["ID", "Purchase Point", "Purchase Date", "Bill-to Name", "Ship-to Name", "Grand Total (Base)", "Grand Total (Purchased)", "Status", "Billing Address", "Shipping Address", "Shipping Information", "Customer Email", "Customer Group", "Subtotal", "Shipping and Handling", "Customer Name", "Payment Method", "Total Refunded", "Allocated sources", "Pickup Location Code", "Phone Number", "Order Note", "App Order"]].copy()
            order_df = order_df.replace({None: np.nan})
            order_df = order_df.dropna(how='all', subset=["Purchase Point", "Purchase Date", "Bill-to Name", "Ship-to Name", "Grand Total (Base)", "Grand Total (Purchased)", "Status", "Billing Address", "Shipping Address", "Shipping Information", "Customer Email", "Customer Group", "Subtotal", "Shipping and Handling", "Customer Name", "Payment Method", "Total Refunded", "Allocated sources", "Pickup Location Code", "Phone Number", "Order Note"])
            
            # Order-Product DataFrame
            order_product_df = df[["ID", "Sku", "Quantity", "Price", "Barcode", "Zip Code", "City", "Country", "Mailchimp Sync", "Braintree Transaction Source"]].copy()
            
            for index, row in order_df.iterrows():
                try:
                    customer = Customers.objects.get(email=row.get('Customer Email', ''))
                    
                    order = Orders(
                        order_id=row.get('ID', ''),
                        purchase_point=row.get('Purchase Point', ''),
                        purchase_date=row.get('Purchase Date', ''),
                        bill_to_name=row.get('Bill-to Name', ''),
                        ship_to_name=row.get('Ship-to Name', ''),
                        grand_total_base=row.get('Grand Total (Base)', ''),
                        grand_total_purchased=row.get('Grand Total (Purchased)', ''),
                        status=row.get('Status', ''),
                        billing_address=row.get('Billing Address', ''),
                        shipping_address=row.get('Shipping Address', ''),
                        shipping_information=row.get('Shipping Information', ''),
                        customer_email=row.get('Customer Email', ''),
                        customer_name=row.get('Customer Name', ''),
                        subtotal=row.get('Subtotal', ''),
                        shipping_and_handling=row.get('Shipping and Handling', ''),
                        customer=customer,
                        payment_method=row.get('Payment Method', ''),
                        total_refunded=row.get('Total Refunded', ''),
                        allocated_sources=row.get('Allocated sources', ''),
                        pickup_location_code=row.get('Pickup Location Code', ''),
                        phone_number=row.get('Phone Number', ''),
                        order_note=row.get('Order Note', ''),
                        app_order=row.get('App Order', '')
                    )
                    order.save()
                except Customers.DoesNotExist:
                    print(f"Customer with email {row.get('Customer Email', '')} not found.")
                except Exception as e:
                    print(f"Error saving order: {e}")

                try:
                    related_order_products = order_product_df[order_product_df["ID"] == row['ID']]
                    for _, product_row in related_order_products.iterrows():
                        order_product = OrderProductIntersection(
                            order=order,
                            product_id=product_row.get('Sku', ''),
                            quantity=product_row.get('Quantity', 0),
                            price=product_row.get('Price', 0.0),
                            barcode=product_row.get('Barcode', ''),
                            zip_code=product_row.get('Zip Code', ''),
                            city=product_row.get('City', ''),
                            country=product_row.get('Country', ''),
                            mailchimp_sync=product_row.get('Mailchimp Sync', ''),
                            braintree_transaction_source=product_row.get('Braintree Transaction Source', '')
                        )
                        order_product.save()
                except Exception as e:
                    print(f"Error saving order products: {e}")

            return JsonResponse({'message': f'Orders processed and saved successfully, {num_rows} rows found.'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    else:
        return HttpResponse("This endpoint only accepts POST requests.", status=405)


@csrf_exempt
def ProductView(request, product_id=None):
    if request.method == 'GET':
        if product_id:
            product = get_object_or_404(Product, product_id=product_id)
            product_data = {
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price,
                # Add other fields as needed
            }
            return JsonResponse(product_data)
        else:
            products = Product.objects.all()
            product_list = [{
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price,
                # Other Field
            } for product in products]
            return JsonResponse(product_list, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            df = pd.DataFrame([data])
            print("======DataFrame Created======")
            product_df = df.dropna(how='all', subset=["categories", "product_websites", "name"])
            product_df.drop(columns=['store_view_code', 'categories'], inplace=True, errors='ignore')
            
            
            print("======Product DataFrame======")
            print(product_df)
            print("=============================")
            
            ## ============================================================================================
            
            # product_category_df = df[["sku", "categories"]].copy()
            # product_category_df['categories'] = product_category_df['categories'].str.split(',')
            # product_category_df = product_category_df.explode('categories').reset_index(drop=True)
            
            # print("======Product Category DataFrame======")
            # print(product_category_df)
            # print("=============================")
            
            # store_view_code = df["store_view_code"].unique()
            # store_view_code_df = pd.DataFrame(store_view_code, columns=['store_view_code'])
            # store_view_code_df['store_id'] = range(1, len(store_view_code_df) + 1)
            # store_view_code_df.set_index('store_id', inplace=True)
            
            # print("======Store View Code DataFrame======")
            # print(store_view_code_df)
            # print("=====================================")
            
            # product_storeview_df = df[["sku", "store_view_code"]].copy()
            # product_storeview_df = product_storeview_df.reset_index(drop=True)
            
            # print("======Product StoreView DataFrame======")
            # print(product_storeview_df)
            # print("=======================================")
            
            # categories = list(df["categories"])
            # category_list = list(set([item for sub in categories for item in str(sub).split(',')]))
            # categories_list = list(set([category.replace("Default Category/Categories/", "") for category in category_list]))

            # split_categories = [category.split('/', 3) for category in categories_list]

            # category_df = pd.DataFrame(split_categories, columns=['Main Type', 'Category Type', 'Sub-Category Type', 'Additional Info'])
            # category_df.fillna('', inplace=True)
            
            # print("======Category DataFrame======")
            # print(category_df)
            # print("===============================")
            
            # product_data = product_df.to_dict(orient='records')[0]
            # print(product_data)
            
            # product = Product.objects.create(
            #     product_id=product_data.get('sku'),
            #     store_view_code=product_data.get('store_view_code'),
            #     attribute_set_code=product_data.get('attribute_set_code'),
            #     product_type=product_data.get('product_type'),
            #     categories=product_data.get('categories'),
            #     product_websites=product_data.get('product_websites'),
            #     name=product_data.get('name'),
            #     product_online=product_data.get('product_online'),
            #     tax_class_name=product_data.get('tax_class_name'),
            #     visibility=product_data.get('visibility'),
            #     price=product_data.get('price'),
            #     special_price=product_data.get('special_price'),
            #     url_key=product_data.get('url_key'),
            #     created_at=parse_datetime(product_data.get('created_at')),
            #     updated_at=parse_datetime(product_data.get('updated_at')),
            #     new_from_date=parse_datetime(product_data.get('new_from_date')),
            #     new_to_date=parse_datetime(product_data.get('new_to_date')),
            #     display_product_options_in=product_data.get('display_product_options_in'),
            #     map_price=product_data.get('map_price'),
            #     msrp_price=product_data.get('msrp_price'),
            #     map_enabled=product_data.get('map_enabled'),
            #     gift_message_available=product_data.get('gift_message_available'),
            #     custom_design=product_data.get('custom_design'),
            #     custom_design_from=product_data.get('custom_design_from'),
            #     custom_design_to=product_data.get('custom_design_to'),
            #     custom_layout_update=product_data.get('custom_layout_update'),
            #     page_layout=product_data.get('page_layout'),
            #     product_options_container=product_data.get('product_options_container'),
            #     msrp_display_actual_price_type=product_data.get('msrp_display_actual_price_type'),
            #     country_of_manufacture=product_data.get('country_of_manufacture'),
            #     additional_attributes=product_data.get('additional_attributes'),
            #     qty=product_data.get('qty'),
            #     out_of_stock_qty=product_data.get('out_of_stock_qty'),
            #     use_config_min_qty=product_data.get('use_config_min_qty'),
            #     is_qty_decimal=product_data.get('is_qty_decimal'),
            #     allow_backorders=product_data.get('allow_backorders'),
            #     use_config_backorders=product_data.get('use_config_backorders'),
            #     min_cart_qty=product_data.get('min_cart_qty'),
            #     use_config_min_sale_qty=product_data.get('use_config_min_sale_qty'),
            #     max_cart_qty=product_data.get('max_cart_qty'),
            #     use_config_max_sale_qty=product_data.get('use_config_max_sale_qty'),
            #     is_in_stock=product_data.get('is_in_stock'),
            #     notify_on_stock_below=product_data.get('notify_on_stock_below'),
            #     use_config_notify_stock_qty=product_data.get('use_config_notify_stock_qty'),
            #     manage_stock=product_data.get('manage_stock'),
            #     use_config_manage_stock=product_data.get('use_config_manage_stock'),
            #     use_config_qty_increments=product_data.get('use_config_qty_increments'),
            #     qty_increments=product_data.get('qty_increments'),
            #     use_config_enable_qty_inc=product_data.get('use_config_enable_qty_inc'),
            #     enable_qty_increments=product_data.get('enable_qty_increments'),
            #     is_decimal_divided=product_data.get('is_decimal_divided'),
            #     website_id=product_data.get('website_id'),
            #     related_skus=product_data.get('related_skus'),
            #     related_position=product_data.get('related_position'),
            #     crosssell_skus=product_data.get('crosssell_skus'),
            #     crosssell_position=product_data.get('crosssell_position'),
            #     upsell_skus=product_data.get('upsell_skus'),
            #     upsell_position=product_data.get('upsell_position'),
            #     additional_images=product_data.get('additional_images'),
            #     additional_image_labels=product_data.get('additional_image_labels'),
            #     hide_from_product_page=product_data.get('hide_from_product_page'),
            #     custom_options=product_data.get('custom_options'),
            #     bundle_price_type=product_data.get('bundle_price_type'),
            #     bundle_sku_type=product_data.get('bundle_sku_type'),
            #     bundle_price_view=product_data.get('bundle_price_view'),
            #     bundle_weight_type=product_data.get('bundle_weight_type'),
            #     bundle_values=product_data.get('bundle_values'),
            #     bundle_shipment_type=product_data.get('bundle_shipment_type'),
            #     associated_skus=product_data.get('associated_skus'),
            #     downloadable_links=product_data.get('downloadable_links'),
            #     downloadable_samples=product_data.get('downloadable_samples'),
            #     configurable_variations=product_data.get('configurable_variations'),
            #     configurable_variation_labels=product_data.get('configurable_variation_labels')
            # )
            
            ## ============================================================================================
            
            date_fields = ['created_at', 'updated_at', 'new_from_date', 'new_to_date', 'custom_design_from', 'custom_design_to']
            for field in date_fields:
                if field in product_df.columns:
                    product_df[field] = pd.to_datetime(product_df[field], errors='coerce')
            
            with connection.cursor() as cursor:
                pangres.upsert(
                    con=connection, 
                    df=product_df,
                    table_name='magentoData_product',  
                    if_row_exists='update',
                    create_table=False  
                )
            
            return JsonResponse({"message": "Product created successfully."}, status=201)  # , "product_id": product.product_id
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def CategoryView(request, category_id=None):
    if request.method == 'GET':
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            category_data = {
                "category_id": category.category_id,
                "category": category.category,
                # Other Fields
            }
            return JsonResponse(category_data)
        else:
            categories = Category.objects.all()
            category_list = [{
                "category_id": category.category_id,
                "category": category.category,
                # Other Fields
            } for category in categories]
            return JsonResponse(category_list, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            category = Category.objects.create(
                category_id=data.get('category_id'),
                gender_type=data.get('gender_type'),
                category_type=data.get('category_type'),
                sub_category_type=data.get('sub_category_type'),
                additional_info=data.get('additional_info'),
                category=data.get('category'),
            )
            return JsonResponse({"message": "Category created successfully.", "category_id": category.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body.decode('utf-8'))
            category = get_object_or_404(Category, id=category_id)
            category.gender_type = data.get('gender_type', category.gender_type)
            category.category_type = data.get('category_type', category.category_type)
            category.sub_category_type = data.get('sub_category_type', category.sub_category_type)
            category.additional_info = data.get('additional_info', category.additional_info)
            category.category = data.get('category', category.category)
            # Other Fields
            category.save()
            return JsonResponse({"message": "Category updated successfully."})
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Category not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            return JsonResponse({"message": "Category deleted successfully."})
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Category not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def ProductCategoryIntersectionView(request):
    if request.method == 'GET':
        intersections = ProductCategoryIntersection.objects.all()
        intersection_list = [{
            "product_id": intersection.product_id.product_id,
            "category_id": intersection.category_id.category_id,
            "category": intersection.category,
        } for intersection in intersections]
        return JsonResponse(intersection_list, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            product = get_object_or_404(Product, product_id=data.get('product_id'))
            category = get_object_or_404(Category, category_id=data.get('category_id'))
            intersection = ProductCategoryIntersection.objects.create(
                product_id=product,
                category_id=category,
                category=data.get('category'),
            )
            return JsonResponse({"message": "Intersection created successfully.", "intersection_id": intersection.id}, status=201)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Product or Category not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body.decode('utf-8'))
            intersection = get_object_or_404(ProductCategoryIntersection, id=data.get('intersection_id'))
            intersection.delete()
            return JsonResponse({"message": "Intersection deleted successfully."})
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Intersection not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def inventory_list(request):
    inventories = Inventory.objects.all()
    return render(request, 'inventory_list.html', {'inventories': inventories})

def inventory_detail(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    return render(request, 'inventory_detail.html', {'inventory': inventory})

def StockSource(request):
    if request.method == "POST":
        source_code = request.POST['source_code']
        sku = request.POST['sku']
        status = request.POST['status']
        quantity = request.POST['quantity']
        
        inventory = Inventory.objects.create(
            source_code=source_code,
            sku=sku,
            status=status,
            quantity=quantity
        )
        inventory.save()
    return render(request, 'add_inventory.html')