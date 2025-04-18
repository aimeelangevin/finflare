"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from finflare import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.loginAction, name='home'),
    path('register/', views.register, name='register'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('login/', views.loginAction, name='login'),
    path('spending/', views.spending, name='spending'),
    path('spending/data.json/', views.spending_data_json, name='spending_data_json'),
    path('spending/types.json/', views.spending_types_json, name='spending_types_json'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('investment-suggestion/', views.investment_suggestion, name='investment_suggestion'),
    path('tips/', views.tips, name='tips'),
    path('api/generate-ai-tips/', views.generate_ai_tips, name='generate_ai_tips'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('articles/', views.articles, name='articles'),
    path('suggestions/', views.suggestion_form, name='suggestion_form'),
    path('logout/', views.logoutAction, name='logout'),
    path('add-investment/', views.add_investment, name='add_investment'),
    path('investment-overview/', views.investment_overview, name='investment_overview'),
    path('goal-overview/', views.goal_overview, name='goal_overview'),
    path('add-goal/', views.add_goal, name='add_goal'),
    path('profile/', views.profile_view, name='profile'),
]
