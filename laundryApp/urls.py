from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('register_user/', views.register_user, name='register_user'),
    # path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('login_user/', views.login_user, name='login_user'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('profile/', views.profile, name='profile'),
    path('users/', views.users, name='users'),
    path('delete_user/<int:pk>',views.delete_user,name='delete-user'),
    path('manage_user',views.manage_user,name='manage-user'),
    path('manage_user/<int:pk>',views.manage_user,name='manage-user-pk'),
    path('save_user',views.save_user,name='save-user'),

    path('update_profile',views.update_profile,name='update-profile'),
    path('update_password',views.update_password,name='update-password'),

    # Laundry category
    path('prices',views.price,name='price-page'),
    path('manage_price',views.manage_price,name='manage-price'),
    path('save_price',views.save_price,name='save-price'),
    path('view_price/<int:pk>',views.view_price,name='view-price-pk'),
    path('manage_price/<int:pk>',views.manage_price,name='manage-price-pk'),
    path('delete_price/<int:pk>',views.delete_price,name='delete-price'),

    # Product List
    path('products',views.products,name='product-page'),
    path('manage_product',views.manage_product,name='manage-product'),
    path('manage_product/<int:pk>',views.manage_product,name='manage-product-pk'),
    path('save_product',views.save_product,name='save-product'),
    path('view_product',views.view_product,name='view-product'),
    path('view_product/<int:pk>',views.view_product,name='view-product-pk'),
    path('delete_product/<int:pk>',views.delete_product,name='delete-product'),

    # Stock Entry
    path('manage_stockin/<int:pid>',views.manage_stockin,name='manage-stockin-pid'),
    path('manage_stockin/<int:pid>/<int:pk>',views.manage_stockin,name='manage-stockin-pid-pk'),
    path('save_stockin',views.save_stockin,name='save-stockin'),
    path('delete_stockin/<int:pk>',views.delete_stockin,name='delete-stockin'),

    # Laundries
    path('laundries',views.laundries,name='laundry-page'),
    path('manage_laundry',views.manage_laundry,name='manage-laundry'),
    path('manage_laundry/<int:pk>',views.manage_laundry,name='manage-laundry-pk'),
    path('view_laundry',views.view_laundry,name='view-laundry'),
    path('view_laundry/<int:pk>',views.view_laundry,name='view-laundry-pk'),
    path('save_laundry',views.save_laundry,name='save-laundry'),
    path('delete_laundry/<int:pk>',views.delete_laundry,name='delete-laundry'),

    
    path('update_transaction_form/<int:pk>',views.update_transaction_form,name='transacton-update-status'),
    path('update_transaction_status',views.update_transaction_status,name='update-laundry-status'),

    # Daily report
    path('daily_report',views.daily_report,name='daily-report'),
    path('daily_report/<str:date>',views.daily_report,name='daily-report-date'),
]
