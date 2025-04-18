from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Profile, BankingInfo, Goals, Investments,Spending
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, EmailValidator, RegexValidator
import re

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        error_messages={
            'required': 'Please enter your username.',
            'max_length': 'Username must be less than 20 characters.'
        }
    )
    password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(),
        error_messages={
            'required': 'Please enter your password.',
            'max_length': 'Password must be less than 50 characters.'
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid username or password. Please try again.")
            if not user.is_active:
                raise forms.ValidationError("Your account has been disabled. Please contact support.")
        
        return cleaned_data
    
class RegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=20,
        error_messages={
            'required': 'Please enter your first name.',
            'max_length': 'First name must be less than 20 characters.',
            'invalid': 'First name can only contain letters, spaces, hyphens, and apostrophes.'
        }
    )
    last_name = forms.CharField(
        max_length=20,
        error_messages={
            'required': 'Please enter your last name.',
            'max_length': 'Last name must be less than 20 characters.',
            'invalid': 'Last name can only contain letters, spaces, hyphens, and apostrophes.'
        }
    )
    email = forms.EmailField(
        max_length=50,
        validators=[EmailValidator()],
        error_messages={
            'required': 'Please enter your email address.',
            'max_length': 'Email must be less than 50 characters.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    username = forms.CharField(
        max_length=20,
        error_messages={
            'required': 'Please choose a username.',
            'max_length': 'Username must be less than 20 characters.'
        }
    )
    password = forms.CharField(
        max_length=200,
        widget=forms.PasswordInput(),
        error_messages={
            'required': 'Please enter a password.',
            'max_length': 'Password must be less than 200 characters.'
        }
    )
    confirm_password = forms.CharField(
        max_length=200,
        widget=forms.PasswordInput(),
        error_messages={
            'required': 'Please confirm your password.',
            'max_length': 'Password must be less than 200 characters.'
        }
    )

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            # Allow letters, spaces, hyphens, and apostrophes
            if not re.match(r'^[a-zA-Z\s\'\-]+$', first_name):
                raise forms.ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            # Allow letters, spaces, hyphens, and apostrophes
            if not re.match(r'^[a-zA-Z\s\'\-]+$', last_name):
                raise forms.ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes.")
        return last_name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match. Please try again.")
        
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("This username is already taken. Please choose another one.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email):
            raise forms.ValidationError("This email address is already registered. Please use a different one or try logging in.")
        return email

class InvestmentSuggestionForm(forms.Form):
    INVESTMENT_AMOUNTS = [
        ('$1,000', '$1,000'),
        ('$5,000', '$5,000'),
        ('$10,000', '$10,000'),
        ('$25,000', '$25,000'),
        ('$50,000', '$50,000'),
        ('$100,000', '$100,000'),
        ('$500,000', '$500,000'),
        ('$1,000,000', '$1,000,000')
    ]
    
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk')
    ]
    
    INVESTMENT_TYPES = [
        ('stocks', 'Stocks'),
        ('etfs', 'ETFs'),
        ('mutual_funds', 'Mutual Funds'),
        ('bonds', 'Bonds')
    ]
    
    MARKET_SECTORS = [
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('energy', 'Energy'),
        ('consumer', 'Consumer'),
        ('industrial', 'Industrial'),
        ('real_estate', 'Real Estate')
    ]
    
    INVESTMENT_HORIZONS = [
        ('short_term', 'Short Term (1-3 years)'),
        ('medium_term', 'Medium Term (3-7 years)'),
        ('long_term', 'Long Term (7+ years)')
    ]
    
    investment_amount = forms.ChoiceField(
        choices=INVESTMENT_AMOUNTS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    risk_level = forms.ChoiceField(
        choices=RISK_LEVELS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    investment_type = forms.ChoiceField(
        choices=INVESTMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    market_sector = forms.ChoiceField(
        choices=MARKET_SECTORS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    investment_horizon = forms.ChoiceField(
        choices=INVESTMENT_HORIZONS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investments
        fields = ['investment_type', 'investment_name', 'user_amt', 'roi', 'growth_rate', 'risk_level']
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
class GoalForm(forms.ModelForm):
    class Meta:
        model = Goals
        fields = ['goal_name', 'type_of_goal', 'goal_date', 'priority', 'amt']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'age', 'income', 'current_employment', 'retirement_date', 'savings']
        widgets = {
            'retirement_date': forms.DateInput(attrs={'type': 'date'}),
            'age': forms.NumberInput(attrs={'min': '16', 'max': '100'}),
        }
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None:
            if age < 16:
                raise forms.ValidationError("You must be at least 16 years old")
            if age > 100:
                raise forms.ValidationError("Please enter a valid age (between 16 and 100)")
        return age
    
    def clean_current_employment(self):
        employment = self.cleaned_data.get('current_employment')
        if employment:
            # Allow letters, spaces, apostrophes, hyphens, periods, ampersands, and commas
            import re
            valid_employment_regex = re.compile(r'^[a-zA-Z\s\'\-\.&,]+$')
            if not valid_employment_regex.match(employment):
                raise forms.ValidationError("Please enter a valid employment")
        return employment
    
    def clean_income(self):
        income = self.cleaned_data.get('income')
        if income is not None and income <= 0:
            raise forms.ValidationError("Please enter a valid income amount")
        return income
    
    def clean_savings(self):
        savings = self.cleaned_data.get('savings')
        if savings is not None and savings < 0:
            raise forms.ValidationError("Please enter a valid savings amount")
        return savings

class BankingInfoForm(forms.ModelForm):
    class Meta:
        model = BankingInfo
        fields = ['bank_name', 'account_number', 'balance']
    
    def clean_bank_name(self):
        bank_name = self.cleaned_data.get('bank_name')
        if bank_name:
            # Allow letters, spaces, apostrophes, hyphens, periods, and ampersands
            import re
            valid_bank_name_regex = re.compile(r'^[a-zA-Z\s\'\-\.&]+$')
            if not valid_bank_name_regex.match(bank_name):
                raise forms.ValidationError("Please enter a valid bank name")
        return bank_name
    
    def clean_balance(self):
        balance = self.cleaned_data.get('balance')
        if balance is not None and balance < 0:
            raise forms.ValidationError("Please enter a valid balance amount")
        return balance
        


class SpendingInputForm(forms.ModelForm):
    class Meta:
        model = Spending
        fields = ['spending_type', 'amt', 'location', 'category', 'transaction_date']
        widgets = {
            'spending_type': forms.Select(choices=Spending.SPENDING_TYPES),
            'amt': forms.NumberInput(attrs={'placeholder': 'Enter amount'}),
            'location': forms.TextInput(attrs={'placeholder': 'Where did you spend it?'}),
            'category': forms.TextInput(attrs={'placeholder': 'Specific category'}),
            'transaction_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category_choices = [('', 'Select a Category')] + Spending.SPENDING_TYPES
        self.fields['category'].widget.choices = category_choices
        self.fields['category'].required = False  # Make the location field optional
        self.fields['location'].required = False  # Make the location field optional
