from django import forms
import re
from django.core.exceptions import ValidationError


from .models import (
    card_type_details, 
    country_details, 
    state_details, 
    district_details, 
    taluk_details, 
    village_town_details, 
    shop_details,
    commodity_details,
    family_members_details,
    commodity_allocation_details,
    consumer_crud_details

)

#  Common Validation  Class :
class common_form_validation:
    
    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if mobile is not None:
            if mobile and str(mobile).strip():
                if not re.match(r'^[6-9]\d{9}$', str(mobile).strip()):
                    raise ValidationError("Enter a valid 10-digit Indian mobile number starting with 6-9.")
        return mobile

    def clean_card_number(self):
        card = self.cleaned_data.get('card_number')
        if card is not None:
            if not card or len(str(card).strip()) < 5:
                raise ValidationError("Please enter a valid Smart Card number.")
        return card

    def clean_card_type(self):
        card_type = self.cleaned_data.get('card_type')
        if card_type is not None:
            if not card_type:
                raise ValidationError("Please select a valid Smart Card Type.")
            if not card_type_details.objects.filter(id=card_type.id).exists():
                raise ValidationError("Selected card type is invalid or does not exist in the system.")
        return card_type

    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number')
        if aadhaar is not None:
            if not aadhaar or not re.match(r'^\d{12}$', str(aadhaar).strip()):
                raise ValidationError("Aadhaar number must be exactly 12 digits.")
        return aadhaar

    def clean_email_id(self):
        email = self.cleaned_data.get('email_id')
        if email is not None:
            if email and str(email).strip():
                email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                if not re.match(email_pattern, str(email).strip()):
                    raise ValidationError("Please enter a valid email address.")
        return email

    def clean_commodity(self):
        name = self.cleaned_data.get('commodity')
        if name is not None:
            if not name or len(str(name).strip()) < 2:
                raise ValidationError("Please enter a valid commodity name.")
        return name

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None:
            if price < 0:
                raise ValidationError("Price cannot be negative.")
        return price

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password is not None and confirm_password is not None:
            if password != confirm_password:
                raise ValidationError({
                    'confirm_password': "Passwords do not match. Please re-enter."
                })
        return cleaned_data

class LocationHierarchyMixin(forms.Form):
    # --- Hierarchical Location Fields ---
    country = forms.ModelChoiceField(
        queryset=country_details.objects.filter(is_active=True),
        label='Country',
        empty_label='--- Select Country ---',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm py-2', 'id': 'id_country', 'required': 'true'})
    )
    state = forms.ModelChoiceField(
        queryset=state_details.objects.none(),
        label='State',
        empty_label='--- Select State ---',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm py-2', 'id': 'id_state', 'required': 'true'})
    )
    district = forms.ModelChoiceField(
        queryset=district_details.objects.none(),
        label='District',
        empty_label='--- Select District ---',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm py-2', 'id': 'id_district', 'required': 'true'})
    )
    taluk = forms.ModelChoiceField(
        queryset=taluk_details.objects.none(),
        label='Taluk',
        empty_label='--- Select Taluk ---',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm py-2', 'id': 'id_taluk', 'required': 'true'})
    )
    village_town = forms.ModelChoiceField(
        queryset=village_town_details.objects.none(),
        label='Village / Town',
        empty_label='--- Select Village / Town ---',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm py-2', 'id': 'id_village', 'required': 'true'})
    )
    
    shop_id = forms.ModelChoiceField(
        queryset=shop_details.objects.none(),
        label='Select Fair Price Shop',
        empty_label='--- Select Your Fair Price Shop ---',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm py-2', 'id': 'id_shop', 'required': 'true'})
    )

    def load_location_querysets(self):
        self.fields['country'].queryset = country_details.objects.filter(is_active=True)

        if self.data and 'country' in self.data:
            try:
                country_val = self.data.get('country')
                if country_val:
                    country_id = int(country_val)
                    self.fields['state'].queryset = state_details.objects.filter(country_id=country_id, is_active=True)
            except (ValueError, TypeError):
                pass

        if self.data and 'state' in self.data:
            try:
                state_val = self.data.get('state')
                if state_val:
                    state_id = int(state_val)
                    self.fields['district'].queryset = district_details.objects.filter(state_id=state_id, is_active=True)
            except (ValueError, TypeError):
                pass

        if self.data and 'district' in self.data:
            try:
                district_val = self.data.get('district')
                if district_val:
                    district_id = int(district_val)
                    self.fields['taluk'].queryset = taluk_details.objects.filter(district_id=district_id, is_active=True)
            except (ValueError, TypeError):
                pass

        if self.data and 'taluk' in self.data:
            try:
                taluk_val = self.data.get('taluk')
                if taluk_val:
                    taluk_id = int(taluk_val)
                    self.fields['village_town'].queryset = village_town_details.objects.filter(taluk_id=taluk_id, is_active=True)
            except (ValueError, TypeError):
                pass

        if self.data and 'village_town' in self.data:
            try:
                village_val = self.data.get('village_town')
                if village_val:
                    village_id = int(village_val)
                    if 'shop_id' in self.fields:
                        self.fields['shop_id'].queryset = shop_details.objects.filter(village_town_id=village_id, is_active=True)
                    elif 'home_shop' in self.fields:
                        self.fields['home_shop'].queryset = shop_details.objects.filter(village_town_id=village_id, is_active=True)
            except (ValueError, TypeError):
                pass

    

