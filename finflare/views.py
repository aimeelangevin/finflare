from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import LoginForm, RegisterForm, InvestmentSuggestionForm, InvestmentForm, GoalForm, ProfileForm, BankingInfoForm
from django.contrib.auth import authenticate, login, logout
from .models import Profile, BankingInfo, Goals, Investments, News, Spending
import requests
from django.db.models import Sum
from django.db.models.functions import TruncWeek
import json
from dotenv import load_dotenv
import os
from social_core.pipeline.partial import partial
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .ai_utils import generate_financial_tips, get_or_generate_tips
from django.core.cache import cache
from functools import wraps
from django.utils import timezone
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# Debug logging for OAuth credentials
print("Google OAuth2 Key:", os.getenv('GOOGLE_OAUTH2_KEY'))
print("Google OAuth2 Secret:", os.getenv('GOOGLE_OAUTH2_SECRET'))
print("GitHub Key:", os.getenv('GITHUB_KEY'))
print("GitHub Secret:", os.getenv('GITHUB_SECRET'))

def profile_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        try:
            profile = Profile.objects.get(user=request.user)
            if not profile.is_complete:
                return redirect('onboarding')
        except Profile.DoesNotExist:
            # Create a new profile for the user with default values
            Profile.objects.create(
                user=request.user,
                name=request.user.get_full_name() or request.user.username,
                age=0,
                income=0,
                current_employment='',
                retirement_date=None,
                savings=0,
                is_complete=False
            )
            return redirect('onboarding')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def redirect_based_on_profile(backend, user, response, *args, **kwargs):
    """
    Custom pipeline function to redirect users based on their profile status.
    New users will be redirected to onboarding, returning users to dashboard.
    """
    try:
        profile = Profile.objects.get(user=user)
        if not profile.is_complete:
            return redirect('onboarding')
        return redirect('dashboard')
    except Profile.DoesNotExist:
        # Create a new profile for the user with default values
        Profile.objects.create(
            user=user,
            name=user.get_full_name() or user.username,  # Use full name or username
            age=0,  # Default value
            income=0,  # Default value
            current_employment='',  # Empty string as default
            retirement_date=None,  # None as default
            savings=0,  # Default value
            is_complete=False  # Mark as incomplete
        )
        return redirect('onboarding')

