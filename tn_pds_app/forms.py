from django import forms
from .models import commodity_details


class consumer_signup(forms.Form):

    card_type=forms.CharField(
        label='Smart Card Type',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Smart Card Type'
            }
        )
    ) 
    card_number=forms.CharField(
        label='Smart Card number',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Smart Card Number'
            }
        )
    )    
    mobile_number=forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Mobile Number'
            }
        )
    )
    password=forms.CharField(
            label='Password',
            widget=forms.PasswordInput(
                attrs={
                    'placeholder':'Enter Your password'
                }
            )
        ) 
    confirm_password=forms.CharField(
                label='Confirm Password',
                widget=forms.PasswordInput(
                    attrs={
                        'placeholder':'Re-enter Your password'
                    }
                )
            )  

class consumer_login(forms.Form):
    mobile_number=forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Mobile Number'
            }
        )
    )

    password=forms.CharField(
                label='Password',
                widget=forms.PasswordInput(
                    attrs={
                        'placeholder':'Enter Your password'
                    }
                )
            ) 
    
class shop_worker_signup(forms.Form):

    shop_id=forms.CharField(
        label='Shop Number ( Id )',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Shop Number'
            }
        )
    ) 
    shop_worker_id=forms.CharField(
        label='shop worker Id',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Id'
            }
        )
    )    
    mobile_number=forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Mobile Number'
            }
        )
    )

    password=forms.CharField(
                label='Password',
                widget=forms.PasswordInput(
                    attrs={
                        'placeholder':'Enter Your password'
                    }
                )
            ) 
    confirm_password=forms.CharField(
                    label='Confirm Password',
                    widget=forms.PasswordInput(
                        attrs={
                            'placeholder':'Re-enter Your password'
                        }
                    )
                )  
    
class shop_worker_login(forms.Form):
    # shop_id=forms.CharField(
    #         label='Shop Number ( Id )',
    #         widget=forms.TextInput(
    #             attrs={
    #                 'placeholder':'Enter Shop Number'
    #             }
    #         )
    #     ) 
    shop_worker_id=forms.CharField(
        label='Shop Worker id',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Id'
            }
        )
    )

    password=forms.CharField(
            label='Password',
            widget=forms.PasswordInput(
                attrs={
                    'placeholder':'Enter Your password'
                }
            )
        )    
  
class officer_signup(forms.Form):

    officer_id=forms.CharField(
        label='Officer Id',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Officer Id'
            }
        )
    )  
    mobile_number=forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Mobile Number'
            }
        )
    )
    password=forms.CharField(
            label='Password',
            widget=forms.PasswordInput(
                attrs={
                    'placeholder':'Enter Your password'
                }
            )
        ) 
    confirm_password=forms.CharField(
                label='Confirm Password',
                widget=forms.PasswordInput(
                    attrs={
                        'placeholder':'Re-enter Your password'
                    }
                )
            )  

class officer_login(forms.Form):
    officer_id=forms.CharField(
        label='Officer Id',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Officer Id'
            }
        )
    )

    password=forms.CharField(
                label='Password',
                widget=forms.PasswordInput(
                    attrs={
                        'placeholder':'Enter Your password'
                    }
                )
            ) 

class admin_signup(forms.Form):

    admin_id=forms.CharField(
        label='Admin Id',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Admin Id'
            }
        )
    )  
    mobile_number=forms.CharField(
        label='Mobile Number',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Mobile Number'
            }
        )
    )
    password=forms.CharField(
            label='Password',
            widget=forms.PasswordInput(
                attrs={
                    'placeholder':'Enter Your password'
                }
            )
        ) 
    confirm_password=forms.CharField(
                label='Confirm Password',
                widget=forms.PasswordInput(
                    attrs={
                        'placeholder':'Re-enter Your password'
                    }
                )
            )  

class admin_login(forms.Form):
    admin_id=forms.CharField(
        label='Admin Id',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Your Admin Id'
            }
        )
    )

    password=forms.CharField(
                label='Password',
                widget=forms.PasswordInput(
                    attrs={
                        'placeholder':'Enter Your password'
                    }
                )
            )  

class admin_add_card_type(forms.Form):
    card_type=forms.CharField(
        label='Card Type',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Card type'
            }
        )
)  

class admin_add_commodity(forms.Form):
    commodity=forms.CharField(
        label='Commodity',
        widget=forms.TextInput(
            attrs={
                'placeholder':'Enter Commodity'
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
                'step':'0.01'
            }
        )
    )    

class admin_commodity_allocation(forms.Form):
    commodity=forms.ModelMultipleChoiceField(
        label='Allocate Commodity',
        queryset=commodity_details.objects.all(),
        widget=forms.CheckboxSelectMultiple,

    ) 

    quantity=forms.DecimalField(
            label='Quantity',
            max_digits=10,
            decimal_places=2,
            widget=forms.NumberInput(
                attrs={
                    'placeholder':'Enter Quantity Kg/Litre',
                    'step':'0.01',

                }
            ),
    
        )  

    # max_cap=forms.DecimalField(
    #         label='Max Cap',
    #         max_digits=10,
    #         decimal_places=2,
    #         widget=forms.NumberInput(
    #             attrs={
    #                 'placeholder':'Enter max Quantity Kg/Litre',
    #                 'step':'0.01',

    #             }
    #         ),
    
    #     )        

           

 


  