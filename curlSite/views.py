from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, get_user_model, update_session_auth_hash, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Profile, Department, Employee, Location, Role, Warehouse, ActivityLog, Store
from .forms import ProfileForm, CustomPasswordChangeForm
import json

## Magento Data
from magentoData.models import Customers, Product, StoreCodeProduct, ProductCategoryIntersection


def is_admin(user):
    try:
        employee = Employee.objects.get(user=user)
        return employee.role and employee.role.name == 'admin'
    except Employee.DoesNotExist:
        return False

def log_activity(user, module_name, activity_type, status):
    try:
        employee = Employee.objects.get(user=user)
        ActivityLog.objects.create(
            user=user,
            employee_name=employee.name,
            module_name=module_name,
            activity_type=activity_type,
            employee_role=employee.role.name if employee.role else 'None',
            status=status
        )
    except Employee.DoesNotExist:
        pass


@login_required
@user_passes_test(is_admin)
def view_activity_log(request):
    if request.method == 'GET':
        logs = ActivityLog.objects.all().order_by('-timestamp')
        log_data = [{
            'timestamp': log.timestamp,
            'user': log.user.username,
            'employee_name': log.employee_name,
            'module_name': log.module_name,
            'activity_type': log.activity_type,
            'employee_role': log.employee_role,
            'status': log.status
        } for log in logs]
        return JsonResponse(log_data, status=200, safe=False)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


## ------------------------------------
## Basic Urls - Def Functions
## ------------------------------------

User = get_user_model()

