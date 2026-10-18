from pyexpat.errors import messages
from django.contrib import messages
from datetime import datetime
from django.views.decorators.cache import never_cache

from datetime import date
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
import calendar
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.db.models import Sum





# Create your views here.

from django.http import HttpResponse,JsonResponse
from .forms import ( consumer_login,consumer_signup,shop_worker_login,shop_worker_signup,officer_login,officer_signup,admin_signup,admin_login,
                    admin_add_card_type,admin_add_commodity,admin_commodity_allocation,FamilyMemberForm
                    
                    , FamilyMemberEditRequestForm,
                    )
from .models import ( consumer_details,shop_worker_details,officer_details,admin_details,card_type_details,commodity_details,commodity_allocation_details,
                     cart_item_details,shop_commodity_details,shop_worker_login_details,shop_details,consumer_details,order_details,order_item_details,
                     portal_photo_details,consumer_monthly_allocation_status_details,card_details, state_details, district_details, taluk_details, 
                     village_town_details, shop_details,
                     admin_global_allocation_rules,
                     consumer_allocation_details,
                     consumer_crud_details,
                     family_members_details,
                     consumer_crud_history,
                     stock_dispatch_audit_trail,
                     shop_stock_dispatch_details,
                     consumer_monthly_allocation_status_details



                     )


def welcome(request):
    return HttpResponse("welcom to TNPDS!")

def home(request):
    photos = portal_photo_details.objects.filter(portal_type='home', is_active=True).order_by('display_order')

    context=get_portal_context('home',{
                                'photos':photos,
                                'title':'TNPDS-Home',
                                })


    return render(request,'common/home_page.html',context)

@never_cache
def common_signup_login_views(request):
    photos = portal_photo_details.objects.filter(portal_type='consumer', is_active=True).order_by('display_order')

    return render(request,'common/signup_login.html',
                  context={
                      'photos':photos
                  })