def loginAction(request):
    # If user is already logged in, redirect them appropriately
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            if not profile.is_complete:
                return redirect('onboarding')
            return redirect('dashboard')
        except Profile.DoesNotExist:
            # Create a new profile for the user with default values
            Profile.objects.create(
                user=request.user,
                name=request.user.get_full_name() or request.user.username,
                age=0,
                income=0,
                current_employment='',
                retirement_date=None,
                savings=0,
                is_complete=False
            )
            return redirect('onboarding')

    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context= {
        "form" : LoginForm(),
        "pageName": "Login",
        }
        
        return render(request, 'finflare/start.html', context)

    # Creates a bound form from the request POST parameters
    form = LoginForm(request.POST)

    # Validates the form.
    if not form.is_valid():
        context['form'] = form
        return render(request, 'finflare/start.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect("dashboard")

def register(request):
    # If user is already logged in, redirect them appropriately
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            if not profile.is_complete:
                return redirect('onboarding')
            return redirect('dashboard')
        except Profile.DoesNotExist:
            # Create a new profile for the user with default values
            Profile.objects.create(
                user=request.user,
                name=request.user.get_full_name() or request.user.username,
                age=0,
                income=0,
                current_employment='',
                retirement_date=None,
                savings=0,
                is_complete=False
            )
            return redirect('onboarding')

    context={}
    
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context= {
        "form" : RegisterForm(),
        "pageName": "Register",
        
        }
        return render(request, 'finflare/register.html', context)

    # Creates a bound form from the request POST parameters
    # And makes the form available in the request context dictionary.
    form = RegisterForm(request.POST)

    # Validates the form.
    if not form.is_valid():
        context['form'] = form
        return render(request, 'finflare/register.html', context)

    # Create the user with just username, password, and email
    new_user = User.objects.create_user(
        username=form.cleaned_data['username'],
        password=form.cleaned_data['password'],
        email=form.cleaned_data['email']
    )

    # Create a profile with the full name
    Profile.objects.create(
        user=new_user,
        name=form.cleaned_data['first_name'] + ' ' + form.cleaned_data['last_name'],
        is_complete=False
    )

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    
    # Redirect to the onboarding page
    return redirect('onboarding')

def onboarding(request):
    if request.method == "POST":
        # Use the authenticated user
        current_user = request.user
        
        # Get profile data
        age = request.POST.get('age')
        income = request.POST.get('income')
        employment = request.POST.get('employment')
        retirement_date = request.POST.get('retirement_date')
        # Set retirement_date to None if it's empty
        if retirement_date == '':
            retirement_date = None
        savings = request.POST.get('savings')

        # Create or update the profile
        profile, created = Profile.objects.update_or_create(
            user=current_user,
            defaults={
                'age': age,
                'income': income,
                'current_employment': employment,
                'retirement_date': retirement_date,
                'savings': savings,
                'is_complete': True
            }
        )

        # Save banking info if provided
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        balance = request.POST.get('balance')
        
        if bank_name and account_number and balance:
            BankingInfo.objects.update_or_create(
                user=current_user,
                defaults={
                    'bank_name': bank_name,
                    'account_number': account_number,
                    'balance': balance
                }
            )

        # Save goal if provided
        goal_name = request.POST.get('goal_name')
        type_of_goal = request.POST.get('type_of_goal')
        goal_date = request.POST.get('goal_date')
        priority = request.POST.get('priority')
        amt = request.POST.get('amt')

        if goal_name and type_of_goal and goal_date and priority and amt:
            Goals.objects.create(
                profile=profile,
                goal_name=goal_name,
                type_of_goal=type_of_goal,
                goal_date=goal_date,
                priority=priority,
                amt=amt
            )

        # Save investment if provided
        investment_type = request.POST.get('investment_type')
        investment_name = request.POST.get('investment_name')
        user_amt = request.POST.get('user_amt')
        roi = request.POST.get('roi')
        growth_rate = request.POST.get('growth_rate')
        risk_level = request.POST.get('risk_level')

        if investment_type and investment_name and user_amt:
            # Convert empty strings to None for decimal fields
            roi = None if roi == '' else roi
            growth_rate = None if growth_rate == '' else growth_rate
            
            Investments.objects.create(
                profile=profile,
                investment_type=investment_type,
                investment_name=investment_name,
                user_amt=user_amt,
                roi=roi,
                growth_rate=growth_rate,
                risk_level=risk_level
            )

        return redirect('dashboard')
    
    # For GET requests, serve the React application's index.html
    return render(request, 'build/index.html', {})

def get_user(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'user': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        })
    return JsonResponse({'user': None})

@login_required
@profile_required
def dashboard(request):
    current_user = request.user
    
    profile = Profile.objects.filter(user=current_user).first()
    
    banking_info = BankingInfo.objects.filter(user=current_user).first()
    goals = Goals.objects.filter(profile=profile)
    investments = Investments.objects.filter(profile=profile)
    tips = News.objects.all() 

    investment_news = get_investment_articles()

    context = {
        'profile': profile,
        'banking_info': banking_info,
        'goals': goals,
        'investments': investments,
        'tips': tips,
        'investment_news': investment_news  # Add the latest news to the context
    }

    return render(request, 'finflare/dashboard.html', context)

@login_required
@profile_required
def articles(request):
    articles = get_investment_articles()
    return render(request, 'finflare/articles.html', {'articles': articles})


