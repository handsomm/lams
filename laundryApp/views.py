from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import LoginForm, RegisterForm
from . import forms, models
from .models import User

from django.db.models import Q, Sum
# from django.contrib.auth.decorators import login_required

# Create your views here.
# Default Context


def context_data(request):
    fullpath = request.get_full_path()
    abs_uri = request.build_absolute_uri()
    abs_uri = abs_uri.split(fullpath)[0]
    context = {
        'system_host': abs_uri,
        'page_name': '',
        'page_title': '',
        'system_name': 'Laundry Shop Managament System',
        'system_short_name': 'LSMS',
        'sidebar': True,
        'footer_view': True,
    }
    return context

# Register


def register_page(request):
    if not request.user.is_authenticated:
        context = context_data(request)
        context['page_title'] = 'Register'
        context['sidebar'] = False
        context['footer_view'] = False
        fm = RegisterForm()
        context['form'] = fm
        return render(request, 'laundry/register.html', context)
    else:
        return redirect('dashboard')

# Register User


def register_user(request):
    logout(request)
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            resp['status'] = 'success'
            messages.success(request, "User created successfully.")
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")
# Dashboard Page


def dashboard(request):
    if request.user.is_authenticated:
        context = context_data(request)
        context['page_title'] = 'Dashboard'
        context['page_name'] = 'Dashboard'

        date = datetime.datetime.now()
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')

        if request.user.status == 'admin':
            context['users'] = User.objects.exclude(
                pk=request.user.id).filter(is_superuser=False).all().count()
            context['prices'] = models.Prices.objects.filter(delete_flag=0).count()
            context['products'] = models.Products.objects.filter(
                delete_flag=0).count()
            context['todays_transaction'] = models.Laundry.objects.filter(
                date_added__year=year,
                date_added__month=month,
                date_added__day=day,
            ).count()
            context['todays_sales'] = models.Laundry.objects.filter(
                date_added__year=year,
                date_added__month=month,
                date_added__day=day,
            ).aggregate(Sum('total_amount'))['total_amount__sum']
            return render(request, 'laundry/dashboard.html', context)
        else:
            context['prices'] = models.Prices.objects.filter(delete_flag=0).count()
            context['products'] = models.Products.objects.filter(
                delete_flag=0).count()
            context['laundries'] = models.Laundry.objects.filter(client=request.user.get_full_name()).count()
            return render(request, 'user/user_dashboard.html', context)
    else:
        return redirect('login')

# Login Page redirect


def login_page(request):
    if not request.user.is_authenticated:
        context = context_data(request)
        context['page_title'] = 'Login'
        context['sidebar'] = False
        context['footer_view'] = False
        fm = LoginForm()
        context['form'] = fm
        return render(request, 'laundry/login.html', context)
    else:
        return redirect('dashboard')

# User login


def login_user(request):
    logout(request)
    resp = {'status': 'failed', 'msg': '', 'user':''}

    username = ''
    password = ''

    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        flag = User.objects.filter(username=username)
        if flag:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                resp['status'] = 'success'
                resp['user'] = user.status
                messages.success(request, 'Login successful')
            else:
                resp['msg'] = 'Incorrect Password'

        else:
            resp['msg'] = 'Incorrect Username'
    return HttpResponse(json.dumps(resp), content_type='application/json')

# User logout


def logout_user(request):
    logout(request)
    return redirect('login')


def profile(request):
    if request.user.is_authenticated:
        context = context_data(request)
        context['page_title'] = 'Profile'
        context['page_name'] = 'Profile'
        if request.user.status == 'admin':
            return render(request, 'laundry/profile.html', context)
        else:
            return render(request, 'user/profile.html', context)
    else:
        return redirect('login')

# Users


def users(request):
    if request.user.is_authenticated:
        context = context_data(request)
        context['page_title'] = 'Users'
        context['page_name'] = 'Users'
        context['users'] = User.objects.exclude(
            pk=request.user.id).filter(is_superuser=False).all()
        return render(request, 'laundry/users.html', context)
    else:
        return redirect('login')

# Manage user


def manage_user(request, pk=None):
    context = context_data(request)
    context['page_name'] = 'Manage User'
    context['page_title'] = 'Manage User'
    if pk is None:
        context['user'] = {}
    else:
        context['user'] = User.objects.get(id=pk)

    return render(request, 'laundry/manage_user.html', context)

# Save user