def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return JsonResponse({'message': 'User logged in successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = UserCreationForm(data)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            auth_login(request, user)
            return JsonResponse({'message': 'User registered successfully'}, status=201)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


def forgot_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        try:
            user = User.objects.get(email=email)
            otp = get_random_string(length=6, allowed_chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            user.profile.otp = otp
            user.profile.save()
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is {otp}',
                'untawalegaurav@gmail.com',
                [email],
                fail_silently=False,
            )
            return JsonResponse({'message': 'OTP sent to email'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


def verify_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        try:
            user = User.objects.get(email=email)
            if user.profile.otp == otp:
                user.profile.otp = ''
                user.profile.save()
                return JsonResponse({'message': 'OTP verified'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid OTP'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def profile(request):
    profile = request.user.profile
    profile_data = {
        'bio': profile.bio,
        'location': profile.location,
        'birth_date': profile.birth_date,
        'email': profile.email,
        'full_name': profile.full_name,
        'sync_to_shopify': profile.sync_to_shopify,
        'sync_to_other_source': profile.sync_to_other_source
    }
    return JsonResponse(profile_data, status=200)


@login_required
def update_profile(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = ProfileForm(data, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Profile updated successfully'}, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def change_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = CustomPasswordChangeForm(user=request.user, data=data)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return JsonResponse({'message': 'Password changed successfully'}, status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def update_sync_settings(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        profile = request.user.profile
        profile.sync_to_shopify = data.get('sync_to_shopify', profile.sync_to_shopify)
        profile.sync_to_other_source = data.get('sync_to_other_source', profile.sync_to_other_source)
        profile.save()
        return JsonResponse({'message': 'Sync settings updated successfully'}, status=200)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def sync_data(request):
    if request.method == 'POST':
        # Logic to sync data to Shopify or other sources
        # This is a placeholder for the actual implementation
        return JsonResponse({'message': 'Data synced successfully'}, status=200)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def logout(request):
    auth_logout(request)
    return JsonResponse({'message': 'User logged out successfully'}, status=200)

## ------------------------------------
## Organization Urls - Def Functions
## ------------------------------------

@login_required
def add_department(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        try:
            department = Department.objects.create(name=name, created_by=request.user)
            log_activity(request.user, 'Department', 'Create', 'Success')
            return JsonResponse({'message': 'Department added successfully', 'department_id': department.department_id}, status=201)
        except Exception as e:
            log_activity(request.user, 'Department', 'Create', 'Failure')
            return JsonResponse({'message': 'Failed to add department', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def update_department(request, department_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            department = Department.objects.get(department_id=department_id)
            department.name = data.get('name', department.name)
            department.save()
            log_activity(request.user, 'Department', 'Update', 'Success')
            return JsonResponse({'message': 'Department updated successfully'}, status=200)
        except Department.DoesNotExist:
            log_activity(request.user, 'Department', 'Update', 'Failure')
            return JsonResponse({'error': 'Department not found'}, status=404)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def department_data(request, department_id):
    try:
        department = Department.objects.get(department_id=department_id)
        employees = Employee.objects.filter(department=department)
        employee_data = [{'name': emp.name, 'date_added': emp.date_added} for emp in employees]
        department_data = {
            'name': department.name,
            'department_id': department.department_id,
            'number_of_employees': department.number_of_employees(),
            'created_by': department.created_by.username,
            'date_added': department.date_added,
            'employees': employee_data
        }
        log_activity(request.user, 'Department', 'Display', 'Success')
        return JsonResponse(department_data, status=200)
    except Department.DoesNotExist:
        log_activity(request.user, 'Department', 'Display', 'Failure')
        return JsonResponse({'error': 'Department not found'}, status=404)


@login_required
def all_departments(request):
    departments = Department.objects.filter(created_by=request.user)
    department_data = [{
        'name': dept.name,
        'department_id': dept.department_id,
        'number_of_employees': dept.number_of_employees(),
        'created_by': dept.created_by.username,
        'date_added': dept.date_added
    } for dept in departments]
    return JsonResponse(department_data, status=200, safe=False)


@login_required
def delete_department(request, department_id):
    if request.method == 'DELETE':
        try:
            department = Department.objects.get(department_id=department_id)
            delete_employees = request.GET.get('delete_employees', 'false').lower() == 'true'
            if delete_employees:
                employees = Employee.objects.filter(departments=department)
                for employee in employees:
                    user = User.objects.get(username=employee.email)
                    employee.delete()
                    user.delete()
            else:
                employees = Employee.objects.filter(departments=department)
                for employee in employees:
                    employee.departments.remove(department)
            department.delete()
            log_activity(request.user, 'Department', 'Delete', 'Success')
            return JsonResponse({'message': 'Department deleted successfully'}, status=200)
        except Department.DoesNotExist:
            log_activity(request.user, 'Department', 'Delete', 'Failure')
            return JsonResponse({'error': 'Department not found'}, status=404)
    return JsonResponse({'message': 'Invalid request method'}, status=405)



@login_required
def add_location(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        address = data.get('address')
        manager_id = data.get('manager_id')
        manager_contact = data.get('manager_contact')
        manager_email = data.get('manager_email')
        try:
            manager = Employee.objects.get(id=manager_id)
            location = Location.objects.create(
                name=name,
                address=address,
                manager=manager,
                manager_contact=manager_contact,
                manager_email=manager_email
            )
            log_activity(request.user, 'Location', 'Create', 'Success')
            return JsonResponse({'message': 'Location added successfully', 'location_id': location.location_id}, status=201)
        except Employee.DoesNotExist:
            log_activity(request.user, 'Location', 'Create', 'Failure')
            return JsonResponse({'error': 'Manager not found'}, status=404)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def update_location(request, location_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            location = Location.objects.get(location_id=location_id)
            location.name = data.get('name', location.name)
            location.address = data.get('address', location.address)
            manager_id = data.get('manager_id')
            if manager_id:
                location.manager = Employee.objects.get(id=manager_id)
            location.manager_contact = data.get('manager_contact', location.manager_contact)
            location.manager_email = data.get('manager_email', location.manager_email)
            location.save()
            log_activity(request.user, 'Location', 'Update', 'Success')
            return JsonResponse({'message': 'Location updated successfully'}, status=200)
        except Location.DoesNotExist:
            log_activity(request.user, 'Location', 'Update', 'Failure')
            return JsonResponse({'error': 'Location not found'}, status=404)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def location_data(request, location_id):
    try:
        location = Location.objects.get(location_id=location_id)
        departments = Department.objects.all()
        location_data = {
            'name': location.name,
            'address': location.address,
            'manager': location.manager.name,
            'manager_contact': location.manager_contact,
            'manager_email': location.manager_email,
            'number_of_employees': location.number_of_employees(),
            'date_added': location.date_added,
            'departments': []
        }
        for department in departments:
            employees = Employee.objects.filter(department=department, location=location)
            employee_data = [{'name': emp.name, 'date_added': emp.date_added} for emp in employees]
            location_data['departments'].append({
                'department_name': department.name,
                'employees': employee_data
            })
        log_activity(request.user, 'Location', 'Display', 'Success')
        return JsonResponse(location_data, status=200)
    except Location.DoesNotExist:
        log_activity(request.user, 'Location', 'Display', 'Failure')
        return JsonResponse({'error': 'Location not found'}, status=404)


@login_required
def all_locations(request):
    locations = Location.objects.all()
    location_data = [{
        'name': loc.name,
        'address': loc.address,
        'manager': loc.manager.name,
        'manager_contact': loc.manager_contact,
        'manager_email': loc.manager_email,
        'number_of_employees': loc.number_of_employees(),
        'date_added': loc.date_added
    } for loc in locations]
    log_activity(request.user, 'Location', 'Display', 'Success')
    return JsonResponse(location_data, status=200, safe=False)


@login_required
def delete_location(request, location_id):
    if request.method == 'DELETE':
        try:
            location = Location.objects.get(location_id=location_id)
            delete_employees = request.GET.get('delete_employees', 'false').lower() == 'true'
            if delete_employees:
                employees = Employee.objects.filter(locations=location)
                for employee in employees:
                    user = User.objects.get(username=employee.email)
                    employee.delete()
                    user.delete()
            else:
                employees = Employee.objects.filter(locations=location)
                for employee in employees:
                    employee.locations.remove(location)
            location.delete()
            log_activity(request.user, 'Location', 'Delete', 'Success')
            return JsonResponse({'message': 'Location deleted successfully'}, status=200)
        except Location.DoesNotExist:
            log_activity(request.user, 'Location', 'Delete', 'Failure')
            return JsonResponse({'error': 'Location not found'}, status=404)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def add_employee(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            name = data.get('name')
            contact = data.get('contact')
            email = data.get('email')
            address = data.get('address')
            role_id = data.get('role_id')
            department_ids = data.get('department_ids', [])
            location_ids = data.get('location_ids', [])
            password = f"{name[:3]}@{contact[-4:]}"
            user = User.objects.create_user(username=email, email=email, password=password)
            role = Role.objects.get(id=role_id) if role_id else None
            employee = Employee.objects.create(
                name=name,
                contact=contact,
                email=email,
                address=address,
                role=role,
                user=user
            )
            employee.departments.set(Department.objects.filter(department_id__in=department_ids))
            employee.locations.set(Location.objects.filter(location_id__in=location_ids))
            log_activity(request.user, 'Employee', 'Create', 'Success')
            return JsonResponse({'message': 'Employee added successfully', 'employee_id': employee.employee_id}, status=201)
        except Exception as e:
            log_activity(request.user, 'Employee', 'Create', 'Failure')
            return JsonResponse({'message': 'Failed to add employee', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def update_employee(request, employee_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            employee = get_object_or_404(Employee, employee_id=employee_id)
            employee.name = data.get('name', employee.name)
            employee.contact = data.get('contact', employee.contact)
            employee.email = data.get('email', employee.email)
            employee.address = data.get('address', employee.address)
            role_id = data.get('role_id')
            if role_id:
                employee.role = get_object_or_404(Role, id=role_id)
            department_ids = data.get('department_ids', [])
            location_ids = data.get('location_ids', [])
            employee.departments.set(Department.objects.filter(department_id__in=department_ids))
            employee.locations.set(Location.objects.filter(location_id__in=location_ids))
            employee.save()
            log_activity(request.user, 'Employee', 'Update', 'Success')
            return JsonResponse({'message': 'Employee updated successfully'}, status=200)
        except Exception as e:
            log_activity(request.user, 'Employee', 'Update', 'Failure')
            return JsonResponse({'message': 'Failed to update employee', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def all_employees(request):
    if request.method == 'GET':
        try:
            employees = Employee.objects.all()
            employee_data = [{
                'name': emp.name,
                'employee_id': emp.employee_id,
                'contact': emp.contact,
                'email': emp.email,
                'address': emp.address,
                'date_added': emp.date_added,
                'role': emp.role.name if emp.role else None,
                'departments': [dept.name for dept in emp.departments.all()],
                'locations': [loc.name for loc in emp.locations.all()]
            } for emp in employees]
            log_activity(request.user, 'Employee', 'Display', 'Success')
            return JsonResponse(employee_data, status=200, safe=False)
        except Exception as e:
            log_activity(request.user, 'Employee', 'Display', 'Failure')
            return JsonResponse({'message': 'Failed to retrieve employees', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def delete_employee(request, employee_id):
    if request.method == 'DELETE':
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            user = User.objects.get(username=employee.email)
            employee.delete()
            user.delete()
            log_activity(request.user, 'Employee', 'Delete', 'Success')
            return JsonResponse({'message': 'Employee deleted successfully'}, status=200)
        except Exception as e:
            log_activity(request.user, 'Employee', 'Delete', 'Failure')
            return JsonResponse({'message': 'Failed to delete employee', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def add_role(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            name = data.get('name')
            role = Role.objects.create(
                name=name,
                access_control_1=data.get('access_control_1', False),
                access_control_2=data.get('access_control_2', False),
                access_control_3=data.get('access_control_3', False),
                access_control_4=data.get('access_control_4', False),
                access_control_5=data.get('access_control_5', False),
                access_control_6=data.get('access_control_6', False)
            )
            log_activity(request.user, 'Role', 'Create', 'Success')
            return JsonResponse({'message': 'Role added successfully', 'role_id': role.id}, status=201)
        except Exception as e:
            log_activity(request.user, 'Role', 'Create', 'Failure')
            return JsonResponse({'message': 'Failed to add role', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def update_role(request, role_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            role = get_object_or_404(Role, id=role_id)
            role.name = data.get('name', role.name)
            role.access_control_1 = data.get('access_control_1', role.access_control_1)
            role.access_control_2 = data.get('access_control_2', role.access_control_2)
            role.access_control_3 = data.get('access_control_3', role.access_control_3)
            role.access_control_4 = data.get('access_control_4', role.access_control_4)
            role.access_control_5 = data.get('access_control_5', role.access_control_5)
            role.access_control_6 = data.get('access_control_6', role.access_control_6)
            role.save()
            log_activity(request.user, 'Role', 'Update', 'Success')
            return JsonResponse({'message': 'Role updated successfully'}, status=200)
        except Exception as e:
            log_activity(request.user, 'Role', 'Update', 'Failure')
            return JsonResponse({'message': 'Failed to update role', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)



@login_required
def all_roles(request):
    if request.method == 'GET':
        try:
            roles = Role.objects.all()
            role_data = [{
                'id': role.id,
                'name': role.name,
                'access_control_1': role.access_control_1,
                'access_control_2': role.access_control_2,
                'access_control_3': role.access_control_3,
                'access_control_4': role.access_control_4,
                'access_control_5': role.access_control_5,
                'access_control_6': role.access_control_6
            } for role in roles]
            log_activity(request.user, 'Role', 'Display', 'Success')
            return JsonResponse(role_data, status=200, safe=False)
        except Exception as e:
            log_activity(request.user, 'Role', 'Display', 'Failure')
            return JsonResponse({'message': 'Failed to retrieve roles', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def delete_role(request, role_id):
    if request.method == 'DELETE':
        try:
            role = Role.objects.get(id=role_id)
            employees = Employee.objects.filter(role=role)
            for employee in employees:
                employee.role = None
                employee.save()
            role.delete()
            log_activity(request.user, 'Role', 'Delete', 'Success')
            return JsonResponse({'message': 'Role deleted successfully'}, status=200)
        except Exception as e:
            log_activity(request.user, 'Role', 'Delete', 'Failure')
            return JsonResponse({'message': 'Failed to delete role', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


## ----------------------------------------
## Product Catelog Urls - Def Functions
## ----------------------------------------

@login_required
def get_product(request, product_id):
    if request.method == 'GET':
        try:
            product = get_object_or_404(Product, product_id=product_id)
            store_codes = StoreCodeProduct.objects.filter(product=product).values_list('store_code', flat=True)
            categories = ProductCategoryIntersection.objects.filter(product=product).values_list('category', flat=True)
            product_data = {
                'product_id': product.product_id,
                'attribute_set_code': product.attribute_set_code,
                'product_type': product.product_type,
                'product_websites': product.product_websites,
                'name': product.name,
                'price': product.price,
                'special_price': product.special_price,
                'url_key': product.url_key,
                'created_at': product.created_at,
                'updated_at': product.updated_at,
                'new_from_date': product.new_from_date,
                'new_to_date': product.new_to_date,
                'map_price': product.map_price,
                'msrp_price': product.msrp_price,
                'country_of_manufacture': product.country_of_manufacture,
                'qty': product.qty,
                'out_of_stock_qty': product.out_of_stock_qty,
                'additional_images': product.additional_images,
                'additional_image_labels': product.additional_image_labels,
                'store_codes': list(store_codes),
                'categories': list(categories)
            }
            log_activity(request.user, 'Product', 'Display', 'Success')
            return JsonResponse(product_data, status=200)
        except Exception as e:
            log_activity(request.user, 'Product', 'Display', 'Failure')
            return JsonResponse({'message': 'Failed to retrieve product', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def add_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            product = Product.objects.create(
                product_id=data['product_id'],
                attribute_set_code=data['attribute_set_code'],
                product_type=data['product_type'],
                product_websites=data.get('product_websites'),
                name=data['name'],
                price=data.get('price'),
                special_price=data.get('special_price'),
                url_key=data.get('url_key'),
                new_from_date=data.get('new_from_date'),
                new_to_date=data.get('new_to_date'),
                map_price=data.get('map_price'),
                msrp_price=data.get('msrp_price'),
                country_of_manufacture=data.get('country_of_manufacture'),
                qty=data.get('qty'),
                out_of_stock_qty=data.get('out_of_stock_qty', False),
                additional_images=data.get('additional_images'),
                additional_image_labels=data.get('additional_image_labels'),
            )
            store_codes = data.get('store_codes', [])
            categories = data.get('categories', [])
            for store_code in store_codes:
                StoreCodeProduct.objects.create(product=product, store_code=store_code)
            for category in categories:
                ProductCategoryIntersection.objects.create(product=product, category=category)
            log_activity(request.user, 'Product', 'Create', 'Success')
            return JsonResponse({'message': 'Product added successfully', 'product_id': product.product_id}, status=201)
        except Exception as e:
            log_activity(request.user, 'Product', 'Create', 'Failure')
            return JsonResponse({'message': 'Failed to add product', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def update_product(request, product_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            product = get_object_or_404(Product, product_id=product_id)
            product.attribute_set_code = data.get('attribute_set_code', product.attribute_set_code)
            product.product_type = data.get('product_type', product.product_type)
            product.product_websites = data.get('product_websites', product.product_websites)
            product.name = data.get('name', product.name)
            product.price = data.get('price', product.price)
            product.special_price = data.get('special_price', product.special_price)
            product.url_key = data.get('url_key', product.url_key)
            product.new_from_date = data.get('new_from_date', product.new_from_date)
            product.new_to_date = data.get('new_to_date', product.new_to_date)
            product.map_price = data.get('map_price', product.map_price)
            product.msrp_price = data.get('msrp_price', product.msrp_price)
            product.country_of_manufacture = data.get('country_of_manufacture', product.country_of_manufacture)
            product.qty = data.get('qty', product.qty)
            product.out_of_stock_qty = data.get('out_of_stock_qty', product.out_of_stock_qty)
            product.additional_images = data.get('additional_images', product.additional_images)
            product.additional_image_labels = data.get('additional_image_labels', product.additional_image_labels)
            product.save()
            StoreCodeProduct.objects.filter(product=product).delete()
            ProductCategoryIntersection.objects.filter(product=product).delete()
            store_codes = data.get('store_codes', [])
            categories = data.get('categories', [])
            for store_code in store_codes:
                StoreCodeProduct.objects.create(product=product, store_code=store_code)
            for category in categories:
                ProductCategoryIntersection.objects.create(product=product, category=category)
            log_activity(request.user, 'Product', 'Update', 'Success')
            return JsonResponse({'message': 'Product updated successfully'}, status=200)
        except Exception as e:
            log_activity(request.user, 'Product', 'Update', 'Failure')
            return JsonResponse({'message': 'Failed to update product', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def delete_product(request, product_id):
    if request.method == 'DELETE':
        try:
            product = get_object_or_404(Product, product_id=product_id)
            product.delete()
            log_activity(request.user, 'Product', 'Delete', 'Success')
            return JsonResponse({'message': 'Product deleted successfully'}, status=200)
        except Exception as e:
            log_activity(request.user, 'Product', 'Delete', 'Failure')
            return JsonResponse({'message': 'Failed to delete product', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)

## ----------------------------------------
## Warehouse Urls - Def Functions
## ----------------------------------------

@login_required
def add_warehouse(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            warehouse = Warehouse.objects.create(
                name=data['name'],
                country=data['country'],
                address=data['address'],
                city=data['city'],
                state=data['state'],
                pincode=data['pincode'],
                contact_person_name=data['contact_person_name'],
                contact=data['contact'],
                email=data['email']
            )
            log_activity(request.user, 'Warehouse', 'Create', 'Success')
            return JsonResponse({'message': 'Warehouse added successfully', 'warehouse_id': warehouse.warehouse_id}, status=201)
        except Exception as e:
            log_activity(request.user, 'Warehouse', 'Create', 'Failure')
            return JsonResponse({'message': 'Failed to add warehouse', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def update_warehouse(request, warehouse_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)
            warehouse.name = data.get('name', warehouse.name)
            warehouse.country = data.get('country', warehouse.country)
            warehouse.address = data.get('address', warehouse.address)
            warehouse.city = data.get('city', warehouse.city)
            warehouse.state = data.get('state', warehouse.state)
            warehouse.pincode = data.get('pincode', warehouse.pincode)
            warehouse.contact_person_name = data.get('contact_person_name', warehouse.contact_person_name)
            warehouse.contact = data.get('contact', warehouse.contact)
            warehouse.email = data.get('email', warehouse.email)
            warehouse.save()
            log_activity(request.user, 'Warehouse', 'Update', 'Success')
            return JsonResponse({'message': 'Warehouse updated successfully'}, status=200)
        except Exception as e:
            log_activity(request.user, 'Warehouse', 'Update', 'Failure')
            return JsonResponse({'message': 'Failed to update warehouse', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def delete_warehouse(request, warehouse_id):
    if request.method == 'DELETE':
        try:
            warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)
            warehouse.delete()
            log_activity(request.user, 'Warehouse', 'Delete', 'Success')
            return JsonResponse({'message': 'Warehouse deleted successfully'}, status=200)
        except Exception as e:
            log_activity(request.user, 'Warehouse', 'Delete', 'Failure')
            return JsonResponse({'message': 'Failed to delete warehouse', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def all_warehouses(request):
    if request.method == 'GET':
        warehouses = Warehouse.objects.all()
        warehouse_data = [{
            'warehouse_id': wh.warehouse_id,
            'name': wh.name,
            'country': wh.country,
            'address': wh.address,
            'city': wh.city,
            'state': wh.state,
            'pincode': wh.pincode
        } for wh in warehouses]
        log_activity(request.user, 'Warehouse', 'Display', 'Success')
        return JsonResponse(warehouse_data, status=200, safe=False)
    log_activity(request.user, 'Warehouse', 'Display', 'Failure')
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def get_warehouse(request, warehouse_id):
    if request.method == 'GET':
        try:
            warehouse = get_object_or_404(Warehouse, warehouse_id=warehouse_id)
            warehouse_data = {
                'warehouse_id': warehouse.warehouse_id,
                'name': warehouse.name,
                'country': warehouse.country,
                'address': warehouse.address,
                'city': warehouse.city,
                'state': warehouse.state,
                'pincode': warehouse.pincode,
                'contact_person_name': warehouse.contact_person_name,
                'contact': warehouse.contact,
                'email': warehouse.email
            }
            log_activity(request.user, 'Warehouse', 'Display', 'Success')
            return JsonResponse(warehouse_data, status=200)
        except Exception as e:
            log_activity(request.user, 'Warehouse', 'Display', 'Failure')
            return JsonResponse({'message': 'Failed to retrieve warehouse', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)



## ----------------------------------------
## Store Management Urls - Def Functions
## ----------------------------------------


@login_required
def add_store(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            store = Store.objects.create(
                name=data['name'],
                country=data['country'],
                city=data['city'],
                state=data['state'],
                pincode=data['pincode'],
                contact_person_name=data['contact_person_name'],
                contact=data['contact'],
                email=data['email']
            )
            products = data.get('products', [])
            for product_id in products:
                product = Product.objects.get(id=product_id)
                store.products.add(product)
            log_activity(request.user, 'Store', 'Create', 'Success')
            return JsonResponse({'message': 'Store added successfully', 'store_id': store.store_id}, status=201)
        except Exception as e:
            log_activity(request.user, 'Store', 'Create', 'Failure')
            return JsonResponse({'message': 'Failed to add store', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)

@login_required
def update_store(request, store_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        try:
            store = get_object_or_404(Store, store_id=store_id)
            store.name = data.get('name', store.name)
            store.country = data.get('country', store.country)
            store.city = data.get('city', store.city)
            store.state = data.get('state', store.state)
            store.pincode = data.get('pincode', store.pincode)
            store.contact_person_name = data.get('contact_person_name', store.contact_person_name)
            store.contact = data.get('contact', store.contact)
            store.email = data.get('email', store.email)
            store.save()
            store.products.clear()
            products = data.get('products', [])
            for product_id in products:
                product = Product.objects.get(id=product_id)
                store.products.add(product)
            log_activity(request.user, 'Store', 'Update', 'Success')
            return JsonResponse({'message': 'Store updated successfully'}, status=200)
        except Exception as e:
            log_activity(request.user, 'Store', 'Update', 'Failure')
            return JsonResponse({'message': 'Failed to update store', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)

@login_required
def delete_store(request, store_id):
    if request.method == 'DELETE':
        try:
            store = get_object_or_404(Store, store_id=store_id)
            store.delete()
            log_activity(request.user, 'Store', 'Delete', 'Success')
            return JsonResponse({'message': 'Store deleted successfully'}, status=200)
        except Exception as e:
            log_activity(request.user, 'Store', 'Delete', 'Failure')
            return JsonResponse({'message': 'Failed to delete store', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)

@login_required
def all_stores(request):
    if request.method == 'GET':
        stores = Store.objects.all()
        store_data = [{
            'store_id': store.store_id,
            'name': store.name,
            'country': store.country,
            'city': store.city,
            'state': store.state,
            'pincode': store.pincode,
            'products': [product.name for product in store.products.all()]
        } for store in stores]
        log_activity(request.user, 'Store', 'Display', 'Success')
        return JsonResponse(store_data, status=200, safe=False)
    log_activity(request.user, 'Store', 'Display', 'Failure')
    return JsonResponse({'message': 'Invalid request method'}, status=405)

@login_required
def get_store(request, store_name):
    if request.method == 'GET':
        try:
            store = get_object_or_404(Store, name=store_name)
            store_data = {
                'store_id': store.store_id,
                'name': store.name,
                'country': store.country,
                'city': store.city,
                'state': store.state,
                'pincode': store.pincode,
                'products': [product.name for product in store.products.all()],
                'contact_person_name': store.contact_person_name,
                'contact': store.contact,
                'email': store.email
            }
            log_activity(request.user, 'Store', 'Display', 'Success')
            return JsonResponse(store_data, status=200)
        except Exception as e:
            log_activity(request.user, 'Store', 'Display', 'Failure')
            return JsonResponse({'message': 'Failed to retrieve store', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)


@login_required
def get_store_with_products(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        store_name = data.get('store_name')
        try:
            store = get_object_or_404(Store, name=store_name)
            products = store.products.all()
            product_data = []
            for product in products:
                product_info = {
                    'name': product.name,
                    'price': product.price,
                    'description': product.description,
                    'sku': product.sku,
                    'quantity': product.quantity,
                    'category': product.category.name if product.category else None
                }
                product_data.append(product_info)
            store_data = {
                'store_id': store.store_id,
                'name': store.name,
                'country': store.country,
                'city': store.city,
                'state': store.state,
                'pincode': store.pincode,
                'products': product_data,
                'contact_person_name': store.contact_person_name,
                'contact': store.contact,
                'email': store.email
            }
            log_activity(request.user, 'Store', 'Display', 'Success')
            return JsonResponse(store_data, status=200)
        except Exception as e:
            log_activity(request.user, 'Store', 'Display', 'Failure')
            return JsonResponse({'message': 'Failed to retrieve store', 'error': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method'}, status=405)