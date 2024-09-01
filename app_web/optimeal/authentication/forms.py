from django import forms

# Définition du formulaire
class SignUpEmployeeForm(forms.Form):
    employee_username = forms.CharField(max_length=150, label='Username')
    employee_password = forms.CharField(widget=forms.PasswordInput, label='Password')
    employee_email = forms.EmailField(label='Email')
    employee_first_name = forms.CharField(max_length=100, label='First Name')
    employee_last_name = forms.CharField(max_length=100, label='Last Name')
    employee_zip_code_prefix = forms.CharField(max_length=10, label='Zip Code Prefix')
    employee_city = forms.CharField(max_length=100, label='City')
    employee_state = forms.CharField(max_length=100, label='State')

class UpdateEmployeeForm(forms.Form):
    employee_username = forms.CharField(max_length=150, label='Username')
    employee_password = forms.CharField(widget=forms.PasswordInput, label='Password')
    employee_email = forms.EmailField(label='Email')
    employee_first_name = forms.CharField(max_length=100, label='First Name')
    employee_last_name = forms.CharField(max_length=100, label='Last Name')
    employee_zip_code_prefix = forms.CharField(max_length=10, label='Zip Code Prefix')
    employee_city = forms.CharField(max_length=100, label='City')
    employee_state = forms.CharField(max_length=100, label='State')

class LoginEmployeeForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label='Nom d\'utilisateur')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Mot de passe')