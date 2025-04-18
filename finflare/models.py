from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class Profile(models.Model):
    """
    Profile model stores a particular user's profile with certain 
    financial information and relevant data
    """
    user = models.ForeignKey(User, on_delete=models.PROTECT,)  # User
    name = models.CharField(max_length=200, null=True, blank=True)  # User name
    income = models.DecimalField(max_digits=10000000000, decimal_places=2, null=True, blank=True)  # User monthly income 
    savings = models.DecimalField(max_digits=100000000000, decimal_places=2, null=True, blank=True)  # User savings amount
    current_employment = models.CharField(max_length=200, null=True, blank=True)  # User employment status and job
    age = models.IntegerField(validators=[MinValueValidator(18)], null=True, blank=True)  # User should at least be 18 years old
    retirement_date = models.DateField(null=True, blank=True)  # User goal retirement date
    is_complete = models.BooleanField(default=False)  # Whether the profile is complete

    def __str__(self):
        return f"Profile for {self.user.username}"

class BankingInfo(models.Model):
    """
    BankingInfo model stores the banking information for a particular user.
    It stores:
    user, account number, bank's name, and the total account balance
    """
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT) # User
    account_number = models.CharField(max_length=50) # Account Number
    bank_name = models.CharField(max_length=100) # Bank Name
    balance = models.DecimalField(max_digits=100000000, decimal_places=2) # Total Account Balance 
    
    def __str__(self):
        return f'user={self.user}, id={self.id}, bank_name="{self.bank_name}", balance={self.balance}'

class Spending(models.Model):
    """
    Spending model storews information about user spending,
    stores information about specific transactions
    """
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)  # User Profile
    SPENDING_TYPES = [
        ('groceries', 'Groceries'),
        ('entertainment', 'Entertainment'),
        ('utilities', 'Utilities'),
        ('dining', 'Dining'),
        ('transportation', 'Transportation'),
    ]
    spending_type = models.CharField(max_length=50, choices=SPENDING_TYPES, blank=True, null=True)
    amt = models.DecimalField(max_digits=100000, decimal_places=2)  
    location = models.CharField(max_length=200) 
    category = models.CharField(max_length=100)  
    transaction_date = models.DateTimeField()  

    def __str__(self):
        return f"Spending of {self.amt} at {self.location} on {self.transaction_date}"
    
class Goals(models.Model):
    """
    Goals model stores financial goals set by the user
    """
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)  # User Profile
    goal_name = models.CharField(max_length=200, blank=True, null=True)  # Goal text
    GOAL_TYPES = [
        ('save_money', 'Save Money'),
        ('buy_house', 'Buy a House'),
        ('pay_debt', 'Pay Off Debt'),
        ('emergency_fund', 'Emergency Fund'),
        ('not_set', 'None for now!')
    ]
    type_of_goal = models.CharField(max_length=50, choices=GOAL_TYPES, blank=True, null=True)
    goal_date = models.DateField(blank=True, null=True)  # Date to have goal achieved by
    priority = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=True, null=True)  # Priority level of the goal
    amt = models.DecimalField(max_digits=10000000000, decimal_places=2, blank=True, null=True)  # Money amount goal

    def __str__(self):
        return f"Goal: {self.goal_name} (Priority: {self.priority})"

class Investments(models.Model):
    """
    Investment model keeps track of user's investments and information related
    to each specific investment
    """
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)  # User Profile
    INVESTMENT_TYPES = [
        ('stocks', 'Stocks'),
        ('bonds', 'Bonds'),
        ('mutual_funds', 'Mutual Funds'),
        ('real_estate', 'Real Estate'),
        ('crypto', 'Crypto'),
        ('not_set', 'None for now!')
    ]
    investment_type = models.CharField(max_length=50, choices=INVESTMENT_TYPES, blank=True, null=True)
    investment_name = models.CharField(max_length=200, blank=True, null=True)  # Investment Name
    user_amt = models.DecimalField(max_digits=1000000000000, decimal_places=2, blank=True, null=True)  # Amount invested
    roi = models.DecimalField(max_digits=100000000000, decimal_places=2, blank=True, null=True)  # Return on Investment (ROI)
    growth_rate = models.DecimalField(max_digits=1000000000, decimal_places=2, blank=True, null=True)  # Investment growth rate
    risk_level = models.CharField(max_length=50, blank=True, null=True)  # Risk level ranking (1-5 or low-medium)

class Suggestions(models.Model):
    """
    Suggestions model stores suggestions specific to the user based on their
    accounts, spending, lifestyle, and investments
    """
    text = models.CharField(max_length=200)  # Suggestion text
    category = models.CharField(max_length=100)  # Suggestion Category (Spending tips, investment tips, etc.)
    profile = models.ForeignKey(Investments, on_delete=models.PROTECT)  # Investments

    def __str__(self):
        return f"Suggestion: {self.text} (Category: {self.category})"

class News(models.Model):
    """
    News model stores relevant articles shown to the user to inform them on
    current financial trends and to help provide financial information and education 
    """
    name_of_article = models.CharField(max_length=200)  # Article name 
    publishing_date = models.DateTimeField()  # Article published date and time
    author = models.CharField(max_length=200)  # Article Author
    link = models.URLField(max_length=200)  # Article URL

    def __str__(self):
        return f"Article: {self.name_of_article} by {self.author}"

class AIGeneratedTips(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_tips')
    tips_content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    user_data_hash = models.CharField(max_length=64, help_text="Hash of user data to detect changes")
    
    def __str__(self):
        return f"Tips for {self.user.username} - {self.last_updated.strftime('%Y-%m-%d %H:%M')}"



