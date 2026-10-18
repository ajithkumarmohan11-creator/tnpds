from statistics import mode

from django.db import models

# Create your models here.

class card_type_details(models.Model):
    card_type=models.CharField(max_length=50)
    is_pds_allocation = models.BooleanField(default=False)

    class Meta:
            db_table='card_type_details'

    def __str__(self):
        return self.card_type        

class consumer_details(models.Model):
    card_type= models.ForeignKey('card_type_details', on_delete=models.CASCADE)
    card_number=models.CharField(max_length=30,primary_key=True)
    mobile_number=models.CharField(max_length=15)
    password=models.CharField(max_length=100)
    home_shop = models.ForeignKey('shop_details', on_delete=models.SET_NULL, null=True, blank=True, related_name='registered_consumers')

    class Meta:
        db_table='consumer_details'

class consumer_allocation_details(models.Model):
    consumer = models.ForeignKey('consumer_details', on_delete=models.CASCADE, related_name='allocated_commodities')
    commodity = models.ForeignKey('commodity_details', on_delete=models.CASCADE)
    entitlement = models.FloatField(default=0.00)
    group_name = models.CharField(max_length=100, null=True, blank=True)
    card_max_qty = models.DecimalField(max_digits=10,default=0.00,decimal_places=2)
    min_qty = models.DecimalField(max_digits=10,default=0.00,decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='consumer_allocation_details'

    def __str__(self):
        return f"{self.consumer.mobile_number} - {self.commodity.commodity} ({self.entitlement})"

class family_members_details(models.Model):
    consumer = models.ForeignKey('consumer_details', on_delete=models.CASCADE, related_name='family_members')
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=20)
    relation = models.CharField(max_length=50)  # Head, Wife, Son, Daughter, etc.
    mobile_number = models.CharField(max_length=15, blank=True, null=True)  # Optional
    aadhaar_number = models.CharField(max_length=12, unique=True)  # Unique for verification
    is_adult = models.BooleanField(default=True)  # True = Adult, False = Child
    created_at = models.DateTimeField(auto_now_add=True)
    email_id = models.EmailField(max_length=100, blank=True, null=True)

    
    class Meta:
        db_table='family_members_details'

    def __str__(self):
        return f"{self.name} ({self.relation})"    

