from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Horario
from datetime import time






class SignInForm(forms.Form):
    username = forms.CharField(max_length=150, label='Usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')

# forms.py



class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='Nombre', max_length=30, required=True)
    last_name = forms.CharField(label='Apellido', max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email




class ExcelForm(forms.Form):
    archivo_excel = forms.FileField(label='Seleccionar archivo Excel')

    from django import forms

class ExcelUploadForm(forms.Form):
    archivo_excel = forms.FileField(label='Seleccionar archivo Excel')


from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Subir archivo Excel')

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['hora_inicio', 'hora_fin']
   
   
class SolicitudDiasForm(forms.Form):
    opcion = forms.ChoiceField(
        choices=[('3', 'Seleccionar 3 días'), ('todos', 'Seleccionar todos los días')],
        widget=forms.HiddenInput()
    )
# myapp/forms.py
from django import forms

class GmailForm(forms.Form):
    gmail = forms.EmailField(label='Correo Gmail', max_length=254, required=True)
