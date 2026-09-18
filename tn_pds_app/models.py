from statistics import mode

from django.db import models

# Create your models here.

class consumer_details(models.Model):
    card_type=models.CharField(max_length=50)
    card_number=models.CharField(max_length=30,primary_key=True)
    mobile_number=models.CharField(max_length=15)
    password=models.CharField(max_length=100)

    class Meta:
        db_table='consumer_details'

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

class shop_details(models.Model):
    shop_id=models.CharField(max_length=100,primary_key=True)
    # shop_worker_id=models.CharField(max_length=30)
    name=models.CharField(max_length=240)
    address=models.CharField(max_length=240)
    total_card_holders=models.IntegerField()

    class Meta:
        db_table='shop_details'

class shop_worker_details(models.Model):
    shop_id=models.CharField(max_length=100)
    shop_worker_id=models.CharField(max_length=30,primary_key=True)
    name=models.CharField(max_length=100)
    mobile_number=models.CharField(max_length=15,unique=True)
    address=models.CharField(max_length=240)
    gender=models.CharField(max_length=10)
    password=models.CharField(max_length=100)

    class Meta:
        db_table='shop_worker_details'

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

class card_type_details(models.Model):
    card_type=models.CharField(max_length=50)

    class Meta:
            db_table='card_type_details'

class commodity_details(models.Model):
    units=[('kg','Kg'),('litre','litre')]
    commodity=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10,decimal_places=2,default=00.00)
    unit = models.CharField(max_length=10, choices=units, default='kg')
    class Meta:
            db_table='commodity_details' 

    def __str__(self):
         return self.commodity 


class commodity_allocation_details(models.Model):
    card_type=models.ForeignKey(card_type_details,on_delete=models.CASCADE)
    commodity=models.ForeignKey(commodity_details,on_delete=models.CASCADE)
    quantity=models.DecimalField(max_digits=10,decimal_places=2,default=00.00)
    # max_cap=models.DecimalField(max_digits=10,decimal_places=2,default=00.00)
    unit = models.CharField(max_length=10, choices=commodity_details.units, default='Kg')

    class Meta:
            db_table='commodity_allocation_details' 

    def __str__(self):
         return f'{self.card_type.card_type}-{self.commodity.commodity}'          

                       



