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
    path('consumer_signup/',views.consumer_signup_views,name='consumer_signup'),
    path('consumer_login/',views.consumer_login_views,name='consumer_login'),
    path('consumer_home_page/',views.consumer_home_page_views,name='consumer_home_page'),
    path('consumer_product_details/',views.consumer_product_details_views,name='consumer_product_details'),
    path('add_to_cart/<int:commodity_id>/',views.add_to_cart_views,name='add_to_cart'),
    path('remove_from_cart/<int:commodity_id>/',views.remove_from_cart_views,name='remove_from_cart'),

    path('cart/',views.cart_views,name='cart'),



    # path('shop/',views.shop_views,name='shop'),
    path('shop_worker_signup/',views.shop_worker_signup_views,name='shop_worker_signup'),
    path('shop_worker_login/',views.shop_worker_login_views,name='shop_worker_login'),

    path('officer_signup/',views.officer_signup_views,name='officer_signup'),
    path('officer_login/',views.officer_login_views,name='officer_login'),
    path('officer_home_page/',views.officer_home_page_views,name='officer_home_page'),


    path('admin_signup/',views.admin_signup_views,name='admin_signup'),
    path('admin_login/',views.admin_login_views,name='admin_login'),
    path('admin_add_card_type/',views.admin_add_card_type_views,name='admin_add_card_type'),
    path('admin_home/',views.admin_home_views,name='admin_home'),
    path('admin_add_commodity/',views.admin_add_commodity_views,name='admin_add_commodity'),
    path('admin_commodity_allocation/<int:card_id>/',views.admin_commodity_allocation_views,name='admin_commodity_allocation'),
    path('admin_edit_commodity/<int:commodity_id>/', views.admin_edit_commodity_views, name='admin_edit_commodity'),
    path('admin_delete_commodity/<int:commodity_id>/', views.admin_delete_commodity_views, name='admin_delete_commodity'),
    path('delete_card_type/<int:card_id>/', views.admin_delete_card_type_views, name='admin_delete_card_type'),

    path('shop_home_page/',views.shop_home_page_views,name='shop_home_page'),





]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)