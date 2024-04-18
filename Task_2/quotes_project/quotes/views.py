from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from quotes.models import Quote, LogoutForm
from django.contrib.auth import views as auth_views
from .forms import UserRegistrationForm, AuthorForm, ScrapeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import logout as auth_logout
from .models import Author, Tag, Quote
from django.contrib import messages
from .forms import QuoteForm, UserLoginForm, UserRegistrationForm, AuthorForm, ScrapeForm
from django.db.models import Count
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from quotes import scrape_quotes
from bs4 import BeautifulSoup
import requests


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')  
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def home(request):
    tags = Tag.objects.all() 
    login_form = AuthenticationForm()
    registration_form = UserCreationForm()
    logout_form = None  

    if request.user.is_authenticated:
        logout_form = LogoutForm()  

    top_tags = Tag.objects.annotate(num_quotes=Count('quotes')).order_by('-num_quotes')[:10]

    return render(request, 'home.html', {'login_form': login_form, 'registration_form': registration_form, 'logout_form': logout_form, 'tags': tags, 'top_tags': top_tags})

@login_required
def exit_page(request):
    auth_logout(request)
    return redirect('home')

@login_required
def add_author(request):
    form = AuthorForm()
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            author, created = Author.objects.get_or_create(name=name)
            if created:
                messages.success(request, 'Author added')
            else:
                messages.error(request, 'This author already exists')
            return redirect('home')  
    return render(request, 'add_author.html', {'form': form})

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_profile.html'

def author_detail(request, pk):
    author = Author.objects.get(pk=pk)
    return render(request, 'author_detail.html', {'author': author})

@login_required
def add_quote(request):
    # Отримання топ-10 тегів з найбільшою кількістю цитат
    top_tags = Tag.objects.order_by('-quote_count')[:10]
    
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.save()
            tags_input = form.cleaned_data.get('tags')
            if tags_input:
                tags_list = tags_input.split(',')
                for tag_name in tags_list:
                    tag_name = tag_name.strip()
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    quote.tags.add(tag)
            return redirect('quote_list')
    else:
        form = QuoteForm()
    return render(request, 'add_quote.html', {'form': form, 'top_tags': top_tags})


def all_authors(request):
    authors = Author.objects.all()
    return render(request, 'all_authors.html', {'authors': authors})

def quote_list(request):
    quotes = Quote.objects.all()
    return render(request, 'quote_list.html', {'quotes': quotes})

def author_quotes(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    quotes = author.quote_set.all()
    return render(request, 'author_quotes.html', {'author': author, 'quotes': quotes})

def author_list(request):
    authors = Author.objects.all()
    return render(request, 'author_list.html', {'authors': authors})

def tag_quotes(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    quotes = tag.quotes.all()
    if not quotes:
        messages.info(request, 'There are no quotes with this tag.')
    return render(request, 'tag_quotes.html', {'tag': tag, 'quotes': quotes})

def quotes_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    quotes = tag.quotes.all()
    return render(request, 'quotes_by_tag.html', {'tag': tag, 'quotes': quotes})

def quote_list(request):
    quote_list = Quote.objects.all()
    paginator = Paginator(quote_list, 10)  # Показувати 10 цитат на сторінці
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'quote_list.html', {'page_obj': page_obj})

def scrape_quotes_view(request):
    if request.method == 'POST':
        form = ScrapeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    quotes = soup.find_all('span', class_='text')
                    for quote in quotes:
                        print(quote.text)
                    return HttpResponseRedirect('/success/') 
                else:
                    return render(request, 'error.html')  
            except Exception as e:
                print(f"An error occurred: {e}")
                return render(request, 'error.html') 
    else:
        form = ScrapeForm()
    return render(request, 'scrape_quotes.html', {'form': form})

def success_view(request):
    return render(request, 'success.html')