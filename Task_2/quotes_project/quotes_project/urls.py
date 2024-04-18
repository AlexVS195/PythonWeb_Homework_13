"""quotes_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from quotes import views 
from django.contrib.auth import views as auth_views
from quotes.views import exit_page, author_quotes, UserProfileView, add_author, add_quote, all_authors, tag_quotes
from quotes.views import scrape_quotes_view, success_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('exit/', views.exit_page, name='exit'),
    path('accounts/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('add_author/', views.add_author, name='add_author'),
    path('add_quote/', add_quote, name='add_quote'),
    path('all_authors/', all_authors, name='all_authors'),
    path('author/<int:author_id>/', author_quotes, name='author_quotes'),
    path('quotes/', views.quote_list, name='quote_list'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
    path('tag/<int:tag_id>/', tag_quotes, name='tag_quotes'),
    path('quotes_by_tag/<int:tag_id>/', views.quotes_by_tag, name='quotes_by_tag'),
    path('scrape/', scrape_quotes_view, name='scrape'),
    path('success/', success_view, name='success'),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]