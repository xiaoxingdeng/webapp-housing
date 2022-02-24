from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import validators
from phonenumber_field.formfields import PhoneNumberField

from housing.models import *
from django.forms import ModelForm, Textarea, TextInput

MAX_UPLOAD_SIZE = 5000000

class LoginForm(forms.Form):
    username = forms.CharField(max_length = 20)
    password = forms.CharField(max_length = 200, widget = forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegisterForm(forms.Form):
    username   = forms.CharField(max_length = 20, 
                                 label='Andrew Id')
    password  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput(), 
                                 validators=[validate_password],
                                 help_text="At least 8 length, must contain numbers and avoid similar attr password.")
    
    confirm_password  = forms.CharField(max_length = 200, 
                                 label='Confirm',  
                                 widget = forms.PasswordInput())
    email      = forms.CharField(max_length=50,
                                 label='E-mail',
                                 widget = forms.EmailInput(), 
                                 help_text="Must use a cmu andrew email.")
    first_name = forms.CharField(max_length=20, 
                                 label='First Name')
    last_name  = forms.CharField(max_length=20, 
                                 label='Last Name')

                                 
    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the email field.
    def clean_email(self):
        # Confirms that the email is not already present in the
        # User model database.
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email).exists() or not email.endswith("@andrew.cmu.edu"):
             raise forms.ValidationError("Email exists or is not cmu andrew email")
        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return email
    def clean_username(self):
        # Confirms that the email is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username).exists():
             raise forms.ValidationError("username exists")
        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('description', 'profile_picture')
        widgets = {
            'description': forms.Textarea(attrs={'id':'id_bio_input_text', 'rows':'3'}),
            'profile_picture': forms.FileInput(attrs={'id':'id_profile_picture'})
        }
        labels = {
                'description':'Description',
                'profile_picture':'Upload Image'
                }
    def clean_picture(self):
        picture = self.cleaned_data['profile_picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture

class HProfileForm(forms.ModelForm):
    class Meta:
        model = HProfile
        fields = ('description', 'picture', 'region', 'room_type', 'house_type', 'price', 'area', 'distance2cmu','address','latitude','longtitude')
        labels = {
                'description':'Description',
                'picture':'Picture',
                'region':'Region',
                'room_type':'Room_type',
                'house_type':'House_type',
                'price':'Price',
                'area':'Area Size',
                'distance2cmu':'Distance to cmu',
                'address':'Address',
                'latitude':'latitude',
                'longtitude':'longtitude',
                }
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if(not description):
            raise forms.ValidationError("Description can not be empty.")
        return description

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture

'''
class MessageTextForm(forms.ModelForm):
    class Meta:
        model = MessageText
        field = ('text')
        labels = {
            'text':'send message',
        }
        def clean_post_text(self):
        text = self.cleaned_data.get('text')
        if(not text):
            raise forms.ValidationError("text can not be empty.")
        return text
'''


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')    
    class Meta:
        model = Images
        fields = ('image', )
    def clean_picture(self):
        picture = self.cleaned_data['image']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture

