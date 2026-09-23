from pyexpat.errors import messages

from django.contrib import messages

from django.shortcuts import render,redirect,get_object_or_404

# Create your views here.

from django.http import HttpResponse,JsonResponse
from .forms import consumer_login,consumer_signup,shop_worker_login,shop_worker_signup,officer_login,officer_signup,admin_signup,admin_login,admin_add_card_type,admin_add_commodity,admin_commodity_allocation
from .models import consumer_details,shop_worker_details,officer_details,admin_details,card_type_details,commodity_details,commodity_allocation_details,cart_item_details

def welcome(request):
    return HttpResponse("welcom to TNPDS!")

def home(request):
    return render(request,'home_page.html')

def consumer_signup_views(request):
    if request.method=='POST':
        form=consumer_signup(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            card_type=data['card_type']
            card_number=data['card_number']
            mobile_number=data['mobile_number']
            password=data['password']
            confirm_password=data['confirm_password']

            if password != confirm_password:
                messages.error(request, 'Passwords and confirm password do not match')
                return redirect('consumer_signup')
            else:
                if consumer_details.objects.filter(card_number=card_number).exists():
                    messages.error(request,'card number already Registerd')
                    return redirect('consumer_login')
                elif consumer_details.objects.filter(mobile_number=mobile_number).exists():
                    messages.error(request,'Mobile number already Registered')  
                    return redirect('consumer_login')

                else:      
                    consumer_details.objects.create(
                    card_type=card_type,
                    card_number=card_number,
                    mobile_number=mobile_number,
                    password=password

                    )
                    messages.success(request,'consumer SignUp successfully')
                    return redirect('consumer_login')

    else:
        form=consumer_signup()    
    return render(request,'signup_login.html',
                   context={'form':form,
                            'title':'Consumer SignUp',
                            'user':'Consumer',
                            'action':'SignUp',
                            'url':'/consumer_signup/',
                            'in_type':'Sign Up'
                                             }) 

def consumer_login_views(request):
    if request.method=='POST':
        form=consumer_login(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            mobile_number=data['mobile_number']
            password=data['password']

            consumer=consumer_details.objects.filter(mobile_number=mobile_number).first()
            if consumer:
                if consumer.password==password:
                    request.session['consumer_mobile']=mobile_number
                    messages.success(request,'login successfull')
                    return redirect('consumer_home_page')
                else:
                    messages.error(request,'wrong password')
            else:
                messages.error(request,'consumer not found')    
                return redirect('consumer_signup')


    else:
        form=consumer_login()    
    return render(request,'signup_login.html',
                   context={'form':form,
                            'title':'Consumer LogIn',
                            'user':'Consumer',
                            'action':'LogIn',
                            'url':'/consumer_login/',
                            'in_type':'LogIn',
                            'new_user':'Consumer',
                            'new_user_url':'/consumer_signup/',
                                             }) 

def consumer_home_page_views(request):
    return render(request,'consumer/consumer_home_page.html')

def consumer_product_details_views(request):
    mobile_number=request.session.get('consumer_mobile')
    if not mobile_number:
        return redirect('consumer_login')
    
    consumer=consumer_details.objects.get(mobile_number=mobile_number)
    user_card_type=consumer.card_type


    allocated_commodities=commodity_allocation_details.objects.filter(card_type=user_card_type)

    user_card_items=cart_item_details.objects.filter(consumer=consumer)
    cart_dict={item.commodity.id: item.quantity for item in user_card_items}

    for item in allocated_commodities:
        item.in_cart_qty=cart_dict.get(item.commodity.id,0)

    return render(request,'consumer/consumer_product_details.html',
                  {
                      'consumer':consumer,
                      'card_type':user_card_type,
                      'allocated_commodities':allocated_commodities,
                  })

def shop_worker_signup_views(request):
    if request.method=='POST':
        form=shop_worker_signup(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            shop_id=data['shop_id']
            shop_worker_id=data['shop_worker_id']
            mobile_number=data['mobile_number']
            password=data['password']
            confirm_password=data['confirm_password']

            if password != confirm_password:
                messages.error(request, 'Passwords and confirm password do not match')
            else:
                if shop_worker_details.objects.filter(shop_worker_id=shop_worker_id).exists():
                    messages.error(request,'shop worker id already Registerd')
                    return redirect('shop_worker_login')

                else:      
                    shop_worker_details.objects.create(
                        shop_id=shop_id,
                        shop_worker_id=shop_worker_id,
                        mobile_number=mobile_number,
                        password=password

                    )
                    messages.success(request,'shop worker SignUp successfully')
                    return redirect('shop_worker_login')

    else:
        form=shop_worker_signup()    
    return render(request,'signup_login.html',
                   context={'form':form,
                            'title':'Shop Worker SignUp',
                            'user':'Shop Worker',
                            'action':'SignUp',
                            'url':'/shop_worker_signup/',
                            'in_type':'Sign Up'
                                             }) 

def shop_worker_login_views(request):
    if request.method=='POST':
        form=shop_worker_login(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            shop_worker_id=data['shop_worker_id']
            password=data['password']

            shop_worker=shop_worker_details.objects.filter(shop_worker_id=shop_worker_id).first()
            if shop_worker:
                if shop_worker.password==password:
                    messages.success(request,'login successfull')
                    messages.info(request,'Work Is God')
                    return redirect('shop_home_page')
                else:
                    messages.error(request,'wrong password')
            else:
                messages.error(request,'shop worker not found')  
                return redirect('shop_worker_signup')


    else:
        form=shop_worker_login()    
    return render(request,'signup_login.html',
                   context={'form':form,
                            'title':'Shop Worker LogIn',
                            'user':'Shop Worker',
                            'action':'LogIn',
                            'url':'/shop_worker_login/',
                            'in_type':'LogIn',
                            'new_user':'shop worker',
                            'new_user_url':'/shop_worker_signup/',
                                             }) 

def officer_signup_views(request):
    if request.method=='POST':
        form=officer_signup(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            officer_id=data['officer_id']
            mobile_number=data['mobile_number']
            password=data['password']
            confirm_password=data['confirm_password']

            if password != confirm_password:
                messages.error(request, 'Passwords and confirm password do not match')
            else:
                if officer_details.objects.filter(officer_id=officer_id).exists():
                    messages.error(request,'officer id already Registerd')
                    return redirect('officer_login')

                else:      
                    officer_details.objects.create(
                        officer_id=officer_id,
                        mobile_number=mobile_number,
                        password=password

                    )
                    messages.success(request,'officer Signup successfully')
                    return redirect('officer_login')

    else:
        form=officer_signup()    
    return render(request,'signup_login.html',
                   context={'form':form,
                            'title':'officer SignUp',
                            'user':'Officer',
                            'action':'SignUp',
                            'url':'/officer_signup/',
                            'in_type':'Sign Up'
                                             }) 

def officer_login_views(request):
    if request.method=='POST':
        form=officer_login(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            officer_id=data['officer_id']
            password=data['password']

            officer=officer_details.objects.filter(officer_id=officer_id).first()
            if officer:
                if officer.password==password:
                    messages.success(request,'login successfull')
                    return redirect('officer_home_page')
                else:
                    messages.error(request,'wrong password')
            else:
                messages.error(request,'officer not found')      
                return redirect('officer_signup')


    else:
        form=officer_login()    
    return render(request,'signup_login.html',
                   context={'form':form,
                            'title':'officer LogIn',
                            'user':'Officer',
                            'action':'LogIn',
                            'url':'/officer_login/',
                            'in_type':'LogIn',
                            'new_user':'Officer',
                            'new_user_url':'/officer_signup/',
                                             }) 

def officer_home_page_views(request):
    return render(request,'officer/officer_home_page.html')

def admin_signup_views(request):
    if request.method=='POST':
        form=admin_signup(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            admin_id=data['admin_id']
            mobile_number=data['mobile_number']
            password=data['password']
            confirm_password=data['confirm_password']

            if password != confirm_password:
                messages.error(request, 'Passwords and confirm password do not match')
            else:
                if admin_details.objects.filter(admin_id=admin_id).exists():
                    messages.error(request,'admin id already Registerd')
                    return redirect('admin_login')

                else:      
                    admin_details.objects.create(
                        admin_id=admin_id,
                        mobile_number=mobile_number,
                        password=password

                    )
                    messages.success(request,'admin Signup successfully')
                    return redirect('admin_login')

    else:
        form=admin_signup()    
    return render(request,'admin/signup_login.html',
                   context={'form':form,
                            'title':'admin SignUp',
                            'user':'Admin',
                            'action':'SignUp',
                            'url':'/admin_signup/',
                            'in_type':'Sign Up'
                                             }) 

def admin_login_views(request):
    if request.method=='POST':
        form=admin_login(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            admin_id=data['admin_id']
            password=data['password']

            admin=admin_details.objects.filter(admin_id=admin_id).first()
            if admin:
                if admin.password==password:
                    messages.success(request,'login successfull')
                    return redirect('admin_home')
                else:
                    messages.error(request,'wrong password')
            else:
                messages.error(request,'admin not found')  
                return redirect('admin_signup')


    else:
        form=admin_login()    
    return render(request,'admin/signup_login.html',
                   context={'form':form,
                            'title':'admin LogIn',
                            'user':'Admin',
                            'action':'LogIn',
                            'url':'/admin_login/',
                            'in_type':'LogIn',
                            'new_user':'Admin',
                            'new_user_url':'/admin_signup/',
                                             }) 

def admin_add_card_type_views(request):
    if request.method=='POST':
        form=admin_add_card_type(request.POST)
        if form.is_valid():
            card_type=form.cleaned_data
            enter_card_type=card_type['card_type']


            if card_type_details.objects.filter(card_type=enter_card_type).exists():
                    messages.info(request,'card Type Already exist')
                
            else:
                card_type_details.objects.create(
                                       card_type=enter_card_type
                
                                    )
                messages.success(request,'card type added into db successfully')
                return redirect('admin_add_card_type')

                      

    else:
        form=admin_add_card_type() 
    all_card_type=card_type_details.objects.all()

    return render(request,'admin/admin_actions.html',
                   context={'form':form,
                            'title':'admin Action',
                            'user':'Admin',
                            'action':'Add Card',
                            'url':'/admin_add_card_type/',
                            'in_type':'Add',
                            'card_type':all_card_type,
                            'column_title':'Card Type',
                            # 'commodities':commodities,
                            'all_card_type':True,
                            'new_url':'/admin_commodity_allocation/'
                                             }) 

def admin_home_views(request):
    return render(request,'admin/admin_home.html')
    # return HttpResponse("welcom to Admin Page!")

def admin_add_commodity_views(request):
    if request.method=='POST':
        form=admin_add_commodity(request.POST,request.FILES)
        if form.is_valid():
            data=form.cleaned_data
            enter_commodity=data['commodity']
            enter_price=data['price']
            enter_unit=data['unit']
            enter_image = request.FILES.get('commodity_image')

            print("FILES RECEIVED:", request.FILES)
            if commodity_details.objects.filter(commodity=enter_commodity).exists():
                    messages.info(request,'commodity Already exist')
                    return redirect('admin_add_commodity')
                    
                
            else:
                commodity_details.objects.create(
                                       commodity=enter_commodity,
                                       price=enter_price,
                                       unit=enter_unit,
                                       commodity_image=enter_image
                
                                    )
                messages.success(request,'commodity added into db successfully')
                return redirect('admin_add_commodity')

                      

    else:
        form=admin_add_commodity() 

    commodities=commodity_details.objects.all()       
       
    return render(request,'admin/admin_actions.html',
                   context={'form':form,
                            'title':'admin Action',
                            'user':'Admin',
                            'action':'Add Commodity',
                            'url':'/admin_add_commodity/',
                            'in_type':'Add',
                            'data':commodities,
                            'column_title':'Commodity',
                            'commodity':True,

                            
                                             }) 

def admin_commodity_allocation_views(request, card_id):
    selected_card = get_object_or_404(card_type_details, id=card_id)
    commodities = commodity_details.objects.all()

    if request.method == 'POST':
        form=admin_commodity_allocation(request.POST)

        for commodity in commodities:
            quantity = request.POST.get(f'quantity_{commodity.id}', '').strip()
            selected_unit=request.POST.get(f'unit_{{commodity.id}}',commodity.unit)
            if quantity:
                allocation_quantity = float(quantity)
            else:
                allocation_quantity = 0.00

            commodity_allocation_details.objects.update_or_create(
                card_type=selected_card,
                commodity=commodity,
                defaults={
                    'quantity': allocation_quantity,
                    'unit':selected_unit}
            )

        messages.success(request, f'Commodity allocation updated for {selected_card.card_type} successfully!')
        return redirect('admin_add_card_type')

    existing_allocations = {}
    for a in commodity_allocation_details.objects.filter(card_type=selected_card):
        existing_allocations[a.commodity_id] = {
            'qty': a.quantity,
             'unit': getattr(a, 'unit', a.commodity.unit)  # getattr=>get Attribute
        }

    commodity_list = []
    for commodity in commodities:
        saved_data = existing_allocations.get(commodity.id)
        commodity_list.append({
            'id': commodity.id,
            'name': commodity.commodity,
            'unit': commodity.unit,
            'current_quantity': saved_data['qty'] if saved_data else '',
            'current_unit': saved_data['unit'] if saved_data else commodity.unit
        })


    return render(
        request,
        'admin/admin_allocate_commodity.html',
        { 
            'title': 'Admin Action',
            'user': 'Admin',
            'action': f'Allocate Commodity for card type {selected_card.card_type } ',
            'url': f'/admin_commodity_allocation/{card_id}/',
            'in_type': 'Allocate',
            'commodity_list': commodity_list,
            'is_allocation_page': True,
        }
    )

def admin_edit_commodity_views(request, commodity_id):
    commodity_item = get_object_or_404(commodity_details, id=commodity_id)

    if request.method == 'POST':
        form = admin_add_commodity(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            commodity_item.commodity = data['commodity']
            commodity_item.price = data['price']
            commodity_item.save()

            messages.success(request, f'{commodity_item.commodity} updated successfully!')
            return redirect('admin_add_commodity')
    else:
        form = admin_add_commodity(initial={
            'commodity': commodity_item.commodity,
            'price': commodity_item.price
        })

    commodities = commodity_details.objects.all()

    return render( 

        request,
        'admin/admin_actions.html',
        context={
            'form': form,
            'title': 'Admin Action',
            'user': 'Admin',
            'action': f'Edit Commodity ({commodity_item.commodity})',
            'url': f'/admin_edit_commodity/{commodity_id}/',
            'in_type': 'Save',
            'data': commodities,
            'column_title': 'Commodity',
            'commodity': True,
            'item':commodity_item,
        }
    )

def admin_delete_commodity_views(request, commodity_id):
    commodity_item = get_object_or_404(commodity_details, id=commodity_id)

    commodity_name = commodity_item.commodity
    
    commodity_item.delete()
    
    messages.success(request, f'{commodity_name} deleted successfully!')
    return redirect('admin_add_commodity')

def admin_delete_card_type_views(request, card_id):
    card = get_object_or_404(card_type_details, id=card_id)
    card_name = card.card_type
    card.delete()
    
    messages.error(request, f'Card type "{card_name}" deleted!')
    return redirect('admin_add_card_type')

def shop_home_page_views(request):
    return render(request,'shop/shop_home_page.html')

def add_to_cart_views(request,commodity_id):
    mobile_number = request.session.get('consumer_mobile')
    if not mobile_number:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=401)

    consumer = get_object_or_404(consumer_details, mobile_number=mobile_number)

    commodity=get_object_or_404(commodity_details,id=commodity_id)



    allocation = commodity_allocation_details.objects.filter(
            card_type=consumer.card_type, 
            commodity=commodity
        ).first()
        
    max_allocated_qty = allocation.quantity if allocation else 0

    if max_allocated_qty <= 0:
            return JsonResponse({'status': 'error', 'message': 'This item has 0 allocated quota.'})



    cart_item,created=cart_item_details.objects.get_or_create(
        commodity=commodity,
        consumer=consumer,
        defaults={'quantity': max_allocated_qty},
        )

    if not created:
        if cart_item.quantity==0:
                    cart_item.quantity=max_allocated_qty
                    cart_item.save()
        elif cart_item.quantity<max_allocated_qty:
            cart_item.quantity+=1
            cart_item.save()
        else:
            return JsonResponse({
                'status': 'limit_reached',
                'item_qty': cart_item.quantity,
                'message': f'Cannot exceed allocated limit of {max_allocated_qty}'
            }) 
     
    return JsonResponse({
        'status':'success',
        'item_qty':cart_item.quantity
        }
    )    

def remove_from_cart_views(request, commodity_id):
    mobile_number = request.session.get('consumer_mobile')
    if not mobile_number:
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=401)

    consumer = get_object_or_404(consumer_details, mobile_number=mobile_number)
    commodity = get_object_or_404(commodity_details, id=commodity_id)
    
    cart_item = cart_item_details.objects.filter(
        commodity=commodity,
        consumer=consumer,
    ).first()

    if cart_item:
        cart_item.quantity -= 1

        if cart_item.quantity > 0:
            cart_item.save()
            return JsonResponse({'status': 'success', 'item_qty': cart_item.quantity})
        else:
            cart_item.delete()
            return JsonResponse({'status': 'success', 'item_qty': 0})

    return JsonResponse({'status': 'success', 'item_qty': 0})

def cart_views(request):
    cart_items=cart_item_details.objects.all()
    total_price=sum(item.get_total_price() for item in cart_items)
    return render(request,'consumer/cart_view.html',{
        'cart_items':cart_items,
        'total_price':total_price,
        }
    )