def save_user(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            user = User.objects.get(id=post['id'])
            form = forms.UpdateUser(request.POST, instance=user)
        else:
            form = forms.SaveUser(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "User has been saved successfully.")
            else:
                messages.success(
                    request, "User has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


# Delete user
def delete_user(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'User ID is invalid'
    else:
        try:
            User.objects.filter(pk=pk).delete()
            messages.success(request, "User has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting User Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# Update profile


def update_profile(request):
    context = context_data(request)
    context['page_name'] = 'Update Profile'
    context['page_title'] = 'Update Profile'

    user = User.objects.get(id=request.user.id)
    if not request.method == 'POST':
        form = forms.UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = forms.UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile")
        else:
            context['form'] = form
    if request.user.status == 'admin':
        return render(request, 'laundry/manage_profile.html', context)
    else:
        return render(request, 'user/manage_profile.html', context)

# Update password


def update_password(request):
    context = context_data(request)
    context['page_name'] = 'Update Password'
    context['page_title'] = 'Update Password'
    if request.method == 'POST':
        form = forms.UpdatePasswords(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = forms.UpdatePasswords(request.POST)
        context['form'] = form
    if request.user.status == 'admin':
        return render(request, 'laundry/update_password.html', context)
    else:
        return render(request, 'user/update_password.html', context)


# Laundry category
def price(request):
    context = context_data(request)
    context['page_name'] = 'Price List'
    context['page_title'] = 'Price List'
    context['prices'] = models.Prices.objects.filter(delete_flag=0).all()
    if request.user.status == 'admin':
        return render(request, 'laundry/prices.html', context)
    else:
        return render(request, 'user/prices.html', context)


# Manage Price
def manage_price(request, pk=None):
    context = context_data(request)
    context['page_name'] = 'Manage Price'
    context['page_title'] = 'Manage price'
    if pk is None:
        context['price'] = {}
    else:
        context['price'] = models.Prices.objects.get(id=pk)

    return render(request, 'laundry/manage_price.html', context)

# Save price


def save_price(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            price = models.Prices.objects.get(id=post['id'])
            form = forms.SavePrice(request.POST, instance=price)
        else:
            form = forms.SavePrice(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Price has been saved successfully.")
            else:
                messages.success(
                    request, "Price has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# View Price


def view_price(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_price'
    context['page_title'] = 'View Price'
    if pk is None:
        context['price'] = {}
    else:
        context['price'] = models.Prices.objects.get(id=pk)

    return render(request, 'laundry/view_price.html', context)

# Delete price


def delete_price(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Price ID is invalid'
    else:
        try:
            models.Prices.objects.filter(pk=pk).update(delete_flag=1)
            messages.success(request, "Price has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Price Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# Products


def products(request):
    context = context_data(request)
    context['page_name'] = 'Product List'
    context['page_title'] = 'Product List'
    context['products'] = models.Products.objects.filter(delete_flag=0).all()
    if request.user.status == 'admin':
        return render(request, 'laundry/products.html', context)
    else:
        return render(request, 'user/products.html', context)

# Manage Product


def manage_product(request, pk=None):
    context = context_data(request)
    context['page_name'] = 'Manage product'
    context['page_title'] = 'Manage product'
    if pk is None:
        context['product'] = {}
    else:
        context['product'] = models.Products.objects.get(id=pk)

    return render(request, 'laundry/manage_product.html', context)

# Save Product


def save_product(request):
    resp = {'status': 'failed', 'msg': '', 'id': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            product = models.Products.objects.get(id=post['id'])
            form = forms.SaveProducts(request.POST, instance=product)
        else:
            form = forms.SaveProducts(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(
                    request, "Product has been saved successfully.")
                pid = models.Products.objects.last().id
                resp['id'] = pid
            else:
                messages.success(
                    request, "Product has been updated successfully.")
                resp['id'] = post['id']
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# View Product


def view_product(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_product'
    context['page_title'] = 'View Product'
    if pk is None:
        context['product'] = {}
        context['stockins'] = {}
    else:
        context['product'] = models.Products.objects.get(id=pk)
        context['stockins'] = models.StockIn.objects.filter(product__id=pk)
        context['stockouts'] = models.LaundryProducts.objects.filter(
            product__id=pk).order_by('laundry__code')

    return render(request, 'laundry/view_product.html', context)

# Manage Stock in


def manage_stockin(request, pid=None, pk=None):
    context = context_data(request)
    context['page_name'] = 'Manage Stockin'
    context['page_title'] = 'Manage Stockin'
    context['pid'] = pid
    print(pid)
    print(pk)
    if pk is None:
        context['stockin'] = {}
    else:
        context['stockin'] = models.StockIn.objects.get(id=pk)

    return render(request, 'laundry/manage_stockin.html', context)

# Delete Product


def delete_product(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Product ID is invalid'
    else:
        try:
            models.Products.objects.filter(pk=pk).update(delete_flag=1)
            messages.success(request, "Product has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Product Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# Save Stock In


def save_stockin(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            stockin = models.StockIn.objects.get(id=post['id'])
            form = forms.SaveStockIn(request.POST, instance=stockin)
        else:
            form = forms.SaveStockIn(request.POST)

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(
                    request, "Stock Entry has been saved successfully.")
            else:
                messages.success(
                    request, "Stock Entry has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# Delete Stock in


def delete_stockin(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Stock-in ID is invalid'
    else:
        try:
            models.StockIn.objects.filter(pk=pk).delete()
            messages.success(
                request, "Stock Entry Details has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Stock Entry Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# Laundries


def laundries(request):
    context = context_data(request)
    context['page_name'] = 'Laundry List'
    context['page_title'] = "Laundry List"
    context['laundries'] = models.Laundry.objects.order_by('-date_added').all()
    
    if request.user.status == 'admin':
        return render(request, 'laundry/laundries.html', context)
    else:
        return render(request, 'user/laundries.html', context)


# Manage Laundry
def manage_laundry(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_laundry'
    context['page_title'] = 'Manage laundry'
    context['products'] = models.Products.objects.filter(
        delete_flag=0, status=1).all()
    context['prices'] = models.Prices.objects.filter(
        delete_flag=0, status=1).all()
    if pk is None:
        context['laundry'] = {}
        context['items'] = {}
        context['pitems'] = {}
    else:
        context['laundry'] = models.Laundry.objects.get(id=pk)
        context['items'] = models.LaundryItems.objects.filter(
            laundry__id=pk).all()
        context['pitems'] = models.LaundryProducts.objects.filter(
            laundry__id=pk).all()
    if request.user.status == 'admin':
        return render(request, 'laundry/manage_laundry.html', context)
    else:
        return render(request, 'user/manage_laundry.html', context)


# View Laundry
def view_laundry(request, pk=None):
    context = context_data(request)
    context['page_name'] = 'View Laundry'
    context['page_title'] = 'View Laundry'
    if pk is None:
        context['laundry'] = {}
        context['items'] = {}
        context['pitems'] = {}
    else:
        context['laundry'] = models.Laundry.objects.get(id=pk)
        context['items'] = models.LaundryItems.objects.filter(
            laundry__id=pk).all()
        context['pitems'] = models.LaundryProducts.objects.filter(
            laundry__id=pk).all()
    if request.user.status == 'admin':
        return render(request, 'laundry/view_laundry.html', context)
    else:
        return render(request, 'user/view_laundry.html', context)


# Save Laundry


def save_laundry(request):
    resp = {'status': 'failed', 'msg': '', 'id': ''}
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            laundry = models.Laundry.objects.get(id=post['id'])
            form = forms.SaveLaundry(request.POST, instance=laundry)
        else:
            form = forms.SaveLaundry(request.POST)
        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(
                    request, "Laundry has been saved successfully.")
                pid = models.Laundry.objects.last().id
                resp['id'] = pid
            else:
                messages.success(
                    request, "Laundry has been updated successfully.")
                resp['id'] = post['id']
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# Delete Laundry


def delete_laundry(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}
    if pk is None:
        resp['msg'] = 'Laundry ID is invalid'
    else:
        try:
            models.Laundry.objects.filter(pk=pk).delete()
            messages.success(request, "Laundry has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Laundry Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# Update Transaction form


def update_transaction_form(request, pk=None):
    context = context_data(request)
    context['page'] = 'update_laundry'
    context['page_title'] = 'Update Transaction'
    if pk is None:
        context['laundry'] = {}
    else:
        context['laundry'] = models.Laundry.objects.get(id=pk)

    return render(request, 'laundry/update_status.html', context)


def update_transaction_status(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.POST['id'] is None:
        resp['msg'] = 'Transaction ID is invalid'
    else:
        try:
            models.Laundry.objects.filter(pk=request.POST['id']).update(
                status=request.POST['status'])
            messages.success(
                request, "Transaction Status has been updated successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Transaction Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# Daily report


def daily_report(request, date=None):
    context = context_data(request)
    context['page'] = 'view_laundry'
    context['page_title'] = 'Daily Transaction Report'

    if date is None:
        date = datetime.datetime.now()
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
    else:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')

    context['date'] = date
    context['laundries'] = models.Laundry.objects.filter(
        date_added__year=year,
        date_added__month=month,
        date_added__day=day,
    )
    grand_total = 0
    for laundry in context['laundries']:
        grand_total += float(laundry.total_amount)
    context['grand_total'] = grand_total

    return render(request, 'laundry/report.html', context)