class consumer_signup(common_form_validation, LocationHierarchyMixin,forms.Form):

    card_type = forms.ModelChoiceField(
        queryset=card_type_details.objects.all(),
        label='Smart Card Type',
        empty_label='--- Select Your Smart Card Type ---',
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-sm py-2',
                'required': 'true'
            }
        )
    ) 
    card_number = forms.CharField(
        label='Smart Card number',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your Smart Card Number', 
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'minlength': '10',
                'maxlength': '15',
                'title': 'Enter valid 10 to 15 digit smart card number',
            }
        )
    )       
    mobile_number = forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your 10-digit Mobile Number', 
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'pattern': '[6-9][0-9]{9}',
                'maxlength': '10',
                'title': 'Enter valid 10-digit mobile number starting with 6-9',
            }
        )
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter Your password', 
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'minlength': '6',
                'title': 'Enter atleast 6-digit password',
            }
        )
    ) 
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Re-enter Your password', 
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'password and confirm password are not match',
            }
        )
    )


    def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.load_location_querysets()
        
                if 'village_town' in self.data:
                    try:
                        village_id = int(self.data.get('village_town'))
                        self.fields['shop_id'].queryset = shop_details.objects.filter(village_town_id=village_id, is_active=True)
                    except (ValueError, TypeError):
                        pass

       

class consumer_login(common_form_validation,forms.Form):

    mobile_number = forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your 10-digit Mobile Number',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'pattern': '[6-9][0-9]{9}',
                'maxlength': '10',
                'title': 'Enter valid 10-digit mobile number starting with 6-9'
            }
        )
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter Your password',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'minlength': '6',
                'title': 'Enter atleast 6-digit password'
            }
        )
    )

class FamilyMemberForm(common_form_validation,forms.ModelForm):

    name = forms.CharField(
        label='Member Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Member Name', 
            'class': 'form-control form-control-sm py-2', 
            'required': 'true',
            'pattern': '^[A-Za-z\\s]+$', 
            'title': 'Name should contain only letters and spaces'
        })
    )
    dob = forms.DateField(
        label='Date of Birth',
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control form-control-sm py-2', 
            'required': 'true'
        })
    )
    gender = forms.ChoiceField(
        label='Gender',
        choices=[('', '--- Select Gender ---'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm py-2', 
            'required': 'true'
        })
    )
    relation = forms.CharField(
        label='Relation',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Head, Wife, Son, Daughter', 
            'class': 'form-control form-control-sm py-2', 
            'required': 'true',
            'pattern': '^[A-Za-z\\s]+$', 
            'title': 'Relation should contain only letters and spaces'
        })
    )
    mobile_number = forms.CharField(
        required=False,
        label='Mobile Number',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Mobile Number (Optional)', 
            'class': 'form-control form-control-sm py-2', 
            'pattern': '[6-9][0-9]{9}', 
            'maxlength': '10', 
            'title': 'Enter valid 10-digit mobile number starting with 6-9'
        })
    )
    aadhaar_number = forms.CharField(
        label='Aadhaar Number',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 12-digit Aadhaar Number', 
            'class': 'form-control form-control-sm py-2', 
            'required': 'true', 
            'pattern': r'\d{12}', 
            'maxlength': '12', 
            'minlength': '12', 
            'title': 'Enter exact 12-digit Aadhaar Number'
        })
    )

    email_id = forms.CharField(
        required=False,
        label='Email ID (Recomended)',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your Email Address',
                'class': 'form-control form-control-sm py-2',
                'type': 'email',
                'pattern': '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$', 
                'title': 'Enter a valid email address'
            }
        )
    )

    class Meta:
        model = family_members_details
        fields = ['name', 'dob', 'gender', 'relation', 'mobile_number', 'aadhaar_number','email_id']

 