@never_cache
def consumer_signup_views(request):
    photos = portal_photo_details.objects.filter(portal_type='consumer', is_active=True).order_by('display_order')
    if request.method == 'POST':
        form = consumer_signup(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            card_type = data['card_type']
            card_number = data['card_number']
            mobile_number = data['mobile_number']
            password = data['password']
            shop_instance = data['shop_id'] 

            if consumer_details.objects.filter(card_number=card_number).exists():
                messages.error(request, 'Card number already registered')
                return redirect('consumer_signup')
            elif consumer_details.objects.filter(mobile_number=mobile_number).exists():
                messages.error(request, 'Mobile number already registered')  
                return redirect('consumer_signup')
            else:     
                consumer_details.objects.create(
                    card_type=card_type,
                    card_number=card_number,
                    mobile_number=mobile_number,
                    password=password,
                    home_shop=shop_instance,  # Database column name 'home_shop' 
                )
                messages.success(request, 'Consumer signup successfully')
                return redirect('consumer_login')
    else:
        form = consumer_signup()    
        
    return render(request, 'common/signup.html',
                    context={
                        'form': form,
                        'title': 'Consumer-Signup',
                        'subtitle': 'New Consumer Registration',
                        'url': '/consumer_signup/',
                        'login_url': 'consumer_login',
                        'photos': photos,
                    })

@never_cache
def consumer_login_views(request):
    auto_flip = False
    entered_mobile = ""

    
    photos = portal_photo_details.objects.filter(portal_type='consumer', is_active=True).order_by('display_order')
    
    if request.method == 'POST':
        form = consumer_login(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            mobile_number = data['mobile_number']
            password = data['password']

            consumer = consumer_details.objects.filter(mobile_number=mobile_number).first()
            if consumer:
                if consumer.password == password:
                    request.session['consumer_mobile'] = mobile_number
                    messages.success(request, 'உள்நுழைவு வெற்றிகரமாக முடிந்தது!')
                    return redirect('consumer_home_page')
                else:
                    messages.error(request, 'தவறான கடவுச்சொல் (Wrong Password)!')
            else:
                messages.warning(request, 'பதிவு செய்யப்படாத எண்! 5 விநாடிகளில் பதிவுப் பக்கம் திறக்கும்...')
                auto_flip = True
                entered_mobile = mobile_number

    else:
        form = consumer_login()

    return render(request, 'common/login.html', {
        'form': form,
        'title': 'consumer-Login',
        'subtitle': 'Consumer Login Portal',
        'user_type': 'Consumer',
        'url': '/consumer_login/',
        'signup_url': 'consumer_signup',
        'home_url': 'home',
        'auto_flip': auto_flip,
        'entered_mobile': entered_mobile,
        'photos': photos,
        'new_user':'Consumer',
    })

def consumer_logout_views(request):
    request.session.flush()
    
    messages.success(request, 'Logged out successfully!')
    return redirect('consumer_login') 

def consumer_profile_views(request):
    mobile_number = request.session.get('consumer_mobile')
    if not mobile_number:
        return redirect('consumer_login')

    consumer = consumer_details.objects.filter(mobile_number=mobile_number).first()
    if not consumer:
        return redirect('consumer_login')

    family_members = consumer.family_members.all()
    table_headers = ['Name', 'Relation', 'Gender', 'Status', 'Aadhaar', 'Actions']

    #  check pending request (Edit or Delete or Add ) 
    members_data = []
    for m in family_members:
        pending_edit = consumer_crud_details.objects.filter(member=m, request_type='EDIT', status='PENDING').exists()
        pending_delete = consumer_crud_details.objects.filter(member=m, request_type='DELETE', status='PENDING').exists()
        
        pending_add = consumer_crud_details.objects.filter(member=m, request_type='ADD', status='PENDING').exists() # need to implement in future update.

        members_data.append({
            'member': m,
            'is_edit_pending': pending_edit,
            'is_delete_pending': pending_delete,
            'is_add_pending': pending_add,


        })

    if request.method == 'POST':
        form = FamilyMemberForm(request.POST, request.FILES) 
        if form.is_valid():
            print("ok")
            data = form.cleaned_data
            
            consumer_crud_details.objects.create(
                consumer=consumer,
                request_type='ADD',
                name=data['name'],
                dob=data['dob'],
                gender=data['gender'],
                relation=data['relation'],
                mobile_number=data.get('mobile_number'),
                aadhaar_number=data['aadhaar_number'],
                reason='New family member addition request',
                status='PENDING'
            )
            
            messages.success(request, "Family member addition request submitted successfully! Waiting for officer approval.")
            return redirect('consumer_profile')
    else:
        print("error")
        form = FamilyMemberForm()

    saved_allocations = consumer_allocation_details.objects.filter(consumer=consumer)

    profile_data = [
        ("Mobile Number", consumer.mobile_number),
        ("Card Type", consumer.card_type.card_type if consumer.card_type else "N/A"),
        ("Card Number", consumer.card_number),
        ("Home Shop", consumer.home_shop_id),
    ]

    adult_count = sum(1 for m in family_members if getattr(m, 'is_adult', False))
    child_count = family_members.count() - adult_count

    context = get_portal_context('consumer', {
        'title':'Consumer-Profile',
        'consumer': consumer,
        'profile_data': profile_data,
        'form': form,
        'table_headers': table_headers,
        'family_members_data': members_data,  # send as  'family_members_data' 
        'allocations': saved_allocations,
        'result': {
            'card_type': consumer.card_type.card_type if consumer.card_type else "N/A",
            'adult_count': adult_count,
            'child_count': child_count,
            'allocations': saved_allocations,
        }
    })

    return render(request, 'consumer/profile.html', context)

def consumer_edit_family_member_views(request, member_id):
    mobile_number = request.session.get('consumer_mobile')
    if not mobile_number:
        messages.error(request, 'Please login first!')
        return redirect('consumer_login')
    
    consumer = get_object_or_404(consumer_details, mobile_number=mobile_number)
    member = get_object_or_404(family_members_details, id=member_id, consumer=consumer)
    
    #  Check if an edit request is already pending for this member (Latest pending request)
    pending_req = consumer_crud_details.objects.filter(member=member, status='PENDING').order_by('-requested_at').first()

    if request.method == 'POST':
        form = FamilyMemberEditRequestForm(request.POST, request.FILES)
        if form.is_valid():
            print("FORM IS VALID AND PASSING!")
            data = form.cleaned_data
            
            name_changed = data['name'].strip() != member.name.strip()
            dob_changed = str(data['dob']) != str(member.dob)
            gender_changed = data['gender'].strip() != member.gender.strip()
            
            if (name_changed or dob_changed or gender_changed) and not request.FILES.get('document_copy') and not pending_req:
                messages.error(request, "Supporting proof document is mandatory for changing Name, DOB, or Gender!")
                context = get_portal_context('consumer', {'form': form, 'member': member, 'pending_req': pending_req})
                return render(request, 'consumer/edit_member.html', context)

            # changed field check :
            changed = []
            if data['name'].strip() != member.name.strip():
                changed.append('name')
            if str(data['dob']) != str(member.dob):
                changed.append('dob')
            if data['gender'].strip() != member.gender.strip():
                changed.append('gender')
            if data['relation'].strip() != member.relation.strip():
                changed.append('relation')

            form_mobile = (data.get('mobile_number') or '').strip()
            db_mobile = (getattr(member, 'mobile_number', '') or '').strip()
            if form_mobile != db_mobile:
                changed.append('mobile_number')
                
            # Email ID (None vs "" safe check)
            form_email = (data.get('email_id') or '').strip()
            db_email = (getattr(member, 'email_id', '') or '').strip()
            if form_email != db_email:
                changed.append('email_id')
            
            changed_str = ",".join(changed)

            if (name_changed or dob_changed or gender_changed) and not request.FILES.get('document_copy') and not pending_req:
                messages.error(request, "Supporting proof document is mandatory for changing Name, DOB, or Gender!")

            #  UPSERT LOGIC: (Accumulate changes)
            if pending_req:
                pending_req.name = data['name']
                pending_req.dob = data['dob']
                pending_req.gender = data['gender']
                pending_req.relation = data['relation']
                pending_req.mobile_number = data['mobile_number']
                pending_req.email_id = data.get('email_id')
                pending_req.reason = data['reason']
                
                if request.FILES.get('document_copy'):
                    pending_req.document_copy = request.FILES.get('document_copy')
                
                existing_fields = pending_req.changed_fields.split(',') if pending_req.changed_fields else []
                combined_fields = list(set(existing_fields + changed))
                pending_req.changed_fields = ",".join(combined_fields)
                
                pending_req.save()
                messages.success(request, "Your pending edit request has been updated successfully! Waiting for officer approval.")
            else:
                # new request create : 
                consumer_crud_details.objects.create(
                    consumer=consumer,
                    member=member,
                    request_type='EDIT',
                    name=data['name'],
                    dob=data['dob'],
                    gender=data['gender'],
                    relation=data['relation'],
                    mobile_number=data['mobile_number'],
                    aadhaar_number=data['aadhaar_number'], 
                    email_id=data.get('email_id'),
                    reason=data['reason'],
                    document_copy=request.FILES.get('document_copy'),
                    changed_fields=changed_str,
                    status='PENDING'
                )
                messages.success(request, "Edit request submitted successfully! Waiting for officer approval.")
            
            return redirect('consumer_edit_family_member',member_id=member.id)
    else:
        # Initial Data Logic: show Pending or  original member data :
        if pending_req:
            form = FamilyMemberEditRequestForm(initial={
                'name': pending_req.name,
                'dob': pending_req.dob,
                'gender': pending_req.gender,
                'relation': pending_req.relation,
                'mobile_number': pending_req.mobile_number,
                'email_id': getattr(pending_req, 'email_id', ''),
                'reason': pending_req.reason,
            })
        else:
            form = FamilyMemberEditRequestForm(initial={
                'name': member.name,
                'dob': member.dob,
                'gender': member.gender,
                'relation': member.relation,
                'mobile_number': member.mobile_number,
                'aadhaar_number': member.aadhaar_number, 
                'email_id': getattr(member, 'email_id', ''),
            })

    context = get_portal_context('consumer', {
        'form': form,
        'member': member,
        'pending_req': pending_req,
        'title':'Consumer-Edit-Member',
    })
    return render(request, 'consumer/edit_member.html', context)                                            

def consumer_delete_family_member_views(request, member_id):
    mobile_number = request.session.get('consumer_mobile')
    if not mobile_number:
        messages.error(request, 'Please login first!')
        return redirect('consumer_login')
    
    consumer = get_object_or_404(consumer_details, mobile_number=mobile_number)
    member = get_object_or_404(family_members_details, id=member_id, consumer=consumer)
    
    # already pending DELETE request check:
    existing_delete_pending = consumer_crud_details.objects.filter(member=member, request_type='DELETE', status='PENDING').first()
    if existing_delete_pending:
        messages.warning(request, "A deletion request is already pending approval for this member!")
        return redirect('consumer_profile')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        document_copy = request.FILES.get('document_copy')

        if not reason:
            messages.error(request, "Reason for deletion is mandatory!")
            return redirect('consumer_delete_family_member', member_id=member.id)

        # Create DELETE CRUD Request for Officer Approval
        consumer_crud_details.objects.create(
            consumer=consumer,
            member=member,
            request_type='DELETE',
            name=member.name,
            dob=member.dob,
            gender=member.gender,
            relation=member.relation,
            mobile_number=member.mobile_number,
            aadhaar_number=member.aadhaar_number, 
            email_id=getattr(member, 'email_id', ''),
            reason=reason,
            document_copy=document_copy,
            status='PENDING'
        )
        
        messages.success(request, "Family member deletion request submitted successfully! Waiting for officer approval.")
        return redirect('consumer_profile')

    context = get_portal_context('consumer', {
        'member': member,
        'title':'Consumer-Delete-Member',
    })
    return render(request, 'consumer/delete_member_request.html', context)

def calculate_consumer_allocation(user_profile):
    card_type_val = user_profile.card_type  
    
    if not card_type_val:
        return {'success': False, 'message': 'Ration card type not found for this profile!'}

    # 1. Card Type object-fetch (Case-insensitive search)
    if isinstance(card_type_val, str):
        card_type_obj = card_type_details.objects.filter(card_type__iexact=card_type_val).first()
    else:
        card_type_obj = card_type_val  

    if not card_type_obj:
        return {'success': False, 'message': f'Card type "{card_type_val}" is not configured in the system!'}

    # 2. Family members count (Adults & Children)
    adult_count = user_profile.adult_count or 0
    child_count = user_profile.child_count or 0

    if adult_count == 0 and child_count == 0:
        return {'success': False, 'message': 'Please add family members in your profile before ordering!'}

    pds_commodities = commodity_details.objects.filter(is_non_pds=False, is_deleted=False)
    
    if not pds_commodities.exists():
        return {'success': False, 'message': 'No PDS commodities available in the system!'}

    calculated_allocations = []
    group_totals = {}

    for commodity in pds_commodities:
        allocation_rule = commodity_allocation_details.objects.filter(
            card_type=card_type_obj, 
            commodity=commodity
        ).first()

        if not allocation_rule:
            continue  

        card_max_qty = float(allocation_rule.max_cap or 0.00)
        min_qty = float(commodity.min_qty or 0.00)
        
        if card_max_qty <= 0:
            continue

        # Per-Head Calculation Formula
        raw_entitlement = (adult_count * float(commodity.adult_rate)) + (child_count * float(commodity.child_rate))

        if raw_entitlement > 0 and raw_entitlement < min_qty:
            entitlement = min_qty
        else:
            entitlement = raw_entitlement

        if entitlement > card_max_qty:
            entitlement = card_max_qty

        group_name = commodity.group_name
        group_max_cap = float(commodity.group_max_cap or 0.00)

        if group_name and group_name.lower() != 'none':
            if group_name not in group_totals:
                group_totals[group_name] = {'current_sum': 0.00, 'max_cap': group_max_cap}
            
            group_totals[group_name]['current_sum'] += entitlement

        calculated_allocations.append({
            'commodity': commodity,
            'entitlement': round(entitlement, 2),
            'group_name': group_name,
            'card_max_qty': card_max_qty,
            'min_qty': min_qty
        })

    # Group Max Cap Enforcement
    for item in calculated_allocations:
        g_name = item['group_name']
        if g_name and g_name in group_totals:
            g_data = group_totals[g_name]
            if g_data['max_cap'] > 0 and g_data['current_sum'] > g_data['max_cap']:
                excess_ratio = g_data['max_cap'] / g_data['current_sum']
                item['entitlement'] = round(item['entitlement'] * excess_ratio, 2)

    return {
        'success': True,
        'allocations': calculated_allocations,
        'adult_count': adult_count,
        'child_count': child_count,
        'card_type': card_type_obj.card_type
    }   

@transaction.atomic
def update_consumer_allocations(consumer):
    """
    1. Checks if card type has is_pds_allocation = True. If False, skips.
    2. Calculates entitlements based on total members (<3 vs >=3 Max Cap logic).
    3. Saves calculated quantities to consumer_allocation_details.
    4. Automatically triggers shop required stock live update.
    """
    card_type_obj = consumer.card_type
    if not card_type_obj or not getattr(card_type_obj, 'is_pds_allocation', False):
        consumer_allocation_details.objects.filter(consumer=consumer).delete()
        if consumer.home_shop:
            update_shop_required_stock(consumer.home_shop)
        return

    consumer_allocation_details.objects.filter(consumer=consumer).delete()

    family_members = consumer.family_members.all()
    total_members = family_members.count()
    
    adult_count = sum(1 for m in family_members if getattr(m, 'is_adult', False) or str(getattr(m, 'status', '')).strip().capitalize() == 'Adult')
    child_count = total_members - adult_count

    if total_members == 0:
        if consumer.home_shop:
            update_shop_required_stock(consumer.home_shop)
        return  

    pds_commodities = commodity_details.objects.filter(is_non_pds=False, is_deleted=False)
    group_totals = {}
    temp_allocations = []

    for commodity in pds_commodities:
        allocation_rule = commodity_allocation_details.objects.filter(
            card_type=card_type_obj, 
            commodity=commodity
        ).first()

        if not allocation_rule:
            continue

        card_max_qty = float(allocation_rule.max_cap or 0.00)
        min_qty = float(commodity.min_qty or 0.00)
        
        if card_max_qty <= 0:
            continue

        # Rule: Members count < 3  adult/child rate,   >= 3 n Max Cap limit :
        if total_members < 3:
            raw_entitlement = (adult_count * float(commodity.adult_rate)) + (child_count * float(commodity.child_rate))
            if raw_entitlement > 0 and raw_entitlement < min_qty:
                entitlement = min_qty
            else:
                entitlement = raw_entitlement
        else:
            entitlement = card_max_qty

        if entitlement > card_max_qty:
            entitlement = card_max_qty

        group_name = commodity.group_name
        group_max_cap = float(commodity.group_max_cap or 0.00)

        if group_name and group_name.lower() != 'none':
            if group_name not in group_totals:
                group_totals[group_name] = {'current_sum': 0.00, 'max_cap': group_max_cap}
            group_totals[group_name]['current_sum'] += entitlement

        temp_allocations.append({
            'commodity': commodity,
            'entitlement': entitlement,
            'group_name': group_name,
            'card_max_qty': card_max_qty,
            'min_qty': min_qty
        })

    for item in temp_allocations:
        g_name = item['group_name']
        final_entitlement = item['entitlement']
        
        if g_name and g_name in group_totals:
            g_data = group_totals[g_name]
            if g_data['max_cap'] > 0 and g_data['current_sum'] > g_data['max_cap']:
                excess_ratio = g_data['max_cap'] / g_data['current_sum']
                final_entitlement = final_entitlement * excess_ratio

        consumer_allocation_details.objects.create(
            consumer=consumer,
            commodity=item['commodity'],
            entitlement=round(final_entitlement, 2),
            group_name=g_name,
            card_max_qty=item['card_max_qty'],
            min_qty=item['min_qty']
        )

    if consumer.home_shop:
        update_shop_required_stock(consumer.home_shop)

@transaction.atomic
def update_shop_required_stock(shop):
    """
    Sums up all card holder allocations under this shop and updates overall required stock live.
    """
    consumers = consumer_details.objects.filter(home_shop=shop)
    total_card_holders = consumers.count()
    
    overall_req = {}

    for consumer in consumers:
        allocations = consumer_allocation_details.objects.filter(consumer=consumer)
        for alloc in allocations:
            comm_id = alloc.commodity.id
            if comm_id in overall_req:
                overall_req[comm_id] += float(alloc.entitlement)
            else:
                overall_req[comm_id] = float(alloc.entitlement)

    for comm_id, total_qty in overall_req.items():
        commodity_obj = commodity_details.objects.get(id=comm_id)
        shop_commodity_details.objects.update_or_create(
            shop=shop,
            commodity=commodity_obj,
            defaults={'required_stock': Decimal(str(round(total_qty, 2)))}
        )
        
    shop.total_card_holders = total_card_holders
    shop.save()

def consumer_allocation_details_views(request):
    # Logged-in user profile-ai fetch :
    try:
        user_profile = consumer_details.objects.get(user=request.user)
    except consumer_details.DoesNotExist:
        messages.warning(request, 'Please complete your profile and add family members first!')
        return redirect('update_user_profile')  

    calculation_result = calculate_consumer_allocation(user_profile)

    if not calculation_result['success']:
        messages.error(request, calculation_result['message'])
        return redirect('update_user_profile')

    context = get_portal_context('consumer', {
        'result': calculation_result,
        'user_profile': user_profile,
        'title':'Consumer-Allocation',
    })
    
    return render(request, 'consumer/allocation_details.html', context)

def consumer_home_page_views(request):
    photos = portal_photo_details.objects.filter(portal_type='consumer', is_active=True).order_by('display_order')
    context = get_portal_context('consumer', 
                                 {
                                    'photos': photos,
                                    'title':'Consumer-Home',
                                })
   
    return render(request, 'common/home_page.html',context)

def consumer_product_details_views(request):
    mobile_number = request.session.get('consumer_mobile')
    if not mobile_number:
        return redirect('consumer_login')
    
    consumer = consumer_details.objects.get(mobile_number=mobile_number)
    user_card_type = consumer.card_type

    if hasattr(consumer, 'taluk') and consumer.taluk:
        nearby_shops = list(shop_details.objects.filter(taluk=consumer.taluk).order_by('shop_id')[:10])
    else:
        nearby_shops = list(shop_details.objects.all().order_by('shop_id')[:10])

    incoming_shop_id = request.GET.get('selected_shop')
    previous_shop_id = request.session.get('selected_shop_id')

    if incoming_shop_id:
        if previous_shop_id and str(previous_shop_id) != str(incoming_shop_id):
            cart_item_details.objects.filter(consumer=consumer).delete()
            messages.info(request, 'Shop changed so items are removed!')
        selected_shop_id = incoming_shop_id
    else:
        selected_shop_id = previous_shop_id    
    
    current_shop = None
    
    if selected_shop_id:
        current_shop = shop_details.objects.filter(shop_id=selected_shop_id).first()
        request.session['selected_shop_id'] = selected_shop_id
    elif nearby_shops:
        current_shop = nearby_shops[0]
        request.session['selected_shop_id'] = str(current_shop.shop_id)

    allocated_commodities = consumer_allocation_details.objects.filter(
        consumer=consumer,
        commodity__is_non_pds=False,
        commodity__is_deleted=False,
    ).select_related('commodity')

    # Fetch current month monthly allocation status for this consumer
    current_month = datetime.now().month
    current_year = datetime.now().year
    quotas = consumer_monthly_allocation_status_details.objects.filter(
        consumer=consumer,
        month=current_month,
        year=current_year
    )
    quota_dict = {q.commodity_id: q for q in quotas}

    if current_shop:
        user_card_items = cart_item_details.objects.filter(
            consumer=consumer,
            shop=current_shop,
        )
    else:
        user_card_items = cart_item_details.objects.none()

    cart_dict = {item.commodity.id: item.quantity for item in user_card_items}
    
    for item in allocated_commodities:
        item.in_cart_qty = cart_dict.get(item.commodity.id, 0)
        
        q_obj = quota_dict.get(item.commodity.id)
        purchased = q_obj.purchased_qty if q_obj else 0.00
        allocated = q_obj.allocated_qty if (q_obj and q_obj.allocated_qty > 0) else item.entitlement
        
        # PDS Pending Qty Check
        pending_query = order_item_details.objects.filter(
            order__consumer=consumer,
            order__status__iexact='PENDING',
            commodity=item.commodity
        )
        if current_shop:
            pending_query = pending_query.filter(order__shop=current_shop)
            
        pending_qty = pending_query.aggregate(total_pending=Sum('quantity'))['total_pending'] or 0.00

        # Net Available Remaining Qty = Allocated - Purchased - Pending
        net_remaining = max(0.00, float(allocated) - float(purchased) - float(pending_qty))
        
        item.purchased_qty = purchased
        item.pending_qty = pending_qty
        item.remaining_qty = net_remaining
        
        # Selected shop physical stock check for PDS
        shop_stock_obj = None
        if current_shop:
            shop_stock_obj = shop_commodity_details.objects.filter(
                shop=current_shop,
                commodity=item.commodity
            ).first()
            
        physical_stock = shop_stock_obj.stock_quantity if shop_stock_obj else 0.00
        item.physical_stock = physical_stock
        
        # Out of stock or fully purchased flags
        if physical_stock <= 0:
            item.is_out_of_stock = True
        else:
            item.is_out_of_stock = False

        if (float(purchased) + float(pending_qty)) >= float(allocated) or (q_obj and q_obj.is_fully_purchased):
            item.is_fully_purchased = True
        else:
            item.is_fully_purchased = False

    # ================= 2. NON-PDS COMMODITIES SECTION =================
    non_pds_items = []
    if current_shop:
        non_pds_items = shop_commodity_details.objects.filter(
            shop=current_shop,
            commodity__is_non_pds=True,
            commodity__is_deleted=False,
        ).select_related('commodity')

        for item in non_pds_items:
            item.in_cart_qty = cart_dict.get(item.commodity.id, 0)
            
            # Non-PDS pending qty check
            pending_non_pds_qty = order_item_details.objects.filter(
                order__consumer=consumer,
                order__shop=current_shop,
                order__status__iexact='PENDING',
                commodity=item.commodity
            ).aggregate(total_pending=Sum('quantity'))['total_pending'] or 0.00
            
            item.pending_qty = pending_non_pds_qty

    context = get_portal_context('consumer', {
        'consumer': consumer,
        'card_type': user_card_type,
        'nearby_shops': nearby_shops,
        'selected_shop': current_shop,
        'allocated_commodities': allocated_commodities,
        'non_pds_commodities': non_pds_items,
        'title': 'Consumer-Purchase',
    })

    return render(request, 'consumer/product_details.html', context)

def add_to_cart_views(request, commodity_id):
    mobile_number = request.session.get('consumer_mobile')
    selected_shop_id = request.session.get('selected_shop_id')

    if not mobile_number:
        return JsonResponse({'status': 'error', 'message': 'Please login first!'}, status=401)

    if not selected_shop_id:
        return JsonResponse({'status': 'error', 'message': 'Please Select Shop First!'}, status=400)
    
    consumer = consumer_details.objects.get(mobile_number=mobile_number)
    commodity = commodity_details.objects.get(id=commodity_id)
    shop = shop_details.objects.filter(shop_id=selected_shop_id).first()

    if not commodity.is_non_pds:
        allocation = consumer_allocation_details.objects.filter(
            consumer=consumer,
            commodity=commodity
        ).first()

        if not allocation or allocation.entitlement <= 0:
            return JsonResponse({
                'status': 'limit_reached',
                'message': f'No commodity allocated for {commodity.commodity}!'
            })

        # Check current month quota purchase status & remaining qty
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_status = consumer_monthly_allocation_status_details.objects.filter(
            consumer=consumer,
            commodity=commodity,
            month=current_month,
            year=current_year
        ).first()

        if monthly_status and monthly_status.is_fully_purchased:
            return JsonResponse({
                'status': 'limit_reached',
                'message': 'Quota already fully purchased for this month! Wait for next renewal.'
            })

        # Allowed max quantity is remaining_qty if partial purchase exists, else full entitlement
        allowed_max_qty = monthly_status.remaining_qty if monthly_status else allocation.entitlement

        cart_item = cart_item_details.objects.filter(
            consumer=consumer, 
            commodity=commodity,
            shop=shop,
        ).first()
        
        current_qty = cart_item.quantity if cart_item else 0

        if current_qty >= allowed_max_qty:
            return JsonResponse({
                'status': 'limit_reached',
                'message': f'Limit reached ({allowed_max_qty} {commodity.unit} remaining)'
            })

        new_qty = allowed_max_qty # or increment based on button action
        if cart_item:
            cart_item.quantity = new_qty
            cart_item.save()
        else:
            cart_item = cart_item_details.objects.create(
                consumer=consumer,
                commodity=commodity,
                quantity=new_qty,
                shop=shop,
            )

        return JsonResponse({
            'status': 'success',
            'item_qty': float(cart_item.quantity)
        })

    else:
        selected_shop_id = request.session.get('selected_shop_id')
        shop_stock = None
        if selected_shop_id:
            shop_stock = shop_commodity_details.objects.filter(
                commodity=commodity,
                shop=shop,
            ).first()

        if not shop_stock or shop_stock.stock_quantity <= 0:
            return JsonResponse({
                'status': 'limit_reached',
                'message': 'Out of Stock !'
            })  

        cart_item, created = cart_item_details.objects.get_or_create(
            consumer=consumer,
            commodity=commodity,
            shop=shop,
            defaults={'quantity': 1}
        )

        if not created:
            if shop_stock and (cart_item.quantity + 1) > shop_stock.stock_quantity:
                return JsonResponse({
                    'status': 'limit_reached',
                    'message': f'exeed stock (available stock: {shop_stock.stock_quantity})'
                })
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({
            'status': 'success',
            'item_qty': int(cart_item.quantity)
        })
    
def consumer_check_and_create_monthly_quota_views(consumer): # future update.
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get card details of the consumer to know their card type (e.g., PHH, AAY, etc.)
    try:
        card = card_details.objects.get(card_number=consumer.card_number)
        card_type_obj = card.card_type # based on your relation
    except consumer_details.DoesNotExist:
        return

    # Fetch allocated commodities for this card type from commodity_allocation_details
    allocations = commodity_allocation_details.filter(card_type=card.card_type)
    
    for alloc in allocations:
        # Check if quota status already exists for this month/year
        quota_obj, created = consumer_monthly_allocation_status_details.get_or_create(
            consumer=consumer,
            commodity=alloc.commodity,
            month=current_month,
            year=current_year,
            defaults={
                'allocated_qty': alloc.quantity,
                'remaining_qty': alloc.quantity,
                'purchased_qty': 0.00,
                'is_fully_purchased': False,
                'is_partially_purchased': False
            }
        )

@transaction.atomic
def consumer_checkout_process_views(request, consumer, shop):
    cart_items = cart_item_details.filter(consumer=consumer, shop=shop)
    if not cart_items.exists():
        return False, "Cart is empty!"

    current_month = datetime.now().month
    current_year = datetime.now().year
    total_order_amount = 0

    # 1. Validation for PDS items quota limits
    for item in cart_items:
        if not item.commodity.is_non_pds: # PDS Item
            try:
                quota = consumer_monthly_allocation_status_details.get(
                    consumer=consumer,
                    commodity=item.commodity,
                    month=current_month,
                    year=current_year
                )
                if quota.is_fully_purchased:
                    return False, f"{item.commodity.commodity} - இந்த மாதத்திற்கான quota முழுமையாக பெறப்பட்டுவிட்டது!"
                if item.quantity > quota.remaining_qty:
                    return False, f"{item.commodity.commodity} - மீதமுள்ள அளவு ({quota.remaining_qty}) விட அதிகமாக வாங்க முடியாது!"
            except consumer_monthly_allocation_status_details.DoesNotExist:
                return False, f"{item.commodity.commodity} - Quota details not found for this month."

        # 2. Check Shop Stock Availability
        try:
            shop_stock = shop_commodity_details.get(shop=shop, commodity=item.commodity)
            if shop_stock.stock_quantity < item.quantity:
                return False, f"{item.commodity.commodity} - கடையில் போதுமான இருப்பு இல்லை!"
        except shop_commodity_details.DoesNotExist:
            return False, f"{item.commodity.commodity} - இந்த கடையில் இருப்பு விவரங்கள் இல்லை."

    # 3. Create Order
    token = f"TNPDS-{timezone.now().strftime('%Y%m%d%H%M%S')}-{consumer.card_number}"
    order = order_details.objects.create(
        token_number=token,
        consumer=consumer,
        shop=shop,
        status='DELIVERED'
    )

    # 4. Process Items & Update Stocks / Quotas
    for item in cart_items:
        item_total = item.get_total_price()
        total_order_amount += item_total

        order_item_details.create(
            order=order,
            commodity=item.commodity,
            quantity=item.quantity,
            price=item.commodity.price,
            total_price=item_total
        )

        # Reduce Shop Stock
        shop_stock = shop_commodity_details.get(shop=shop, commodity=item.commodity)
        shop_stock.stock_quantity -= item.quantity
        shop_stock.save()

        # If PDS item, update Quota status (Partial or Full)
        if not item.commodity.is_non_pds:
            quota =consumer_monthly_allocation_status_details.get(
                consumer=consumer,
                commodity=item.commodity,
                month=current_month,
                year=current_year
            )
            quota.purchased_qty += item.quantity
            quota.remaining_qty = quota.allocated_qty - quota.purchased_qty
            quota.last_purchased_at = timezone.now()

            if quota.remaining_qty <= 0:
                quota.is_fully_purchased = True
                quota.is_partially_purchased = False
            else:
                quota.is_partially_purchased = True
            
            quota.save()

    order.total_amount = total_order_amount
    order.save()

    # Clear Cart after successful checkout
    cart_items.delete()

    return True, "Purchase successful and stock updated live!"        

def checkout_bill_views(request):
    mobile_number = request.session.get('consumer_mobile')
    selected_shop_id = request.session.get('selected_shop_id')

    if not mobile_number:
        return redirect('consumer_login')
    if not selected_shop_id:
        return redirect('consumer_product_details')

    consumer = consumer_details.objects.get(mobile_number=mobile_number)
    shop = shop_details.objects.filter(shop_id=selected_shop_id).first()

    cart_items = cart_item_details.objects.filter(
        consumer=consumer,
        shop=shop,
        commodity__is_deleted=False
    ).select_related('commodity')

    if not cart_items.exists():
        return redirect('consumer_product_details')

    token_number = f"TNPDS-{timezone.now().strftime('%d%m%Y%H%M%S')}-{(consumer.pk)[-4:]}"
    total_amount = sum(item.quantity * item.commodity.price for item in cart_items)

    order = order_details.objects.create(
        token_number=token_number,
        consumer=consumer,
        shop=shop,
        total_amount=total_amount,
        status='PENDING'
    )

    for item in cart_items:
        order_item_details.objects.create(
            order=order,
            commodity=item.commodity,
            quantity=item.quantity,
            price=item.commodity.price,
            total_price=item.quantity * item.commodity.price
        )

    cart_items.delete()

    context=get_portal_context('consumer',
                               {
                                   
                                'order': order,
                                'cart_items': order.items.all(),
                                'title':'Consumer-Bill',

                               })

    return render(request, 'consumer/bill_receipt.html',context)

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
    mobile_number = request.session.get('consumer_mobile')
    selected_shop_id = request.session.get('selected_shop_id')

    if not mobile_number:
        return redirect('consumer_login')

    if not selected_shop_id:
        return redirect('consumer_product_details')

    consumer = consumer_details.objects.get(mobile_number=mobile_number)

    cart_items = cart_item_details.objects.filter(
        consumer=consumer,
        commodity__is_deleted=False,
        shop__shop_id=selected_shop_id,
    ).select_related('commodity','shop')

    total_amount = sum(item.quantity * item.commodity.price for item in cart_items)
    total_items = cart_items.count()

    context=get_portal_context('consumer',{
                                        'consumer': consumer,
                                        'cart_items': cart_items,
                                        'total_amount': total_amount,
                                        'total_items': total_items,
                                        'selected_shop_id': selected_shop_id,
                                        'title':'Consumer-Cart'
    })

    return render(request, 'consumer/cart_view.html',context)

def consumer_purchase_history_views(request):
    mobile_number = request.session.get('consumer_mobile')
    if not mobile_number:
        return redirect('consumer_login')
    
    consumer = consumer_details.objects.filter(mobile_number=mobile_number).first()
    if not consumer:
        return redirect('consumer_login')
    
    # Get and safely convert filter parameters to integers
    try:
        selected_month = int(request.GET.get('month', datetime.now().month))
    except (ValueError, TypeError):
        selected_month = datetime.now().month

    try:
        selected_year = int(request.GET.get('year', datetime.now().year))
    except (ValueError, TypeError):
        selected_year = datetime.now().year

    month_choices = [(i, calendar.month_name[i]) for i in range(1, 13)]

    # Fetch orders for this consumer filtered by month/year (includes PENDING, DELIVERED, etc.)
    orders = order_details.objects.filter(
        consumer__mobile_number=mobile_number,
        order_date__month=selected_month,
        order_date__year=selected_year
    ).order_by('-order_date')

    # Fetch current month quota and partial purchase statuses
    quotas = consumer_monthly_allocation_status_details.objects.filter(
        consumer__mobile_number=mobile_number,
        month=selected_month,
        year=selected_year
    )

    context = get_portal_context('consumer', {
        'consumer': consumer,
        'orders': orders,
        'quotas': quotas,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_choices': month_choices,
        'title':'Consumer-Purchase-History',
    })
    return render(request, 'consumer/purchase_history.html', context)

def consumer_forgot_password_views(request): # future update.
    if request.method == "POST":
        mobile_number = request.POST.get('mobile_number')
        new_password = request.POST.get('new_password')

        try:
            consumer = consumer_details.objects.get(mobile_number=mobile_number)
            
            consumer.password = new_password  
            consumer.save()

            messages.success(request, "கடவுச்சொல் வெற்றிகரமாக மாற்றப்பட்டது! புதிய கடவுச்சொல்லைப் பயன்படுத்தி உள்நுழையவும்.")
            return redirect('consumer_login') 

        except consumer.DoesNotExist:
            messages.error(request, "இந்த மொபைல் எண் பதிவு செய்யப்படவில்லை. சரியான எண்ணை உள்ளிடவும்!")
            return redirect('consumer_login')

    return redirect('consumer_login')


@never_cache
def shop_worker_signup_views(request):
    photos = portal_photo_details.objects.filter(portal_type='shop', is_active=True).order_by('display_order')

    if request.method == 'POST':
        form = shop_worker_signup(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            selected_shop_obj = data['shop_id']
            print(f'shop id value: {selected_shop_obj}')

            actual_shop_id = selected_shop_obj.shop_id if hasattr(selected_shop_obj, 'shop_id') else str(selected_shop_obj)          
            print(f'shop id value: {actual_shop_id}')


            shop_worker_id = data['shop_worker_id']
            mobile_number = data['mobile_number']
            password = data['password']

            #  Existing check for Shop Worker ID and Mobile Number
            if shop_worker_details.objects.filter(shop_worker_id=shop_worker_id).exists():
                messages.error(request, 'Shop worker ID already registered')
                return redirect('shop_worker_login')
            elif shop_worker_details.objects.filter(mobile_number=mobile_number).exists():
                messages.error(request, 'Mobile number already registered enter new number or go to login')  
                return redirect('shop_worker_login')
            else:   
                shop_obj, created = shop_details.objects.get_or_create(
                    shop_id=actual_shop_id,
                    defaults={
                        'name': f'Fair Price Shop {actual_shop_id}',
                        'total_card_holders': 0,
                        'address': 'tamil nadu',
                    }
                )

                shop_worker_details.objects.create(
                    shop_id=shop_obj,  # Model field name 'shop' 
                    shop_worker_id=shop_worker_id,
                    mobile_number=mobile_number,
                    password=password
                )
                messages.success(request, 'Shop worker signup successfully')
                return redirect('shop_worker_login')

    else:
        form = shop_worker_signup()    
        
    return render(request, 'common/signup.html',
                   context={
                       'form': form,
                       'title': 'Shop-Worker-SignUp',
                       'subtitle': 'New Shop Worker Registration',
                       'url': '/shop_worker_signup/',
                       'login_url': 'shop_worker_login',
                       'photos': photos,
                   })

@never_cache
def shop_worker_login_views(request):
    photos = portal_photo_details.objects.filter(portal_type='shop', is_active=True).order_by('display_order')

    if request.method=='POST':
        form=shop_worker_login(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            shop_worker_id=data['shop_worker_id']
            password=data['password']

            shop_worker=shop_worker_details.objects.filter(shop_worker_id=shop_worker_id).first()
            if shop_worker:
                if shop_worker.password==password:
                    shop_id=shop_worker.shop_id_id
                    shop_worker_login_details.objects.create(
                    worker_id=shop_worker.shop_worker_id,
                    shop_id=shop_id,
                    
)
                    request.session['logged_shop_id'] = str(shop_id)
                    request.session['logged_worker_id'] = str(shop_worker.shop_worker_id)
                    
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
    return render(request,'common/login.html',
                   context={
                       'form': form,
                       'title': 'Shop-Worker-LogIn',
                       'subtitle': 'Shop Worker Login Portal',
                       'user_type': 'Shop Worker',
                       'url': '/shop_worker_login/',
                       'signup_url': 'shop_worker_signup',
                       'home_url': 'home',
                       'new_user': 'Shop Worker',
                       'photos':photos,
                                             }) 

def shop_worker_logout_views(request):
    request.session.flush()
    
    messages.success(request, 'Logged out successfully!')
    return redirect('shop_worker_login')                                          

def shop_profile_views(request):
    shop_id = request.session.get('logged_shop_id')
    worker_id = request.session.get('logged_worker_id')

    if not shop_id or not worker_id:
        return redirect('shop_worker_login')

    worker = shop_worker_details.objects.filter(shop_worker_id=worker_id).first()
    shop = shop_details.objects.filter(shop_id=shop_id).first()

    context = get_portal_context('shop', {
                                'shop': shop,
                                'worker':worker,
                                'title':'Shop-Worker-Profile',
                                })

    return render(request, 'shop/profile.html',context)

def shop_home_page_views(request):
    photos = portal_photo_details.objects.filter(portal_type='shop', is_active=True).order_by('display_order')
    context = get_portal_context('shop', 
                                 {
                                    'photos': photos,
                                    'title':'Shop-Home',
                                    })
  
    return render(request, 'common/home_page.html', context)

def shop_product_details_views(request):
    shop_id = request.session.get('logged_shop_id')

    if not shop_id:
        return redirect('shop_worker_login')
    
    current_shop = shop_details.objects.get(shop_id=shop_id)

    #  1. PDS Commodities:  shop- stock table
    pds_items = shop_commodity_details.objects.filter(
        shop=current_shop,
        commodity__is_non_pds=False,
        commodity__is_deleted=False
    ).select_related('commodity').order_by('commodity__commodity')

    #  2. Non-PDS Commodities: shop local items
    non_pds_items = shop_commodity_details.objects.filter(
        shop=current_shop, 
        commodity__is_non_pds=True,
        commodity__is_deleted=False,
    ).select_related('commodity')
    
    context = get_portal_context('shop', {
        'pds_commodities': pds_items,
        'non_pds_commodities': non_pds_items,
        'title': 'Shop-Products',
    })

    return render(request, 'shop/product_details.html', context) 

def shop_add_commodity(request):
    shop_id = request.session.get('logged_shop_id')
    if not shop_id:
        return redirect('shop_worker_login')

    current_shop = shop_details.objects.get(shop_id=shop_id)

    if request.method == 'POST':
        item_name = request.POST.get('commodity', '').strip().capitalize()
        price = request.POST.get('price')
        unit = request.POST.get('unit')
        image = request.FILES.get('commodity_image')
        stock = request.POST.get('stock', 0)

        commodity_obj, created = commodity_details.objects.get_or_create(
            commodity=item_name,
            defaults={
                'price': price,
                'unit': unit,
                'commodity_image': image,
                'is_non_pds': True
            }
        )

        shop_commodity_details.objects.update_or_create(
            shop=current_shop,
            commodity=commodity_obj,
            defaults={
                'custom_price': price,
                'stock_quantity': stock
            }
        )

        messages.success(request, f'{item_name} added successfully!')
        return redirect('shop_add_commodity')

    non_pds_items = shop_commodity_details.objects.filter(
        shop=current_shop,
        commodity__is_non_pds=True
    ).select_related('commodity')

    context=get_portal_context('shop',{
                             'non_pds_commodities': non_pds_items,
                             'title':'Shop-Add-commodity',
                             })

    return render(request, 'shop/add_commodity.html',context)

def shop_edit_commodity_views(request, item_id):
    shop_id = request.session.get('logged_shop_id')
    if not shop_id:
        return redirect('shop_worker_login')

    current_shop = get_object_or_404(shop_details, shop_id=shop_id)
    shop_item = get_object_or_404(shop_commodity_details, id=item_id, shop=current_shop)

    if request.method == 'POST':
        custom_price = request.POST.get('price')
        stock_qty = request.POST.get('stock')
        image = request.FILES.get('commodity_image')

        shop_item.custom_price = custom_price
        shop_item.stock_quantity = stock_qty
        shop_item.save()

        if image:
            shop_item.commodity.commodity_image = image
            shop_item.commodity.save()

        messages.success(request, f"{shop_item.commodity.commodity} updated successfully!")
        return redirect('shop_add_commodity')

    context = get_portal_context('shop', {
        'shop_item': shop_item,
        'title':'Shop-Edit-Commodity',
    })

    return render(request, 'shop/edit_commodity.html', context)

def shop_delete_commodity_views(request, item_id):
    shop_id = request.session.get('logged_shop_id')
    if not shop_id:
        return redirect('shop_worker_login')

    current_shop = get_object_or_404(shop_details, shop_id=shop_id)
    shop_item = get_object_or_404(shop_commodity_details, id=item_id, shop=current_shop)

    item_name = shop_item.commodity.commodity
    shop_item.delete() 

    messages.success(request, f"{item_name} removed from your shop inventory!")
    return redirect('shop_add_commodity')

def shop_order_delivery_views(request, token_number):
    if request.method == 'POST':
        try:
            shop_id = request.session.get('logged_shop_id')
            current_shop = shop_details.objects.filter(shop_id=shop_id).first()
            
            order = order_details.objects.filter(token_number=token_number, shop=current_shop).first()
            if not order:
                return JsonResponse({'status': 'error', 'message': 'Order not found for this shop!'})
            
            if order.status == 'DELIVERED':
                return JsonResponse({'status': 'error', 'message': 'Order is already delivered!'})
            
            
            # 1. Update order status to DELIVERED
            order.status = 'DELIVERED'
            order.save()
            
            # 2. Reduce Physical Stock & Print values for Debugging
            for item in order.items.all():
                shop_stock = shop_commodity_details.objects.filter(
                    shop=order.shop,
                    commodity=item.commodity
                ).first()
                
                if shop_stock:
                    shop_stock.stock_quantity -= item.quantity
                    shop_stock.save()
                    
            
            # 3. Update monthly allocation / quota status
            for item in order.items.all():
                monthly_status, created = consumer_monthly_allocation_status_details.objects.get_or_create(
                    consumer=order.consumer,
                    commodity=item.commodity,
                    month=order.order_date.month,
                    year=order.order_date.year,
                    defaults={
                        'allocated_qty': 0.00,
                        'remaining_qty': 0.00,
                    }
                )
                
                if created or monthly_status.allocated_qty == 0:
                    base_alloc = consumer_allocation_details.objects.filter(
                        consumer=order.consumer,
                        commodity=item.commodity
                    ).first()
                    
                    alloc_val = base_alloc.entitlement if base_alloc else item.quantity
                    monthly_status.allocated_qty = alloc_val
                    monthly_status.remaining_qty = alloc_val
                
                monthly_status.purchased_qty += item.quantity
                monthly_status.remaining_qty = monthly_status.allocated_qty - monthly_status.purchased_qty
                
                if monthly_status.purchased_qty >= monthly_status.allocated_qty:
                    monthly_status.is_fully_purchased = True
                    monthly_status.is_partially_purchased = False
                elif monthly_status.purchased_qty > 0:
                    monthly_status.is_partially_purchased = True
                    
                monthly_status.last_purchased_at = timezone.now()
                monthly_status.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def shop_order_search_views(request):
    search_query = request.GET.get('token', '').strip()
    order = None
    order_items = []
    error_message = None

    if search_query:
        # using Token number fetch :
        order = order_details.objects.filter(token_number__icontains=search_query).first()
        if order:
            order_items = order_item_details.objects.filter(order=order).select_related('commodity')
        else:
            error_message = "No order found with this Token Number!"

    context = get_portal_context('shop',{
        'order': order,
        'order_items': order_items,
        'search_query': search_query,
        'error_message': error_message,
        'title':'Shop-Order-Verify',
    })
    return render(request, 'shop/order_verification.html', context)

def shop_stock_dashboard_views(request):
    shop_id = request.session.get('logged_shop_id')
    if not shop_id:
        return redirect('shop_worker_login')
        
    shop = shop_details.objects.filter(shop_id=shop_id).first()
    if not shop:
        return redirect('shop_worker_login')
    
    # Shop-oda full statistics :
    stats = get_shop_statistics(shop)
    
    # stock item : pending delivery quantity attach :
    if 'shop_stocks' in stats:
        for stock in stats['shop_stocks']:
            # shop PENDING order items total quantity sum :
            pending_qty = order_item_details.objects.filter(
                order__shop=shop,
                order__status='PENDING',
                commodity=stock.commodity
            ).aggregate(total=Sum('quantity'))['total'] or 0.00

            pending_qty = Decimal(str(pending_qty)) if pending_qty is not None else Decimal('0.00')
            
            stock.pending_delivery_qty = pending_qty
            # Net available physical stock (Physical Stock - Pending Delivery)
            stock.net_available = stock.stock_quantity - pending_qty

    context = get_portal_context('shop', {
        'shop': shop,
        'stats': stats,  # pass to Template
        'stocks': stats['shop_stocks'],
        'title':'Shop-DashBoard',
    })
    return render(request, 'shop/stock_dashboard.html', context)

def get_shop_statistics(shop):
    consumers = consumer_details.objects.filter(home_shop=shop).prefetch_related('family_members', 'card_type')
    
    total_cards = consumers.count()
    total_members = 0
    total_adults = 0
    total_children = 0
    
    card_type_stats = {}
    
    for consumer in consumers:
        c_type = consumer.card_type.card_type if consumer.card_type else "Unknown"
        is_pds = getattr(consumer.card_type, 'is_pds_allocation', False) if consumer.card_type else False
        
        if c_type not in card_type_stats:
            card_type_stats[c_type] = {
                'card_count': 0,
                'member_count': 0,
                'is_pds': is_pds
            }
        
        # Card count increase
        card_type_stats[c_type]['card_count'] += 1
        
        # Family members breakdown
        members = consumer.family_members.all()
        m_count = members.count()
        total_members += m_count
        card_type_stats[c_type]['member_count'] += m_count
        
        adults = sum(1 for m in members if getattr(m, 'is_adult', False) or str(getattr(m, 'status', '')).strip().capitalize() == 'Adult')
        total_adults += adults
        total_children += (m_count - adults)

    # Shop  Required Stocks summary
    shop_stocks = shop_commodity_details.objects.filter(shop=shop).select_related('commodity')
    
    return {
        'total_cards': total_cards,
        'total_members': total_members,
        'total_adults': total_adults,
        'total_children': total_children,
        'card_type_stats': card_type_stats,  # Ex: {'PHH': {'card_count': 120, 'member_count': 450, 'is_pds': True}}
        'shop_stocks': shop_stocks,
    }



@never_cache
def officer_signup_views(request):
    photos = portal_photo_details.objects.filter(portal_type='officer', is_active=True).order_by('display_order')

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
    return render(request,'common/signup.html',
                   context={
                            'form': form,
                            'title': 'Officer-SignUp',
                            'subtitle': 'New Officer Registration',
                            'url': '/officer_signup/',
                            'login_url': 'officer_login',
                            'photos':photos,
                                             }) 

@never_cache
def officer_login_views(request):
    photos = portal_photo_details.objects.filter(portal_type='officer', is_active=True).order_by('display_order')
    
    if request.method=='POST':
        form=officer_login(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            officer_id=data['officer_id']
            password=data['password']

            officer=officer_details.objects.filter(officer_id=officer_id).first()
            if officer:
                if officer.password==password:
                    request.session['logged_officer_id'] = str(officer.officer_id)
                    messages.success(request,'login successfull')
                    return redirect('officer_home_page')
                else:
                    messages.error(request,'wrong password')
            else:
                messages.error(request,'officer not found')      
                return redirect('officer_signup')


    else:
        form=officer_login()    
    return render(request,'common/login.html',
                   context={
                       'form': form,
                       'title': 'Officer-LogIn',
                       'subtitle': 'Officer Login Portal',
                       'user_type': 'Officer',
                       'url': '/officer_login/',
                       'signup_url': 'officer_signup',
                       'home_url': 'home',
                       'new_user': 'Officer',
                       'photos':photos,
                                             }) 

def officer_logout_views(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('officer_login')

def officer_home_page_views(request):
    photos = portal_photo_details.objects.filter(portal_type='officer', is_active=True).order_by('display_order')
    context = get_portal_context('officer', {
                                'photos': photos,
                                'title':'Officer-Home',
                                })

    return render(request, 'common/home_page.html', context)

def officer_pending_request_views(request):
    officer_id = request.session.get('logged_officer_id')
    if not officer_id:
        messages.error(request, 'Please login first!')
        return redirect('officer_login')
    
    officer = officer_details.objects.filter(officer_id=officer_id).first()
    if not officer:
        messages.error(request, 'Officer details not found!')
        return redirect('officer_login')

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action') # 'APPROVE' or 'REJECT'
        officer_remarks = request.POST.get('officer_remarks', '').strip()

        crud_req = get_object_or_404(consumer_crud_details, id=request_id)

        if action == 'APPROVE':
            crud_req.status = 'APPROVED'
            crud_req.reviewed_by = officer
            crud_req.reviewed_at = timezone.now()
            crud_req.officer_remarks = officer_remarks
            crud_req.save()

            #  1. ADD REQUEST APPROVAL :
            if crud_req.request_type == 'ADD':
                family_members_details.objects.create(
                    consumer=crud_req.consumer,
                    name=crud_req.name,
                    dob=crud_req.dob,
                    gender=crud_req.gender,
                    relation=crud_req.relation,
                    mobile_number=crud_req.mobile_number,
                    aadhaar_number=crud_req.aadhaar_number, 
                )
                
                # Save to History
                consumer_crud_history.objects.create(
                    consumer=crud_req.consumer,
                    card_number=crud_req.consumer.card_number,
                    aadhaar_number=crud_req.aadhaar_number, 
                    action_type="FAMILY_MEMBER_ADD_APPROVED",
                    description=f"New family member '{crud_req.name}' added and approved by officer {officer.officer_id}. Remarks: {officer_remarks}",
                    performed_by_officer=officer
                )
                
                # Recalculate allocations based on new family member count
                update_consumer_allocations(crud_req.consumer)
                messages.success(request, f"New family member '{crud_req.name}' added successfully & recorded in audit history!")

            # 2. EDIT REQUEST APPROVAL
            elif crud_req.request_type == 'EDIT' and crud_req.member:
                member = crud_req.member
                member.name = crud_req.name
                member.dob = crud_req.dob
                member.gender = crud_req.gender
                member.relation = crud_req.relation
                member.mobile_number = crud_req.mobile_number
                
                if hasattr(member, 'email_id'):
                    member.email_id = crud_req.email_id
                
                member.save()
                update_consumer_allocations(crud_req.consumer)

                consumer_crud_history.objects.create(
                    consumer=crud_req.consumer,
                    card_number=crud_req.consumer.card_number,
                    aadhaar_number=crud_req.aadhaar_number, 
                    action_type="FAMILY_MEMBER_EDIT_APPROVED",
                    description=f"Family member '{member.name}' edit approved by officer {officer.officer_id}. Remarks: {officer_remarks}",
                    performed_by_officer=officer
                )
                messages.success(request, f"Edit request for Card No: {crud_req.consumer.card_number} has been APPROVED successfully!")

            #  3. DELETE REQUEST APPROVAL
            elif crud_req.request_type == 'DELETE' and crud_req.member:
                member_obj = crud_req.member
                member_name = member_obj.name

                consumer_crud_history.objects.create(
                    consumer=crud_req.consumer,
                    card_number=crud_req.consumer.card_number,
                    aadhaar_number=crud_req.aadhaar_number, 
                    action_type="FAMILY_MEMBER_DELETED",
                    description=f"Family Member '{member_name}' deleted by Officer {officer.officer_id}. Reason: {crud_req.reason}. Remarks: {officer_remarks}",
                    performed_by_officer=officer
                )
                
                member_obj.delete()
                update_consumer_allocations(crud_req.consumer)

                messages.success(request, f"Family member '{member_name}' deleted successfully & recorded in audit history!")

            crud_req.delete()

        elif action == 'REJECT':
            crud_req.status = 'REJECTED'
            crud_req.reviewed_by = officer
            crud_req.reviewed_at = timezone.now()
            crud_req.officer_remarks = officer_remarks
            crud_req.save()
            
            consumer_crud_history.objects.create(
                consumer=crud_req.consumer,
                card_number=crud_req.consumer.card_number,
                aadhaar_number=crud_req.aadhaar_number, 
                action_type=f"FAMILY_MEMBER_{crud_req.request_type}_REJECTED",
                description=f"{crud_req.request_type} request for {crud_req.name} rejected by Officer {officer.officer_id}. Remarks: {officer_remarks}",
                performed_by_officer=officer
            )

            messages.warning(request, f"Request for Card No: {crud_req.consumer.card_number} has been rejected.")
            crud_req.delete()

        return redirect('officer_pending_request')

    filter_type = request.GET.get('type', 'ALL')
    if filter_type == 'EDIT':
        pending_requests = consumer_crud_details.objects.filter(status='PENDING', request_type='EDIT').order_by('requested_at')
    elif filter_type == 'DELETE':
        pending_requests = consumer_crud_details.objects.filter(status='PENDING', request_type='DELETE').order_by('requested_at')
    elif filter_type == 'ADD':
        pending_requests = consumer_crud_details.objects.filter(status='PENDING', request_type='ADD').order_by('requested_at')
    else:
        pending_requests = consumer_crud_details.objects.filter(status='PENDING').order_by('requested_at')
    
    context = get_portal_context('officer', {
        'pending_requests': pending_requests,
        'current_filter': filter_type,
        'title':'Officer-Requests',
    })
    return render(request, 'officer/pending_request.html', context)

def officer_review_edit_request_views(request, req_id):
    officer_id = request.session.get('logged_officer_id')
    if not officer_id:
        messages.error(request, 'Please login first!')
        return redirect('officer_login')

    crud_req = get_object_or_404(consumer_crud_details, id=req_id)
    member = crud_req.member  

    # Changed fields  convert into list  (Ex: "name, dob" -> ['name', 'dob'])
    changed_fields_list = []
    if hasattr(crud_req, 'changed_fields') and crud_req.changed_fields:
        changed_fields_list = [f.strip().lower() for f in str(crud_req.changed_fields).split(',')]

    if request.method == 'POST':
        officer_remarks = request.POST.get('officer_remarks', '').strip()
        officer = officer_details.objects.filter(officer_id=officer_id).first()
        updated_fields = []

        if member:
            # Ovvoru field-kum check panrom, antha field change list-la iruntha mattum action edukkum
            # pending for reject action 
            # note future update needed 
            if 'name' in changed_fields_list and request.POST.get('name_action') == 'APPROVE':
                member.name = crud_req.name
                updated_fields.append('name')

            if 'dob' in changed_fields_list and request.POST.get('dob_action') == 'APPROVE':
                member.dob = crud_req.dob
                updated_fields.append('dob')

            if 'gender' in changed_fields_list and request.POST.get('gender_action') == 'APPROVE':
                member.gender = crud_req.gender
                updated_fields.append('gender')

            if 'relation' in changed_fields_list and request.POST.get('relation_action') == 'APPROVE':
                member.relation = crud_req.relation
                updated_fields.append('relation')

            if 'mobile_number' in changed_fields_list and request.POST.get('mobile_action') == 'APPROVE':
                member.mobile_number = crud_req.mobile_number
                updated_fields.append('mobile_number')

            if 'email_id' in changed_fields_list and hasattr(member, 'email_id') and request.POST.get('email_action') == 'APPROVE':
                member.email_id = getattr(crud_req, 'email_id', member.email_id)
                updated_fields.append('email_id')
            
            member.save()
            update_consumer_allocations(crud_req.consumer)

        consumer_crud_history.objects.create(
            consumer=crud_req.consumer,
            card_number=crud_req.consumer.card_number,
            aadhaar_number=crud_req.aadhaar_number,
            action_type="FIELD_LEVEL_EDIT_REVIEWED",
            description=f"Field-level edit reviewed by officer {officer.officer_id}. Approved fields: {updated_fields}. Remarks: {officer_remarks}",
            performed_by_officer=officer
        )
        
        crud_req.delete()
        messages.success(request, "Field-level edit request processed successfully!")
        return redirect('officer_pending_request')

    context = get_portal_context('officer', {
        'crud_req': crud_req,
        'member': member,
        'changed_fields_list': changed_fields_list, 
         'title':'Officer-Edit-Request',
    })
    return render(request, 'officer/review_edit_request.html', context)

def officer_review_add_delete_request_views(request, req_id):
    officer_id = request.session.get('logged_officer_id')
    if not officer_id:
        messages.error(request, 'Please login first!')
        return redirect('officer_login')

    crud_req = get_object_or_404(consumer_crud_details, id=req_id)
    member = crud_req.member  # from Delete request fetch andha member details

    if request.method == 'POST':
        action = request.POST.get('action') # 'APPROVE' or 'REJECT'
        officer_remarks = request.POST.get('officer_remarks', '').strip()
        officer = officer_details.objects.filter(officer_id=officer_id).first()

        if action == 'APPROVE':
            crud_req.status = 'APPROVED'
            crud_req.reviewed_by = officer
            crud_req.reviewed_at = timezone.now()
            crud_req.officer_remarks = officer_remarks
            crud_req.save()

            if crud_req.request_type == 'ADD':
                family_members_details.objects.create(
                    consumer=crud_req.consumer,
                    name=crud_req.name,
                    dob=crud_req.dob,
                    gender=crud_req.gender,
                    relation=crud_req.relation,
                    mobile_number=crud_req.mobile_number,
                    aadhaar_number=crud_req.aadhaar_number,
                )
                update_consumer_allocations(crud_req.consumer)
                messages.success(request, f"New family member '{crud_req.name}' added successfully!")

            elif crud_req.request_type == 'DELETE' and member:
                member_name = member.name
                member.delete()
                update_consumer_allocations(crud_req.consumer)
                messages.success(request, f"Family member '{member_name}' deleted successfully!")

            consumer_crud_history.objects.create(
                consumer=crud_req.consumer,
                card_number=crud_req.consumer.card_number,
                aadhaar_number=crud_req.aadhaar_number,
                action_type=f"FAMILY_MEMBER_{crud_req.request_type}_APPROVED",
                description=f"{crud_req.request_type} request approved by officer {officer.officer_id}. Remarks: {officer_remarks}",
                performed_by_officer=officer
            )
            crud_req.delete()

        elif action == 'REJECT':
            crud_req.status = 'REJECTED'
            crud_req.reviewed_by = officer
            crud_req.reviewed_at = timezone.now()
            crud_req.officer_remarks = officer_remarks
            crud_req.save()

            consumer_crud_history.objects.create(
                consumer=crud_req.consumer,
                card_number=crud_req.consumer.card_number,
                aadhaar_number=crud_req.aadhaar_number,
                action_type=f"FAMILY_MEMBER_{crud_req.request_type}_REJECTED",
                description=f"{crud_req.request_type} request rejected by officer {officer.officer_id}. Remarks: {officer_remarks}",
                performed_by_officer=officer
            )
            messages.warning(request, f"Request for Card No: {crud_req.consumer.card_number} has been rejected.")
            crud_req.delete()

        return redirect('officer_pending_request')

    context = get_portal_context('officer', {
        'crud_req': crud_req,
        'member': member,
        'title':'Officer-Add-Delete-Request',
    })
    return render(request, 'officer/review_add_delete_request.html', context)
   
def officer_audit_history_views(request):
    officer_id = request.session.get('logged_officer_id')
    if not officer_id:
        messages.error(request, 'Please login first!')
        return redirect('officer_login')

    search_query = request.GET.get('q', '').strip()
    if search_query:
        history_list = consumer_crud_history.objects.filter(card_number__icontains=search_query).order_by('-timestamp')
    else:
        history_list = consumer_crud_history.objects.all().order_by('-timestamp')[:50]

    context = get_portal_context('officer', {
        'history_list': history_list,
        'search_query': search_query,
        'title':'Officer-Request-History',
    })
    return render(request, 'officer/audit_history.html', context)

def officer_profile_views(request):
    officer_id = request.session.get('logged_officer_id')
    if not officer_id:
        messages.error(request, 'Please login first!')
        return redirect('officer_login')

    officer = officer_details.objects.filter(officer_id=officer_id).first()
    if not officer:
        messages.error(request, 'Officer not found!')
        return redirect('officer_login')

    profile_data = [
        ("Officer ID", officer.officer_id),
        ("Mobile Number", officer.mobile_number),
        ("Role", "District Supply Officer / Reviewing Officer"),
        ("Department", "Department of Civil Supplies and Consumer Protection"),
    ]

    context = get_portal_context('officer', {
        'officer': officer,
        'profile_data': profile_data,
        'title':'Officer-Profile',
    })
    return render(request, 'officer/profile.html', context)


@never_cache
def admin_signup_views(request):
    photos = portal_photo_details.objects.filter(portal_type='admin', is_active=True).order_by('display_order')

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
    return render(request,'common/signup.html',
                   context={
                       'form': form,
                       'title': 'Admin-SignUp',
                       'subtitle': 'New Admin Registration',
                       'url': '/admin_signup/',
                       'login_url': 'admin_login',
                       'photos':photos,
                                             }) 

@never_cache
def admin_login_views(request):
    photos = portal_photo_details.objects.filter(portal_type='admin', is_active=True).order_by('display_order')

    if request.method=='POST':
        form=admin_login(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            admin_id=data['admin_id']
            password=data['password']

            admin=admin_details.objects.filter(admin_id=admin_id).first()
            if admin:
                if admin.password==password:
                    request.session['logged_admin_id'] = str(admin.admin_id)
                    request.session['logged_admin_mobile'] = str(admin.mobile_number)
                    messages.success(request,'login successfull')
                    return redirect('admin_home_page')
                else:
                    messages.error(request,'wrong password')
            else:
                messages.error(request,'admin not found')  
                return redirect('admin_signup')


    else:
        form=admin_login()    
    return render(request,'common/login.html',
                   context={
                       'form': form,
                       'title': 'Admin-LogIn',
                       'subtitle': 'Admin Login Portal',
                       'user_type': 'Admin',
                       'url': '/admin_login/',
                       'signup_url': 'admin_signup',
                       'home_url': 'home',
                       'new_user': 'Admin',
                       'photos':photos
                                             }) 

def admin_profile_views(request):
    admin_id = request.session.get('logged_admin_id')
    admin_mobile = request.session.get('logged_admin_mobile')

    context = get_portal_context('admin', {
                                'admin_id': admin_id,
                                'admin_mobile': admin_mobile,
                                'title':'Admin-Profile',
                                
                                })

    if not admin_id:
        return redirect('admin_login')

    return render(request, 'admin/profile.html', context)

def admin_logout_views(request):
    request.session.flush()
    
    messages.success(request, 'Logged out successfully!')
    return redirect('admin_login')                                          

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

    context=get_portal_context('admin',{
                            'form':form,
                            'card_type': all_card_type,
                            'title':'Admin-Add-card-type',

    })

    return render(request,'admin/add_card_type.html',context) 

def admin_home_page_views(request):
    photos = portal_photo_details.objects.filter(portal_type='admin', is_active=True).order_by('display_order')
    context = get_portal_context('admin', {
                                'photos': photos,
                                'title':'Admin-Home',
                                })

    return render(request, 'common/home_page.html', context)

def admin_add_commodity_views(request):
    if request.method == 'POST':
        form = admin_add_commodity(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            enter_commodity = data.get('commodity')
            enter_price = data.get('price')
            enter_unit = data.get('unit')
            enter_image = request.FILES.get('commodity_image')
            enter_is_non_pds = data.get('is_non_pds', False)

            existing_item = commodity_details.objects.filter(commodity__iexact=enter_commodity).first()

            if existing_item:
                if existing_item.is_deleted:
                    existing_item.price = enter_price
                    existing_item.unit = enter_unit
                    existing_item.is_non_pds = enter_is_non_pds
                    if enter_image:
                        existing_item.commodity_image = enter_image
                    existing_item.is_deleted = False 
                    existing_item.save()

                    messages.success(request, f'{enter_commodity} restored and updated successfully!')
                    return redirect('admin_add_commodity')
                else:
                    messages.info(request, f'{enter_commodity} already exists!')
                    return redirect('admin_add_commodity')

            else:
                commodity_details.objects.create(
                    commodity=enter_commodity,
                    price=enter_price,
                    unit=enter_unit,
                    is_non_pds=enter_is_non_pds,
                    commodity_image=enter_image,
                    is_deleted=False
                )
                messages.success(request, f'{enter_commodity} added into db successfully')
                return redirect('admin_add_commodity')
        else:
            print("Form Errors:", form.errors)

    else:
        form = admin_add_commodity()

    pds_items = commodity_details.objects.filter(
        is_non_pds=False,
        is_deleted=False,
    ).order_by('commodity')

    non_pds_items = commodity_details.objects.filter(
        is_non_pds=True,
        is_deleted=False,
    ).order_by('commodity')

    context=get_portal_context('admin',{
                    'form': form,
                    'pds_commodities': pds_items,
                    'non_pds_commodities': non_pds_items,
                    'title':'Admin-Add-Commodity',

    })

    return render(request,'admin/add_commodity.html',context)

def admin_commodity_allocation_views(request, card_id):
    selected_card = get_object_or_404(card_type_details, id=card_id)
    commodities = commodity_details.objects.filter(is_non_pds=False, is_deleted=False)
    
    if request.method == 'POST':
        for commodity in commodities:
            max_qty = request.POST.get(f'max_qty_{commodity.id}', '').strip()
            print(f"DEBUG SAVE: Commodity ID {commodity.id} -> Max Cap: {max_qty}") # Debug print

            commodity_allocation_details.objects.update_or_create(
                card_type=selected_card,
                commodity=commodity,
                defaults={
                    'max_cap': float(max_qty) if max_qty else 0.00,
                    'quantity': float(max_qty) if max_qty else 0.00, # Quantity values save 
                }
            )

        selected_card.is_pds_allocation = True
        selected_card.save()    

        affected_consumers = consumer_details.objects.filter(card_type=selected_card)
        for consumer in affected_consumers:
            update_consumer_allocations(consumer)

        messages.success(request, f'Card-specific max limits updated for {selected_card.card_type} successfully & stock recalculated!')
        return redirect('admin_add_card_type')

    existing_allocations = {
        a.commodity_id: a for a in commodity_allocation_details.objects.filter(card_type=selected_card)
    }

    commodity_list = []
    for commodity in commodities:
        alloc = existing_allocations.get(commodity.id)
        commodity_list.append({
            'id': commodity.id,
            'name': commodity.commodity,
            'unit': commodity.unit,
            'min_qty': commodity.min_qty,
            'group_name': commodity.group_name,
            'group_max_cap': commodity.group_max_cap,
            'max_qty': alloc.max_cap if alloc else 0.00,
            'image': commodity.commodity_image.url if commodity.commodity_image else None,
        })

    context = get_portal_context('admin', {
        'commodity_list': commodity_list,
        'selected_card': selected_card,
        'title':'Admin-Allocate-Commodity',
    })
    
    return render(request, 'admin/allocate_commodity.html', context)

def admin_global_allocation_rates(request):
    commodities = commodity_details.objects.filter(is_non_pds=False, is_deleted=False)

    if request.method == 'POST':
        for commodity in commodities:
            min_qty = request.POST.get(f'min_qty_{commodity.id}', '').strip()
            group_name = request.POST.get(f'group_name_{commodity.id}', '').strip()
            group_max_cap = request.POST.get(f'group_max_cap_{commodity.id}', '').strip()
            adult_rate = request.POST.get(f'adult_rate_{commodity.id}', '').strip()
            child_rate = request.POST.get(f'child_rate_{commodity.id}', '').strip()

            commodity.min_qty = float(min_qty) if min_qty else 0.00
            commodity.group_name = group_name if group_name else None
            commodity.group_max_cap = float(group_max_cap) if group_max_cap else 0.00
            commodity.adult_rate = float(adult_rate) if adult_rate else 0.00
            commodity.child_rate = float(child_rate) if child_rate else 0.00
            commodity.save()

        messages.success(request, 'Global PDS commodity rules and per-head rates updated successfully!')
        return redirect('admin_global_allocation_rates')

    context = get_portal_context('admin', {
        'commodities': commodities,
        'title':'Admin-Global-Allocation',
    })
    return render(request, 'admin/global_allocation_rates.html', context)

def admin_edit_commodity_views(request, commodity_id):
    commodity_item = get_object_or_404(commodity_details, id=commodity_id)

    if request.method == 'POST':
        form = admin_add_commodity(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            commodity_item.commodity = data['commodity']
            commodity_item.price = data['price']
            commodity_item.unit = data.get('unit', commodity_item.unit)
            
            if request.FILES.get('commodity_image'):
                commodity_item.commodity_image = request.FILES.get('commodity_image')
                
            commodity_item.save()
            messages.success(request, f'{commodity_item.commodity} updated successfully!')
            return redirect('admin_add_commodity')
    else:
        form = admin_add_commodity(initial={
            'commodity': commodity_item.commodity,
            'price': commodity_item.price,
            'unit': commodity_item.unit,
        })

    commodity = commodity_details.objects.filter(is_deleted=False)

    context = get_portal_context('admin', {
        'form': form,
        'commodity': commodity,
        'item': commodity_item,
        'title':'Admin-Edit-Commotidy',
    })

    return render(request, 'admin/edit_commodity.html', context)

def admin_delete_commodity_views(request, commodity_id):
    commodity_item = get_object_or_404(commodity_details, id=commodity_id)

    commodity_name = commodity_item.commodity
    
    commodity_item.is_deleted = True
    commodity_item.save()
    
    messages.success(request, f'{commodity_name} deleted successfully!')
    return redirect('admin_add_commodity')

def admin_delete_card_type_views(request, card_id):
    card = get_object_or_404(card_type_details, id=card_id)
    card_name = card.card_type
    card.delete()
    
    messages.error(request, f'Card type "{card_name}" deleted!')
    return redirect('admin_add_card_type')

def admin_statewide_item_stock_monitor_views(request):
    # State-wise consolidated stock & required stock sum for PDS items
    pds_stocks = shop_commodity_details.objects.filter(
        commodity__is_non_pds=False,
        commodity__is_deleted=False
    ).values(
        'commodity__id',
        'commodity__commodity', 
        'commodity__unit', 
        'commodity__is_non_pds'
    ).annotate(
        total_state_stock=Sum('stock_quantity'),
        total_required_stock=Sum('required_stock')
    ).order_by('commodity__commodity')

    # State-wise consolidated stock & required stock sum for Non-PDS items
    non_pds_stocks = shop_commodity_details.objects.filter(
        commodity__is_non_pds=True,
        commodity__is_deleted=False
    ).values(
        'commodity__id',
        'commodity__commodity', 
        'commodity__unit', 
        'commodity__is_non_pds'
    ).annotate(
        total_state_stock=Sum('stock_quantity'),
        total_required_stock=Sum('required_stock')
    ).order_by('commodity__commodity')

    # Statewide total counts
    total_state_cards = shop_details.objects.aggregate(total_cards=Sum('total_card_holders'))['total_cards'] or 0
    total_state_members = family_members_details.objects.count()
    
    # Fair Price Shops list overview
    all_shops = shop_details.objects.filter(is_active=True).order_by('shop_id')
    total_shops_count = all_shops.count()

    context = get_portal_context('admin', {
        'pds_stocks': pds_stocks,           # PDS stocks pass 
        'non_pds_stocks': non_pds_stocks,   # Non-PDS stocks pass 
        'total_state_cards': total_state_cards,
        'total_state_members': total_state_members,
        'all_shops': all_shops,
        'total_shops_count': total_shops_count,
        'title':'Admin-Statewide-Stock',
    })
    return render(request, 'admin/statewide_stock_monitor.html', context)

def admin_statewide_analytics_views(request):
    # Get filter parameters from GET request (Dropdown selections)
    selected_district_id = request.GET.get('district')
    selected_taluk_id = request.GET.get('taluk')
    selected_village_id = request.GET.get('village')
    selected_shop_id = request.GET.get('shop')

    # Base Querysets
    shops = shop_details.objects.filter(is_active=True)
    
    # Apply filters dynamically based on admin selection
    if selected_shop_id:
        shops = shops.filter(shop_id=selected_shop_id)
    elif selected_village_id:
        shops = shops.filter(village_town_id=selected_village_id)
    elif selected_taluk_id:
        shops = shops.filter(village_town__taluk_id=selected_taluk_id)
    elif selected_district_id:
        shops = shops.filter(village_town__taluk__district_id=selected_district_id)

    # Calculate Summary Statistics for the filtered scope
    total_shops = shops.count()
    
    # Consumers under filtered shops
    consumers = consumer_details.objects.filter(home_shop__in=shops).select_related('card_type').prefetch_related('family_members')
    total_cards = consumers.count()
    
    total_members = 0
    total_adults = 0
    total_children = 0
    card_type_breakdown = {}

    for c in consumers:
        c_type = c.card_type.card_type if c.card_type else "Unknown"
        if c_type not in card_type_breakdown:
            card_type_breakdown[c_type] = {'cards': 0, 'members': 0}
        card_type_breakdown[c_type]['cards'] += 1

        members = c.family_members.all()
        m_count = members.count()
        total_members += m_count
        card_type_breakdown[c_type]['members'] += m_count

        adults = sum(1 for m in members if getattr(m, 'is_adult', False) or str(getattr(m, 'status', '')).strip().capitalize() == 'Adult')
        total_adults += adults
        total_children += (m_count - adults)

    # Commodity Stock & Requirement Summary for the filtered shops
    stock_summary = shop_commodity_details.objects.filter(shop__in=shops).values(
        'commodity__id',
        'commodity__commodity',
        'commodity__unit',
        'commodity__is_non_pds'
    ).annotate(
        total_required=Sum('required_stock'),
        total_available=Sum('stock_quantity')
    ).order_by('commodity__commodity')

    # Dropdown Options for Hierarchy Filtering
    districts = district_details.objects.filter(is_active=True)
    taluks = taluk_details.objects.filter(is_active=True)
    villages = village_town_details.objects.filter(is_active=True)
    all_shops = shop_details.objects.filter(is_active=True)

    if selected_district_id:
        taluks = taluks.filter(district_id=selected_district_id)
    if selected_taluk_id:
        villages = villages.filter(taluk_id=selected_taluk_id)
    if selected_village_id:
        all_shops = all_shops.filter(village_town_id=selected_village_id)

    context = get_portal_context('admin', {
        'total_shops': total_shops,
        'total_cards': total_cards,
        'total_members': total_members,
        'total_adults': total_adults,
        'total_children': total_children,
        'card_type_breakdown': card_type_breakdown,
        'stock_summary': stock_summary,
        
        # Dropdowns
        'districts': districts,
        'taluks': taluks,
        'villages': villages,
        'all_shops': all_shops,
        
        # Current selections for template retention
        'selected_district': selected_district_id,
        'selected_taluk': selected_taluk_id,
        'selected_village': selected_village_id,
        'selected_shop': selected_shop_id,

        'title':'Admin-Statewide-Analysis',
    })
    return render(request, 'admin/statewide_analytics.html', context)

@transaction.atomic
def admin_dispatch_approval_page_views(request):
   
    admin_id = request.session.get('logged_admin_id')
    if not admin_id:
        messages.error(request, 'Please login first!')
        return redirect('admin_login')

    admin_obj = admin_details.objects.filter(admin_id=admin_id).first()

    # State-wise consolidated PDS stocks
    pds_stocks = shop_commodity_details.objects.filter(
        commodity__is_non_pds=False,
        commodity__is_deleted=False
    ).values(
        'commodity__id',
        'commodity__commodity', 
        'commodity__unit'
    ).annotate(
        total_required_stock=Sum('required_stock'),
        total_state_stock=Sum('stock_quantity')
    ).order_by('commodity__commodity')

    if request.method == 'POST':
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        active_shops = shop_details.objects.filter(is_active=True)
        total_shops_updated = 0

        for comm in pds_stocks:
            comm_id = comm['commodity__id']
            custom_buffer = request.POST.get(f'buffer_{comm_id}', '5.00')
            buffer_val = Decimal(custom_buffer if custom_buffer else '5.00')

            for shop in active_shops:
                shop_comm = shop_commodity_details.objects.filter(shop=shop, commodity_id=comm_id).first()
                if shop_comm:
                    req_val = shop_comm.required_stock or Decimal('0.00')
                    phys_val = shop_comm.stock_quantity or Decimal('0.00')
                    
                    #  Net Requirement = Required - Physical (If negative, clamp to 0.00)
                    net_val = req_val - phys_val
                    if net_val < 0:
                        net_val = Decimal('0.00')

                    #  Dispatch Qty = Net + (Net * Buffer %) [If net is 0, dispatch is 0]
                    if net_val > 0:
                        shop_dispatch_qty = net_val + (net_val * (buffer_val / Decimal('100.00')))
                    else:
                        shop_dispatch_qty = Decimal('0.00')

                    # 1. Upsert dispatch record
                    shop_stock_dispatch_details.objects.update_or_create(
                        shop=shop,
                        commodity_id=comm_id,
                        month=current_month,
                        year=current_year,
                        defaults={
                            'required_stock': req_val,
                            'current_physical_stock': phys_val,
                            'net_requirement': net_val,
                            'buffer_percentage': buffer_val,
                            'dispatch_qty': shop_dispatch_qty,
                            'status': 'APPROVED',
                            'approved_by_admin': admin_obj,
                            'approved_at': timezone.now()
                        }
                    )

                    # 2. Add to physical inventory only if dispatch qty > 0
                    if shop_dispatch_qty > 0:
                        shop_comm.stock_quantity += shop_dispatch_qty
                        shop_comm.save()

                    # 3. Audit trail log
                    stock_dispatch_audit_trail.objects.create(
                        shop=shop,
                        commodity_id=comm_id,
                        action_type="ADMIN_SHOP_DISPATCH_APPROVED_AND_STOCKED",
                        details=f"Admin {admin_id} approved dispatch for Shop {shop.shop_id}. Req: {req_val}, Phys: {phys_val}, Buffer: {buffer_val}%, Dispatch Qty: {shop_dispatch_qty}",
                        performed_by=str(admin_id)
                    )
            total_shops_updated += 1

        messages.success(request, f"Statewide PDS dispatches successfully processed & allocated to all {active_shops.count()} shops!")
        return redirect('admin_dispatch_approval_page')

    context = get_portal_context('admin', {
                    'pds_stocks': pds_stocks,
                    'title':'Admin-Dispatch',
    })
    return render(request, 'admin/dispatch_approval.html', context)

@transaction.atomic
def calculate_and_create_shop_dispatch(shop, officer_obj=None): # future update Noted ****
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    shop_commodities = shop_commodity_details.objects.filter(shop=shop, commodity__is_non_pds=False)
    
    for item in shop_commodities:
        req_stock = float(item.required_stock or 0.00)
        phys_stock = float(item.stock_quantity or 0.00)
        
        #  Fixed Net Requirement Formula (Minus sign added)
        net_req = req_stock - phys_stock
        if net_req < 0:
            net_req = 0.00 # if  Surplus net requirement 0
            
        # Default 5% Buffer Stock Margin
        buffer_pct = 5.00
        # Fixed Multiplication formula for buffer
        dispatch_qty = net_req + (net_req * (buffer_pct / 100.0))
        
        # Upsert dispatch record
        dispatch_obj, created = shop_stock_dispatch_details.objects.update_or_create(
            shop=shop,
            commodity=item.commodity,
            month=current_month,
            year=current_year,
            defaults={
                'required_stock': Decimal(str(round(req_stock, 3))),
                'current_physical_stock': Decimal(str(round(phys_stock, 3))),
                'net_requirement': Decimal(str(round(net_req, 3))),
                'buffer_percentage': Decimal(str(buffer_pct)),
                'dispatch_qty': Decimal(str(round(dispatch_qty, 3))),
                'status': 'PENDING'
            }
        )



def get_portal_context(user_type, extra_context=None):
    portals = {
        'consumer': {
            'nav_links': [
                {'name': 'Home', 'url': 'consumer_home_page', 'icon': 'fa-house', 'color': 'text-primary'},
                {'name': 'Profile', 'url': 'consumer_profile', 'icon': 'fa-user', 'color': 'text-success'},
                {'name': 'Shop / Purchase', 'url': 'consumer_product_details', 'icon': 'fa-store', 'color': 'text-warning'},
                {'name': 'History & Quota', 'url': 'consumer_purchase_history', 'icon': 'fa-clock-rotate-left', 'color': 'text-info'},
            ],
            'logout_url': 'consumer_logout',
            'portal_title': 'TNPDS நுகர்வோர் தளம்',
            'portal_subtitle': 'Consumer Portal',
        },
        'shop': {
            'nav_links': [
                {'name': 'Home', 'url': 'shop_home_page', 'icon': 'fa-house', 'color': 'text-primary'},
                {'name': 'Profile', 'url': 'shop_profile', 'icon': 'fa-user', 'color': 'text-success'},
                {'name': 'Inventory', 'url': 'shop_product_details', 'icon': 'fa-boxes-stacked', 'color': 'text-warning'},
                {'name': 'Add Items', 'url': 'shop_add_commodity', 'icon': 'fa-plus-circle', 'color': 'text-info'},
                {'name': 'Verify Order', 'url': 'shop_order_search', 'icon': 'fa-magnifying-glass', 'color': 'text-danger'},
                {'name': 'Stock Dashboard', 'url': 'shop_stock_dashboard', 'icon': 'fa-chart-pie', 'color': 'text-danger'},
            ],
            'logout_url': 'shop_worker_logout',
            'portal_title': 'நியாயவிலைக் கடை பணியாளர் தளம்',
            'portal_subtitle': 'TNPDS - Shop Portal',
        },

        'officer': {
            'nav_links': [
                {'name': 'Home', 'url': 'officer_home_page', 'icon': 'fa-house', 'color': 'text-primary'},
                {'name': 'Profile', 'url': 'officer_profile', 'icon': 'fa-user', 'color': 'text-success'},
                {'name': 'Pending Requests', 'url': 'officer_pending_request', 'icon': 'fa-clock', 'color': 'text-warning'},
                {'name': 'Audit History', 'url': 'officer_audit_history', 'icon': 'fa-book-history', 'color': 'text-info'},
                
            ],
            'logout_url': 'officer_logout',
            'portal_title': 'அதிகாரி தளம்',
            'portal_subtitle': 'Officer Portal',
        },

        'admin': {
            'nav_links': [
                {'name': 'Home', 'url': 'admin_home_page', 'icon': 'fa-house', 'color': 'text-primary'},
                {'name': 'Profile', 'url': 'admin_profile', 'icon': 'fa-user', 'color': 'text-success'},
                {'name': 'Card Types', 'url': 'admin_add_card_type', 'icon': 'fa-id-card', 'color': 'text-warning'},
                {'name': 'Commodities', 'url': 'admin_add_commodity', 'icon': 'fa-boxes-stacked', 'color': 'text-info'},
                {'name': 'Adult/ Child Allocation', 'url': 'admin_global_allocation_rates', 'icon': 'fa-sliders', 'color': 'text-danger'},
                {'name': 'Statewide Stock', 'url': 'admin_statewide_stock_monitor', 'icon': 'fa-earth-asia', 'color': 'text-success'},
                {'name': 'Dispatch Approval', 'url': 'admin_dispatch_approval_page', 'icon': 'fa-truck-fast', 'color': 'text-warning'},
            ],
            'logout_url': 'admin_logout',
            'portal_title': 'நிர்வாக அதிகாரி தளம்',
            'portal_subtitle': 'TNPDS Admin Portal',
        },

       'home': {
        'nav_links': [
            {'name': 'Home', 'url': 'home', 'icon': 'fa-house', 'color': 'text-primary'},
            {'name': 'Consumer', 'url': 'consumer_login', 'icon': 'fa-user', 'color': 'text-success'},
            {'name': 'Shop', 'url': 'shop_worker_login', 'icon': 'fa-store', 'color': 'text-warning'},
            {'name': 'Officer', 'url': 'officer_login', 'icon': 'fa-building-columns', 'color': 'text-info'},
            {'name': 'Admin', 'url': 'admin_login', 'icon': 'fa-shield-halved', 'color': 'text-dark'},
        ],
        'logout_url': None, # Public home page-ku logout thevai illai
        'portal_title': 'உணவுப் பொருள் வழங்கல் மற்றும் நுகர்வோர் பாதுகாப்புத் துறை',
        'portal_subtitle': 'DEPARTMENT OF CIVIL SUPPLIES AND CONSUMER PROTECTION',
    }      



          
    }
    
    context = portals.get(user_type, {})
    if extra_context:
        context.update(extra_context)
    return context



def ajax_get_states(request):
    country_id = request.GET.get('country_id')
    states = list(state_details.objects.filter(country_id=country_id, is_active=True).values('id', 'name'))
    return JsonResponse(states, safe=False)

def ajax_get_districts(request):
    state_id = request.GET.get('state_id')
    districts = list(district_details.objects.filter(state_id=state_id, is_active=True).values('id', 'name'))
    return JsonResponse(districts, safe=False)

def ajax_get_taluks(request):
    district_id = request.GET.get('district_id')
    taluks = list(taluk_details.objects.filter(district_id=district_id, is_active=True).values('id', 'name'))
    return JsonResponse(taluks, safe=False)

def ajax_get_villages(request):
    taluk_id = request.GET.get('taluk_id')
    villages = list(village_town_details.objects.filter(taluk_id=taluk_id, is_active=True).values('id', 'name'))
    return JsonResponse(villages, safe=False)

def ajax_get_shops(request):
    village_id = request.GET.get('village_id')
    # Shop-kku id-ku pathila shop_id irukkum nu parthukko
    shops = list(shop_details.objects.filter(village_town_id=village_id, is_active=True).values('shop_id', 'name'))
    return JsonResponse(shops, safe=False)