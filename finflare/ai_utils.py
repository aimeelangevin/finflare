import json
import requests
import os
import hashlib
from django.conf import settings
from dotenv import load_dotenv
from .models import AIGeneratedTips

# Load environment variables
load_dotenv()

def calculate_user_data_hash(user_context):
    try:
        # Handle None values in the context
        if user_context is None:
            raise ValueError("User context is None")
            
        # Ensure all required keys exist
        required_keys = ['user_info', 'goals', 'investments']
        for key in required_keys:
            if key not in user_context:
                raise ValueError(f"Missing required key in user context: {key}")
        
        # Convert Decimal values to float and handle None values
        def convert_decimal_to_float(obj):
            from decimal import Decimal
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimal_to_float(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimal_to_float(item) for item in obj]
            return obj
        
        # Convert the context to a string and calculate its hash
        safe_context = convert_decimal_to_float(user_context)
        context_str = json.dumps(safe_context, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()
        
    except Exception as e:
        raise

def get_or_generate_tips(user, user_context):
    try:
        # Calculate hash of current user data
        current_hash = calculate_user_data_hash(user_context)
        
        # Try to get existing tips
        try:
            existing_tips = AIGeneratedTips.objects.get(user=user)
            
            # Check if user data has changed
            if existing_tips.user_data_hash == current_hash:
                # Data hasn't changed, return existing tips
                message = "No changes to your financial data. Tips not updated."
                return existing_tips.tips_content, message
            else:
                # Data has changed, generate new tips
                tips = generate_financial_tips(user_context)
                message = "New tips generated successfully."
                
                # Update the existing record
                existing_tips.tips_content = tips
                existing_tips.user_data_hash = current_hash
                existing_tips.save()
                
                return tips, message
        except AIGeneratedTips.DoesNotExist:
            # No tips exist yet, generate new ones
            tips = generate_financial_tips(user_context)
            
            # Create a new record
            AIGeneratedTips.objects.create(
                user=user,
                tips_content=tips,
                user_data_hash=current_hash
            )
            
            return tips
            
    except Exception as e:
        raise

def generate_financial_tips(user_context):
    """
    Generate personalized financial tips using OpenAI based on the user's context.
    
    Args:
        user_context (dict): Dictionary containing user profile, goals, and investments data
        
    Returns:
        str: Generated financial tips
    """
    # Try to get API key from settings first, then environment
    api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError("OpenAI API key not found. Please check your .env file or settings.")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = create_financial_tips_prompt(user_context)
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a financial advisor providing personalized financial tips."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code != 200:
            error_detail = response.json().get('error', {}).get('message', response.text)
            raise Exception(f"OpenAI API error (Status {response.status_code}): {error_detail}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to connect to OpenAI API: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse OpenAI API response")
    except Exception as e:
        raise Exception(f"Error generating tips: {str(e)}")

def create_financial_tips_prompt(user_context):
    """
    Create a prompt for generating financial tips based on user context.
    
    Args:
        user_context (dict): Dictionary containing user profile, goals, and investments data
        
    Returns:
        str: Formatted prompt for OpenAI
    """
    return f"""
    Based on the following user financial data, generate personalized financial tips:
    
    User Information:
    - Name: {user_context['user_info']['name']}
    - Age: {user_context['user_info']['age']}
    - Income: ${user_context['user_info']['income']}
    - Employment: {user_context['user_info']['employment']}
    - Current Savings: ${user_context['user_info']['savings']}
    
    Financial Goals:
    {json.dumps(user_context['goals'], indent=2)}
    
    Investment Portfolio:
    {json.dumps(user_context['investments'], indent=2)}
    
    Please provide personalized financial tips in the following structured format:
    
    [SPENDING_TIPS]
    - Tip 1 about spending habits and budgeting
    - Tip 2 about spending habits and budgeting
    
    [GOALS_TIPS]
    - Tip 1 about achieving financial goals
    - Tip 2 about achieving financial goals
    
    [INVESTMENT_TIPS]
    - Tip 1 about investment strategy
    - Tip 2 about investment strategy
    
    [GENERAL_TIPS]
    - Tip 1 about general financial wellness
    - Tip 2 about general financial wellness
    
    Make the tips specific, actionable, and tailored to their situation. Each category should have at least one tip, and you can add more if relevant.
    """ 