class shop_worker_signup(common_form_validation, LocationHierarchyMixin, forms.Form):

    shop_worker_id = forms.CharField(
        label='Shop Worker Id',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your Worker Id',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'Enter valid worker ID'
            }
        )
    )    
    mobile_number = forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your 10-digit Mobile Number',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'pattern': '[6-9][0-9]{9}',
                'maxlength': '10',
                'title': 'Enter valid 10-digit mobile number starting with 6-9'
            }
        )
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter Your password',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'minlength': '6',
                'title': 'Enter atleast 6-digit password'
            }
        )
    ) 
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Re-enter Your password',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'Passwords must match'
            }
        )
    )  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_location_querysets()

        if 'village_town' in self.data:
            try:
                village_id = int(self.data.get('village_town'))
                self.fields['shop_id'].queryset = shop_details.objects.filter(village_town_id=village_id, is_active=True)
            except (ValueError, TypeError):
                pass


class shop_worker_login(common_form_validation, forms.Form):
    shop_worker_id = forms.CharField(
        label='Shop Worker Id',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your Worker Id',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'Enter valid worker ID'
            }
        )
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter Your password',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'minlength': '6',
                'title': 'Enter atleast 6-digit password'
            }
        )
    )   
  
class officer_signup(common_form_validation, forms.Form):

    officer_id = forms.CharField(
        label='Officer Id',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your Officer Id',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'Enter valid officer ID'
            }
        )
    )  
    mobile_number = forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your 10-digit Mobile Number',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'pattern': '[6-9][0-9]{9}',
                'maxlength': '10',
                'title': 'Enter valid 10-digit mobile number starting with 6-9'
            }
        )
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter Your password',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'minlength': '6',
                'title': 'Enter atleast 6-digit password'
            }
        )
    ) 
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Re-enter Your password',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'Passwords must match'
            }
        )
    ) 

class officer_login(common_form_validation, forms.Form):
    officer_id = forms.CharField(
        label='Officer Id',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your Officer Id',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'Enter valid officer ID'
            }
        )
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter Your password',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'minlength': '6',
                'title': 'Enter atleast 6-digit password'
            }
        )
    )

class admin_signup(common_form_validation, forms.Form):
    admin_id = forms.CharField(
        label='Admin Id',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your Admin Id',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'Enter valid admin ID'
            }
        )
    )  
    mobile_number = forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your 10-digit Mobile Number',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'pattern': '[6-9][0-9]{9}',
                'maxlength': '10',
                'title': 'Enter valid 10-digit mobile number starting with 6-9'
            }
        )
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter Your password',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'minlength': '6',
                'title': 'Enter atleast 6-digit password'
            }
        )
    ) 
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Re-enter Your password',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'Passwords must match'
            }
        )
    ) 

class admin_login(common_form_validation, forms.Form):
    admin_id = forms.CharField(
        label='Admin Id',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Your Admin Id',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'Enter valid admin ID'
            }
        )
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter Your password',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'minlength': '6',
                'title': 'Enter atleast 6-digit password'
            }
        )
    )

class admin_add_card_type(forms.Form):
    card_type = forms.CharField(
        label='Card Type',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Card type',
                'class': 'form-control form-control-sm py-2',
                'required': 'true',
                'title': 'Enter card type'
            }
        )
    )

class admin_add_commodity(common_form_validation, forms.Form):
    commodity = forms.CharField(
        label='Commodity',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Enter Commodity',
                'class': 'form-control',
                'required': 'true',
                'title': 'Enter commodity name'
            }
        )
    )          
    price = forms.DecimalField(
        label='Price',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Enter Price',
                'step': '0.01',
                'class': 'form-control',
                'required': 'true',
                'title': 'Enter valid price'
            }
        )
    ) 
    unit = forms.ChoiceField(
        label='Unit',
        choices=[
            ('kg', 'Kg'),
            ('litre', 'Litre'),
            ('packet', 'Packet'),
            ('piece', 'Piece'),
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'required': 'true'
            }
        )
    )    
    commodity_image = forms.ImageField(
        label='Product Image',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control mb-3'})
    )