class consumer_crud_details(models.Model):
    REQUEST_TYPE_CHOICES = (
        ('ADD', 'Add Member'),
        ('EDIT', 'Edit Member'),
        ('DELETE', 'Delete Member'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    consumer = models.ForeignKey('consumer_details', on_delete=models.CASCADE, related_name='member_requests')
    member = models.ForeignKey('family_members_details', on_delete=models.SET_NULL, null=True, blank=True, related_name='edit_requests')
    
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    
    # Request data fields (for edit/add/delete tracking)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=20)
    relation = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    email_id = models.EmailField(max_length=100, blank=True, null=True) 
    aadhaar_number = models.CharField(max_length=12) 
    reason = models.TextField(blank=True, null=True) # Reason for deletion/modification
    document_copy = models.FileField(upload_to='request_docs/', blank=True, null=True) # Proof upload

    changed_fields = models.TextField(blank=True, null=True)
    
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey('officer_details', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    officer_remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'consumer_crud_details'

    def __str__(self):
        return f"Card: {self.consumer.card_number} | Type: {self.request_type} | Status: {self.status}"


class consumer_crud_history(models.Model):
    consumer = models.ForeignKey('consumer_details', on_delete=models.SET_NULL, null=True, blank=True)
    card_number = models.CharField(max_length=30)
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True) 
    action_type = models.CharField(max_length=50) # e.g., "MEMBER_APPROVED", "MOBILE_UPDATED"
    description = models.TextField()
    performed_by_officer = models.ForeignKey('officer_details', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consumer_crud_history'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Card: {self.card_number} | Action: {self.action_type} | Time: {self.timestamp}"    

class consumer_address_history(models.Model): # future update
    consumer = models.ForeignKey('consumer_details', on_delete=models.CASCADE)
    old_address = models.TextField(blank=True, null=True)
    new_address = models.TextField()
    reason = models.TextField(blank=True, null=True)
    proof_document = models.FileField(upload_to='address_proofs/', blank=True, null=True) # EB Bill/Gas Bill/Tax Receipt
    updated_by_officer = models.ForeignKey('officer_details', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consumer_address_history'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Card: {self.consumer.card_number} | Address Updated at {self.timestamp}"        

class card_details(models.Model):
    card_type= models.CharField(max_length=100)
    card_number=models.CharField(max_length=100,primary_key=True,unique=True)
    family_head_name=models.CharField(max_length=100)
    family_head_gender=models.CharField(max_length=100)
    family_head_dob=models.DateField()
    family_head_father_or_husband_name=models.CharField(max_length=100)
    family_native_address=models.CharField(max_length=240)
    family_home_shop_address=models.CharField(max_length=240)
    family_home_shop_number=models.CharField(max_length=15)
    total_family_members_count=models.IntegerField()
    # family_members_name=models.CharField(max_length=240)
    # family_members_gender=models.CharField(max_length=20)
    # family_members_dob=models.DateField()
    phone=models.CharField(max_length=12,unique=True)
    

    class Meta:
        db_table= 'card_details'


   
class shop_worker_details(models.Model):
    shop_id=models.ForeignKey('shop_details', on_delete=models.CASCADE, db_column='shop_id')
    shop_worker_id=models.CharField(max_length=30,primary_key=True)
    name=models.CharField(max_length=100)
    mobile_number=models.CharField(max_length=15,unique=True)
    address=models.CharField(max_length=240)
    gender=models.CharField(max_length=10)
    password=models.CharField(max_length=100)

    class Meta:
        db_table='shop_worker_details'

    def __str__(self):
        return f"{self.shop_worker_id} (Shop: {self.shop.shop_id})"

class shop_worker_login_details(models.Model):
    worker = models.ForeignKey('shop_worker_details', on_delete=models.CASCADE)
    shop = models.ForeignKey('shop_details', on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shop_worker_login_details'        

class officer_details(models.Model):
    officer_id=models.CharField(max_length=30,primary_key=True)
    name=models.CharField(max_length=100)
    mobile_number=models.CharField(max_length=15,unique=True)
    address=models.CharField(max_length=240)
    gender=models.CharField(max_length=10)
    password=models.CharField(max_length=100)

    class Meta:
        db_table='officer_details'

class admin_details(models.Model):
    admin_id=models.CharField(max_length=30,primary_key=True)
    name=models.CharField(max_length=100)
    mobile_number=models.CharField(max_length=15,unique=True)
    address=models.CharField(max_length=240)
    gender=models.CharField(max_length=10)
    password=models.CharField(max_length=100)

    class Meta:
        db_table='admin_details'        

class pds_commodities(models.Model):
    product_id=models.CharField(max_length=100,primary_key=True)
    name=models.CharField(max_length=240)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity=models.DecimalField(max_digits=10, decimal_places=3)
    sales_quantity=models.DecimalField(max_digits=10, decimal_places=3,default=0.000)
    available_quantity=models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        db_table='pds_commodities'

class non_pds_commodities(models.Model):
    product_id=models.CharField(max_length=100,primary_key=True)
    name=models.CharField(max_length=240)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity=models.DecimalField(max_digits=10, decimal_places=3)
    sales_quantity=models.DecimalField(max_digits=10, decimal_places=3,default=0.000)
    available_quantity=models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        db_table='non_pds_commodities'

class commodity_details(models.Model):
    commodity = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    unit = models.CharField(max_length=20)
    commodity_image = models.ImageField(upload_to='commodities/', null=True, blank=True)
    is_non_pds = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    min_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    group_name = models.CharField(max_length=100, blank=True, null=True)
    group_max_cap = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # commodity-wise adult & child multipliers 
    adult_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    child_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
            db_table='commodity_details' 

    def __str__(self):
        return f"{self.commodity} ({'Non-PDS' if self.is_non_pds else 'PDS'})"

class shop_commodity_details(models.Model):
    shop = models.ForeignKey('shop_details', on_delete=models.CASCADE)
    commodity = models.ForeignKey('commodity_details', on_delete=models.CASCADE)
    
    custom_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    required_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table='shop_commodity_details'
        unique_together = ('shop', 'commodity')

    def __str__(self):
        return f"{self.shop} - {self.commodity.commodity}"

class commodity_allocation_details(models.Model):
    card_type=models.ForeignKey('card_type_details',on_delete=models.CASCADE)
    commodity=models.ForeignKey('commodity_details',on_delete=models.CASCADE)
    quantity=models.DecimalField(max_digits=10,decimal_places=2,default=00.00)
    adult_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Per Adult quota
    child_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Per Child quota
    max_cap = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    group_name = models.CharField(max_length=50, blank=True, null=True)               
    group_max_cap = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
            db_table='commodity_allocation_details' 
            unique_together = ('card_type', 'commodity')

    def __str__(self):
         return f'{self.card_type.card_type}-{self.commodity.commodity}'  

class admin_global_allocation_rules(models.Model):
    adult = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Per adult quota rate
    child = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Per child quota rate

    class Meta:
        db_table = 'admin_global_allocation_rules'

    def __str__(self):
        return f'Adult: {self.adult}, Child: {self.child}'            
                    
class cart_item_details(models.Model):
    consumer = models.ForeignKey('consumer_details', on_delete=models.CASCADE)
    commodity = models.ForeignKey('commodity_details', on_delete=models.CASCADE)
    shop = models.ForeignKey('shop_details', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    add_time = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return self.quantity * self.commodity.price

    class Meta:
        db_table = 'cart_item_details' 
        unique_together = ('consumer', 'commodity', 'shop')

    def __str__(self):
        return f'{self.consumer.mobile_number} - {self.commodity.commodity} - Shop #{self.shop.shop_id} ({self.quantity})'

class order_details(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending at Counter'),
        ('DELIVERED', 'Delivered & Paid'),
        ('CANCELLED', 'Cancelled'),
    )

    token_number = models.CharField(max_length=50, unique=True)
    consumer = models.ForeignKey('consumer_details', on_delete=models.CASCADE)
    shop = models.ForeignKey('shop_details', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_details'

    def __str__(self):
        return f"{self.token_number} - {self.consumer.card_number} ({self.status})"

class order_item_details(models.Model):
    order = models.ForeignKey('order_details', on_delete=models.CASCADE, related_name='items')
    commodity = models.ForeignKey('commodity_details', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)

    class Meta:
        db_table = 'order_item_details'

    def __str__(self):
        return f"{self.order.token_number} - {self.commodity.commodity}"   

class portal_photo_details(models.Model):
    PORTAL_CHOICES = (
            ('consumer', 'Consumer Portal'),
            ('shop', 'Shop Portal'),
            ('admin', 'Admin Portal'),
            ('officer', 'Officer Portal'),
            ('home', 'Home Portal'),

        )
    portal_type = models.CharField(max_length=20, choices=PORTAL_CHOICES)
    photo = models.ImageField(upload_to='portal_photos/') 
    badge_text = models.CharField(max_length=100) 
    quote_text = models.TextField() 
    subtext = models.TextField(blank=True, null=True, help_text="Bottom subtext for the photo")
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
            db_table = 'portal_photo_details'
            ordering = ['display_order']

    def __str__(self):
            return f"{self.get_portal_type_display()} - {self.badge_text}" 

class consumer_monthly_allocation_status_details(models.Model): 
    consumer = models.ForeignKey('consumer_details', on_delete=models.CASCADE)
    commodity = models.ForeignKey('commodity_details', on_delete=models.CASCADE)
    month = models.IntegerField()  # e.g., 10 for October
    year = models.IntegerField()   # e.g., 2026
    allocated_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Total given quota (e.g., 10.00)
    purchased_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # How much bought so far (e.g., 5.00)
    remaining_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Leftover (e.g., 5.00)
    
    # Status flags
    is_fully_purchased = models.BooleanField(default=False) # True if purchased_qty == allocated_qty
    is_partially_purchased = models.BooleanField(default=False) # True if 0 < purchased_qty < allocated_qty
    
    last_purchased_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'consumer_monthly_allocation_status_details'
        unique_together = ('consumer', 'commodity', 'month', 'year')

    def __str__(self):
        status = "Completed" if self.is_fully_purchased else ("Partial" if self.is_partially_purchased else "Pending")
        return f"{self.consumer.card_number} - {self.commodity.commodity} ({self.month}/{self.year}) [{status}: {self.purchased_qty}/{self.allocated_qty}]"

class country_details(models.Model):
    name = models.CharField(max_length=100, default="India")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'country_details'
        ordering = ['name']

    def __str__(self):
        return self.name

class state_details(models.Model):
    country = models.ForeignKey('country_details', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'state_details'
        ordering = ['name']

    def __str__(self):
        return self.name

class district_details(models.Model):
    state = models.ForeignKey('state_details', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'district_details'
        ordering = ['name']

    def __str__(self,):
        return self.name

class taluk_details(models.Model):
    district = models.ForeignKey('district_details', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'taluk_details'
        ordering = ['name']

    def __str__(self):
        return self.name

class village_town_details(models.Model):
    taluk = models.ForeignKey('taluk_details', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'village_town_details'
        ordering = ['name']

    def __str__(self):
        return self.name

class shop_details(models.Model):
    shop_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    village_town = models.ForeignKey('village_town_details', on_delete=models.CASCADE,null=True, blank=True)
    address = models.TextField()
    is_active = models.BooleanField(default=True) # Soft delete flag
    total_card_holders=models.IntegerField()

    class Meta:
        db_table = 'shop_details'
        ordering = ['shop_id']

    def __str__(self):
        return f"{self.name}"

class district_stock_allocation_details(models.Model):
    district = models.ForeignKey(district_details, on_delete=models.CASCADE)
    commodity = models.ForeignKey(commodity_details, on_delete=models.CASCADE)
    allocated_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    month = models.IntegerField()
    year = models.IntegerField()
    allocated_by_admin = models.ForeignKey('admin_details', on_delete=models.SET_NULL, null=True)
    allocated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.district.name} - {self.commodity.commodity} ({self.allocated_qty})"

class shop_stock_dispatch_details(models.Model):
    shop = models.ForeignKey(shop_details, on_delete=models.CASCADE)
    commodity = models.ForeignKey(commodity_details, on_delete=models.CASCADE)
    required_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_physical_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_requirement = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    buffer_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # Default 0% Buffer
    dispatch_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=20, default='PENDING') # PENDING / APPROVED / DISPATCHED
    month = models.IntegerField()
    year = models.IntegerField()
    
    
    dispatched_by_officer = models.ForeignKey(officer_details, on_delete=models.SET_NULL, null=True, blank=True)
    approved_by_admin = models.ForeignKey(admin_details, on_delete=models.SET_NULL, null=True, blank=True)
    
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shop {self.shop_id} - {self.commodity.commodity} [Dispatch: {self.dispatch_qty}]"

class stock_dispatch_audit_trail(models.Model):
    shop = models.ForeignKey(shop_details, on_delete=models.CASCADE)
    commodity = models.ForeignKey(commodity_details, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50) # e.g., 'DISPATCH_APPROVED', 'STOCK_ALLOCATED'
    details = models.TextField()
    performed_by = models.CharField(max_length=100) # Admin ID or Officer ID
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audit [{self.action_type}] - Shop {self.shop.shop_id}"