# Reference: Youtube Video to understand finance APIs and params
# Using Cache to reset the articles every 24 hours
def get_investment_articles():
    cached_articles = cache.get('daily_finance_articles')
    if cached_articles:
        return cached_articles
    
    api_url = "https://newsapi.org/v2/everything"
    api_key = settings.NEWS_API_KEY

    params = {
        'q': 'investment',
        'pageSize': 6, # Number of articles shown
        'apiKey': api_key,
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        articles =  response.json()['articles'] 
        cache.set('daily_finance_articles', articles, 60 * 60 * 24)
        return articles
    else:
        return []
      

@login_required
def spending(request):
    if request.method == 'POST':
        form = SpendingInputForm(request.POST)
        if form.is_valid():
            spending = form.save(commit=False)
            try:
                profile = Profile.objects.get(user=request.user)
                spending.profile = profile
                spending.save()
                return redirect('spending')
            except Profile.DoesNotExist:
                form.add_error(None, "User profile not found.")
    else:
        form = SpendingInputForm()
    spending_entries = Spending.objects.filter(profile__user=request.user).order_by('-transaction_date')

    # spending_type categories 
    spending_type_totals = Spending.objects.filter(profile__user=request.user).values('spending_type').annotate(total_spent=Sum('amt')).order_by('spending_type')
    #  overall spending 
    overall_spending = Spending.objects.filter(profile__user=request.user).aggregate(overall_total=Sum('amt'))['overall_total'] or 0

    # json conversion
    spending_type_labels = dict(Spending.SPENDING_TYPES)
    formatted_spending_type_totals = []
    for item in spending_type_totals:
        formatted_spending_type_totals.append({
            'spending_type': spending_type_labels.get(item['spending_type'], item['spending_type'].capitalize()),
            'total_spent': item['total_spent']
        })

    context= {
        'spending_entries': spending_entries,
        'form': form,
        'spending_type_totals': formatted_spending_type_totals,
        'overall_spending': overall_spending,
    }
    return render(request, 'finflare/src/spending.html', context)



def spending_data_json(request):
    """
    Returns spending data grouped by spending_type and the overall total as JSON
    for the currently logged-in user.
    """
    if request.user.is_authenticated:
        spending_type_totals_data = Spending.objects.filter(profile__user=request.user).values('spending_type').annotate(total_spent=Sum('amt')).order_by('spending_type')
        overall_spending = Spending.objects.filter(profile__user=request.user).aggregate(overall_total=Sum('amt'))['overall_total'] or 0

        spending_type_labels = dict(Spending.SPENDING_TYPES)
        formatted_totals_json = []
        for item in spending_type_totals_data:
            formatted_totals_json.append({
                'spending_type': spending_type_labels.get(item['spending_type'], item['spending_type'].capitalize()),
                'total_spent': item['total_spent']
            })

        data = {
            'spending_type_totals': formatted_totals_json,
            'overall_total': overall_spending,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

def spending_types_json(request):
    spending_types_data = [{'value': val, 'label': label} for val, label in Spending.SPENDING_TYPES]
    return JsonResponse(spending_types_data)




def get_investment_suggestions(investment_amount, risk_level, investment_type, market_sector, investment_horizon):   
    # Define investment types and their corresponding symbols
    investment_symbols = {
        'stocks': {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'MRK', 'ABBV', 'ABT'],
            'finance': ['JPM', 'BAC', 'V', 'MA', 'WFC', 'GS'],
            'energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC'],
            'consumer': ['WMT', 'MCD', 'PG', 'KO', 'AMZN', 'HD'],
            'industrial': ['GE', 'CAT', 'BA', 'MMM', 'HON', 'UPS'],
            'real_estate': ['O', 'PLD', 'AMT', 'EQIX', 'CCI', 'DLR']
        },
        'etfs': {
            'technology': ['XLK', 'VGT', 'IGV', 'SOXX', 'SMH', 'QQQ'],
            'healthcare': ['XLV', 'VHT', 'IHI', 'IBB', 'XHE', 'XHS'],
            'finance': ['XLF', 'VFH', 'KRE', 'KBE', 'KIE', 'KCE'],
            'energy': ['XLE', 'VDE', 'OIH', 'FCG', 'XOP', 'PSCE'],
            'consumer': ['XLP', 'VDC', 'XLY', 'VCR', 'XRT', 'PEJ'],
            'industrial': ['XLI', 'VIS', 'PPA', 'ITA', 'XAR', 'XHB'],
            'real_estate': ['VNQ', 'IYR', 'O', 'PLD', 'AMT', 'EQIX']
        },
        'mutual_funds': {
            'technology': ['FSCSX', 'FSPTX', 'FSPHX', 'FSPTX', 'FSCSX', 'FSPTX'],
            'healthcare': ['FSPHX', 'FSPHX', 'FSPHX', 'FSPHX', 'FSPHX', 'FSPHX'],
            'finance': ['FSRBX', 'FSRBX', 'FSRBX', 'FSRBX', 'FSRBX', 'FSRBX'],
            'energy': ['FSENX', 'FSENX', 'FSENX', 'FSENX', 'FSENX', 'FSENX'],
            'consumer': ['FSCPX', 'FSCPX', 'FSCPX', 'FSCPX', 'FSCPX', 'FSCPX'],
            'industrial': ['FSCGX', 'FSCGX', 'FSCGX', 'FSCGX', 'FSCGX', 'FSCGX'],
            'real_estate': ['FRESX', 'FRESX', 'FRESX', 'FRESX', 'FRESX', 'FRESX']
        },
        'bonds': {
            'technology': ['AGG', 'BND', 'BNDX', 'BNDW', 'BND', 'BNDX'],
            'healthcare': ['AGG', 'BND', 'BNDX', 'BNDW', 'BND', 'BNDX'],
            'finance': ['AGG', 'BND', 'BNDX', 'BNDW', 'BND', 'BNDX'],
            'energy': ['AGG', 'BND', 'BNDX', 'BNDW', 'BND', 'BNDX'],
            'consumer': ['AGG', 'BND', 'BNDX', 'BNDW', 'BND', 'BNDX'],
            'industrial': ['AGG', 'BND', 'BNDX', 'BNDW', 'BND', 'BNDX'],
            'real_estate': ['AGG', 'BND', 'BNDX', 'BNDW', 'BND', 'BNDX']
        }
    }
    
    # Get symbols based on investment type and sector
    symbols = investment_symbols.get(investment_type, {}).get(market_sector, [])
    
    # If no specific symbols found, use diversified ETFs
    if not symbols:
        symbols = ['SPY', 'VTI', 'QQQ', 'DIA']
    
    suggestions = []
    seen_symbols = set()  # Track unique symbols
    
    # Get data for each symbol
    for symbol in symbols:
        if len(suggestions) >= 4:  # Stop if we have 4 unique suggestions
            break
            
        if symbol in seen_symbols:  # Skip if we've already seen this symbol
            continue
            
        try:
            # Alpha Vantage API parameters
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': ALPHA_VANTAGE_API_KEY
            }
            
            response = requests.get("https://www.alphavantage.co/query", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'Global Quote' in data and data['Global Quote']:
                    quote = data['Global Quote']
                    
                    # Check if we have valid price data
                    price = quote.get('05. price')
                    if price and price != '0.0000':
                        suggestion = {
                            'symbol': symbol,
                            'name': symbol,  # Alpha Vantage doesn't provide names in this endpoint
                            'price': float(price),
                            'change': float(quote.get('09. change', 0)),
                            'change_percent': float(quote.get('10. change percent', '0').replace('%', '')),
                            'volume': int(quote.get('06. volume', 0)),
                            'risk_level': risk_level,
                            'investment_type': investment_type,
                            'market_sector': market_sector
                        }
                        suggestions.append(suggestion)
                        seen_symbols.add(symbol)  # Add to seen symbols
                    else:
                        print(f"No valid price data for {symbol}")
                else:
                    print(f"No Global Quote data for {symbol}")
            else:
                print(f"Error fetching data for {symbol}: Status code {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            continue
    
    return suggestions

@login_required
@profile_required
def investment_suggestion(request):
    if request.method == 'POST':
        form = InvestmentSuggestionForm(request.POST)
        if form.is_valid():
            # Get cleaned data
            investment_amount = form.cleaned_data['investment_amount']
            risk_level = form.cleaned_data['risk_level']
            investment_type = form.cleaned_data['investment_type']
            market_sector = form.cleaned_data['market_sector']
            investment_horizon = form.cleaned_data['investment_horizon']
            
            # Get investment suggestions
            suggestions = get_investment_suggestions(
                investment_amount=investment_amount,
                risk_level=risk_level,
                investment_type=investment_type,
                market_sector=market_sector,
                investment_horizon=investment_horizon
            )
            
            context = {
                'pageName': 'Investment Suggestions',
                'form': form,
                'success': True,
                'suggestions': suggestions,
                'investment_amount': investment_amount,
                'risk_level': risk_level,
                'investment_type': investment_type,
                'market_sector': market_sector,
                'investment_horizon': investment_horizon
            }
            return render(request, 'finflare/investment_suggestion.html', context)
    else:
        form = InvestmentSuggestionForm()
    
    context = {
        'pageName': 'Investment Suggestions',
        'form': form,
        'success': False
    }
    return render(request, 'finflare/investment_suggestion.html', context)

@login_required
@profile_required
def add_investment(request):
    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            profile = Profile.objects.filter(user=request.user).first()
            print(profile)
            Investments.objects.create(
                profile=profile,    
                investment_type=investment.investment_type,
                investment_name=investment.investment_name,
                user_amt=investment.user_amt,
                roi=investment.roi,
                growth_rate=investment.growth_rate,
                risk_level=investment.risk_level
            )
            message = "Investment added successfully"
            return render(request, 'finflare/add_investment.html', {'form': form, 'message': message})
    else:
        form = InvestmentForm()
    return render(request, 'finflare/add_investment.html', {'form': form})

@login_required
@profile_required
def tips(request):
    current_user = request.user
    profile = Profile.objects.filter(user=current_user).first()

    context = {
        'profile': profile,
    }
    return render(request, 'finflare/tips.html', context)

@require_http_methods(["GET"])
@profile_required
def generate_ai_tips(request):
    """
    Generate personalized financial tips using OpenAI based on the user's goals and investment data.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    
    try:
        # Get user's profile, goals, and investments
        profile = Profile.objects.filter(user=request.user).first()
        goals = Goals.objects.filter(profile=profile) if profile else []
        investments = Investments.objects.filter(profile=profile) if profile else []
        
        # Prepare context for OpenAI
        context = {
            "user_info": {
                "name": profile.name if profile else "User",
                "age": profile.age if profile else None,
                "income": profile.income if profile else None,
                "employment": profile.current_employment if profile else None,
                "savings": profile.savings if profile else None,
            },
            "goals": [
                {
                    "name": goal.goal_name,
                    "type": goal.get_type_of_goal_display(),
                    "date": goal.goal_date.strftime("%Y-%m-%d") if goal.goal_date else None,
                    "priority": goal.priority,
                    "amount": float(goal.amt) if goal.amt else None
                } for goal in goals
            ],
            "investments": [
                {
                    "type": investment.get_investment_type_display(),
                    "name": investment.investment_name,
                    "amount": float(investment.user_amt) if investment.user_amt else None,
                    "roi": float(investment.roi) if investment.roi else None,
                    "growth_rate": float(investment.growth_rate) if investment.growth_rate else None,
                    "risk_level": investment.risk_level
                } for investment in investments
            ]
        }
        
        # Get or generate tips using the AI utility function
        tips, message = get_or_generate_tips(request.user, context)
        
        return JsonResponse({"tips": tips, "message": message})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Code for if user wants to input a suggestion or ask a question
suggestions_list = []

def suggestion_form(request):
    if request.method == 'POST':
        suggestion = request.POST.get('suggestion')
        if suggestion:
            suggestions_list.append(suggestion)
            return render(request, 'finflare/thank_you.html', {'suggestion': suggestion})
    return render(request, 'finflare/suggestions.html')

def logoutAction(request):
    logout(request)
    return redirect("home")

@login_required
@profile_required
def investment_overview(request):
    """
    View to display all investments for the current user.
    """
    # Get the user's profile
    profile = Profile.objects.get(user=request.user)
    
    # Get all investments for this profile
    investments = Investments.objects.filter(profile=profile)
    
    context = {
        'pageName': 'Investment Overview',
        'investments': investments
    }
    
    return render(request, 'finflare/investment_overview.html', context)

@login_required
@profile_required
def goal_overview(request):
    profile = Profile.objects.get(user=request.user)
    goals = Goals.objects.filter(profile=profile)
    
    context = {
        'pageName': 'Goal Overview',
        'goals': goals
    }
    
    return render(request, 'finflare/goal_overview.html', context)

@login_required
@profile_required
def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            profile = Profile.objects.filter(user=request.user).first()
            Goals.objects.create(
                profile=profile,
                goal_name=goal.goal_name,
                type_of_goal=goal.type_of_goal,
                goal_date=goal.goal_date,
                priority=goal.priority,
                amt=goal.amt
            )
            message = "Goal added successfully"
            return render(request, 'finflare/add_goal.html', {'form': form, 'message': message})
    else:
        form = GoalForm()
    
    context = {
        'pageName': 'Add Goal',
        'form': form
    }
    return render(request, 'finflare/add_goal.html', context)

@login_required
@profile_required
def profile_view(request):
    current_user = request.user
    profile = get_object_or_404(Profile, user=current_user)
    banking_info = BankingInfo.objects.filter(user=current_user).first()
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        banking_form = BankingInfoForm(request.POST, instance=banking_info)
        
        # Handle profile form
        if profile_form.is_valid():
            profile_form.save()
            print(f"Profile saved successfully. New name: {profile_form.cleaned_data.get('name')}")
        else:
            print(f"Profile form errors: {profile_form.errors}")
            
        # Handle banking form
        if banking_form.is_valid():
            banking_form.save()
            print("Banking info saved successfully")
        else:
            print(f"Banking form errors: {banking_form.errors}")
            
        return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile)
        banking_form = BankingInfoForm(instance=banking_info)
    
    context = {
        'pageName': 'Profile',
        'profile': profile,
        'banking_info': banking_info,
        'profile_form': profile_form,
        'banking_form': banking_form
    }
    
    return render(request, 'finflare/profile.html', context)