class admin_commodity_allocation(forms.ModelForm):
    class Meta:
        model = commodity_allocation_details
        fields = [
            'quantity', 
            'adult_quantity', 
            'child_quantity', 
            'max_cap', 
            'group_name', 
            'group_max_cap'
        ]

class shop_add_commodity(forms.Form):
    commodity=forms.CharField(
        label='Commodity',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Commodity',
                'class': 'form-control',
            }
        )
    )           

    price=forms.DecimalField(
        label='Price',
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'placeholder':'Enter Price',
                'step':'0.01',
                'class': 'form-control',

            }
        )
    ) 

    unit=forms.ChoiceField(
            label='Unit',
            choices=[
                    ('kg','Kg'),
                    ('litre','Litre'),
                    ('packet', 'Packet'),
                    ('piece', 'Piece'),
                    ],
            widget=forms.Select(
                attrs={
                    'class':'form-control'
                }
            )
        )    
    commodity_image = forms.ImageField(
        label='Product Image',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control mb-3'})
    )
           

class FamilyMemberEditRequestForm(common_form_validation, forms.ModelForm):
    name = forms.CharField(
        label='Member Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Member Name', 
            'class': 'form-control form-control-sm py-2', 
            'required': 'true',
            'pattern': '^[A-Za-z\\s]+$', 
            'title': 'Name should contain only letters and spaces'
        })
    )
    dob = forms.DateField(
        label='Date of Birth',
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control form-control-sm py-2', 
            'required': 'true'
        })
    )
    gender = forms.ChoiceField(
        label='Gender',
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm py-2', 
            'required': 'true'
        })
    )
    relation = forms.CharField(
        label='Relation',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Head, Wife, Son, Daughter', 
            'class': 'form-control form-control-sm py-2', 
            'required': 'true',
            'pattern': '^[A-Za-z\\s]+$', 
            'title': 'Relation should contain only letters and spaces'
        })
    )
    mobile_number = forms.CharField(
        required=False,
        label='Mobile Number',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Mobile Number (Optional)', 
            'class': 'form-control form-control-sm py-2', 
            'pattern': '[6-9][0-9]{9}', 
            'maxlength': '10', 
            'title': 'Enter valid 10-digit mobile number starting with 6-9'
        })
    )
    aadhaar_number = forms.CharField(
        label='Aadhaar Number',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 12-digit Aadhaar Number', 
            'class': 'form-control form-control-sm py-2', 
            'required': 'true', 
            'pattern': r'\d{12}', 
            'maxlength': '12', 
            'minlength': '12', 
            'title': 'Enter exact 12-digit Aadhaar number'
        })
    )
    email_id = forms.EmailField(
        label='Member Email ID (Optional)',
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter email id', 
            'class': 'form-control form-control-sm py-2'
        })
    )
    reason = forms.CharField(
        label='Reason for Modification',
        widget=forms.Textarea(attrs={
            'rows': 2, 
            'placeholder': 'Enter reason for edit', 
            'class': 'form-control form-control-sm',
            'required': 'true'
        })
    )
    document_copy = forms.FileField(
        label='Supporting Proof Document (Required only for Name/DOB/Gender changes)',
        required=False,  # Optional
        widget=forms.FileInput(attrs={
            'class': 'form-control form-control-sm mb-3'
        })
    )

    class Meta:
        model = consumer_crud_details
        fields = ['name', 'dob', 'gender', 'relation', 'mobile_number', 'aadhaar_number', 'email_id', 'reason', 'document_copy']

    # --- Edit Form Specific Validation ---
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name is not None and (not name or len(str(name).strip()) < 2):
            raise ValidationError("Please enter a valid member name.")
        return name

    
# future update :
# officer select location heirarchy 
# creat :
# shop ( only existing shop can login )
# shop worker ( only existing worker can login )
# officer ( only existing officer can login )
# admin ( only existing admin can login )   
# consumr :( only existing consumer can login ) 
# apply for a new card
# add request available in consumer profile 
# pending purchase available in consumer purchase history 
# anso on