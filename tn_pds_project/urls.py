"""
URL configuration for tn_pds_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tn_pds_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('',views.welcome,name='welcome'),
    path('',views.home,name='home'),

    path('common_signup_login/',views.common_signup_login_views,name='common_signup_login'),

    path('consumer_signup/',views.consumer_signup_views,name='consumer_signup'),
    path('consumer_login/',views.consumer_login_views,name='consumer_login'),
    path('consumer_logout/',views.consumer_logout_views,name='consumer_logout'),

    path('consumer_profile/',views.consumer_profile_views,name='consumer_profile'),
    path('consumer_forgot_password/', views.consumer_forgot_password_views, name='consumer_forgot_password'),
    path('consumer_purchase_history/', views.consumer_purchase_history_views, name='consumer_purchase_history'),
    path('consumer_allocation_details/', views.consumer_allocation_details_views, name='consumer_allocation_details'),
    path('consumer_edit_family_member<int:member_id>/', views.consumer_edit_family_member_views, name='consumer_edit_family_member'),
    path('consumer_delete_family_member/<int:member_id>/', views.consumer_delete_family_member_views, name='consumer_delete_family_member'),

    path('consumer_home_page/',views.consumer_home_page_views,name='consumer_home_page'),
    path('consumer_product_details/',views.consumer_product_details_views,name='consumer_product_details'),
    path('add_to_cart/<int:commodity_id>/',views.add_to_cart_views,name='add_to_cart'),
    path('remove_from_cart/<int:commodity_id>/',views.remove_from_cart_views,name='remove_from_cart'),
    path('checkout_bill/', views.checkout_bill_views, name='checkout_bill'),

    path('cart/',views.cart_views,name='cart'),



    path('shop_worker_signup/',views.shop_worker_signup_views,name='shop_worker_signup'),
    path('shop_worker_login/',views.shop_worker_login_views,name='shop_worker_login'),
    path('shop_worker_logout/',views.shop_worker_logout_views,name='shop_worker_logout'),
    path('shop_profile/', views.shop_profile_views, name='shop_profile'),

    path('shop_home_page/',views.shop_home_page_views,name='shop_home_page'),
    path('shop_product_details/',views.shop_product_details_views,name='shop_product_details'),
    path('shop_add_commodity/',views.shop_add_commodity,name='shop_add_commodity'),
    path('shop_edit_commodity/<int:item_id>/', views.shop_edit_commodity_views, name='shop_edit_commodity'),
    path('shop_delete_commodity/<int:item_id>/', views.shop_delete_commodity_views, name='shop_delete_commodity'),
    path('shop_stock_dashboard/', views.shop_stock_dashboard_views, name='shop_stock_dashboard'),
    path('shop_order_search/', views.shop_order_search_views, name='shop_order_search'),
    path('shop_order_delivery/<str:token_number>/', views.shop_order_delivery_views, name='shop_order_delivery'),

    path('officer_signup/',views.officer_signup_views,name='officer_signup'),
    path('officer_login/',views.officer_login_views,name='officer_login'),
    path('officer_logout/',views.officer_logout_views,name='officer_logout'),



    path('officer_home_page/',views.officer_home_page_views,name='officer_home_page'),
    path('officer_profile/',views.officer_profile_views,name='officer_profile'),
    path('officer_pending_request/',views.officer_pending_request_views,name='officer_pending_request'),
    path('officer_audit_history/',views.officer_audit_history_views,name='officer_audit_history'),
    path('officer_review_edit_request/<int:req_id>/',views.officer_review_edit_request_views, name='officer_review_edit_request'),
    path('officer_review_add_delete_request/<int:req_id>/', views.officer_review_add_delete_request_views, name='officer_review_add_delete_request'),




    path('admin_signup/',views.admin_signup_views,name='admin_signup'),
    path('admin_login/',views.admin_login_views,name='admin_login'),
    path('admin_logout/',views.admin_logout_views,name='admin_logout'),
    path('admin_profile/',views.admin_profile_views,name='admin_profile'),


    path('admin_add_card_type/',views.admin_add_card_type_views,name='admin_add_card_type'),
    path('admin_home_page/',views.admin_home_page_views,name='admin_home_page'),
    path('admin_add_commodity/',views.admin_add_commodity_views,name='admin_add_commodity'),
    path('admin_commodity_allocation/<int:card_id>/',views.admin_commodity_allocation_views,name='admin_commodity_allocation'),
    path('admin_edit_commodity/<int:commodity_id>/', views.admin_edit_commodity_views, name='admin_edit_commodity'),
    path('admin_global_rates/', views.admin_global_allocation_rates, name='admin_global_allocation_rates'),

    path('admin_delete_commodity/<int:commodity_id>/', views.admin_delete_commodity_views, name='admin_delete_commodity'),
    path('delete_card_type/<int:card_id>/', views.admin_delete_card_type_views, name='admin_delete_card_type'),
    path('admin_statewide_stock_monitor/', views.admin_statewide_item_stock_monitor_views, name='admin_statewide_stock_monitor'),
    path('admin_statewide_analytics/', views.admin_statewide_analytics_views, name='admin_statewide_analytics'),
    path('admin_dispatch_approval_page/', views.admin_dispatch_approval_page_views, name='admin_dispatch_approval_page'),


    path('ajax_get_states/', views.ajax_get_states, name='ajax_get_states'),
    path('ajax_get_districts/', views.ajax_get_districts, name='ajax_get_districts'),
    path('ajax_get_taluks/', views.ajax_get_taluks, name='ajax_get_taluks'),
    path('ajax_get_villages/', views.ajax_get_villages, name='ajax_get_villages'),
    path('ajax_get_shops/', views.ajax_get_shops, name='ajax_get_shops'),

  






]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)