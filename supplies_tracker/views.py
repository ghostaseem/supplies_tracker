# from hamlpy.views.generic import HamlExtensionTemplateView
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Item, Storage, Space, Items_Storage
from .forms import item_form, storage_form, space_form, SignUpForm, LoginForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def items_index(request):
  items = Item.objects.all()
  return render(request, 'items/index.html.haml', { 'items': items })

@login_required
def items_new(request):
    storage_id = request.GET['storage_id']
    storage = Storage.objects.get(id=storage_id)
    print('storage')
    print(storage.name)

    if request.method == 'POST':
        form = item_form(request.POST)
        if form.is_valid():
            obj = Item(**form.cleaned_data)
            obj.save()
            content = Items_Storage.objects.create(item=obj, storage=storage, quantity=0)
            content.save()
            return HttpResponseRedirect('/items')
    else:
        form = item_form()

    return render(request, 'items/new.html.haml', { 'form': form })

@login_required
def storages_index(request):
  user_spaces = Space.objects.filter(user_id=request.user.id)
  user_spaces = user_spaces.values_list('id', flat=True)
  storages = Storage.objects.filter(space_id__in=user_spaces)
  return render(request, 'storages/index.html.haml', { 'storages': storages, 'user_spaces': user_spaces })

def storages_show(request, storage_id):
    try:
        storage = Storage.objects.get(id=storage_id)
        items = storage.items.all()
    except Storage.DoesNotExist:
        storage = None
        items = None

    # items = Storage.objects.values_list('items')
    # items = Storage.objects.filter(items)

    # items = Item.objects.filter(storages=storage)
    if storage is None:
        return render(request, 'error.html.haml' )
    else:
        return render(request, 'storages/show.html.haml', { 'storage': storage, 'items': items } )

@login_required
def storages_new(request):
    space_id = request.GET['space_id']
    space = Space.objects.get(id=space_id)

    if request.method == 'POST':
        form = storage_form(request.POST)
        if form.is_valid():
            obj = Storage(**form.cleaned_data)
            obj.space = space
            obj.save()

            return HttpResponseRedirect('/storages')
    else:
        form = storage_form()

    return render(request, 'storages/new.html.haml', { 'form': form, 'space': space })

@login_required
def spaces_index(request):
  spaces = Space.objects.filter(user_id=request.user.id)
  enum_spaces = enumerate(spaces)
  return render(request, 'spaces/index.html.haml', { 'enum_spaces': enum_spaces })

@login_required
def spaces_show(request, space_id):
  space = Space.objects.get(id=space_id)
  storages = Storage.objects.filter(space_id=space_id)
  return render(request, 'spaces/show.html.haml', { 'space': space, 'storages': storages } )

@login_required
def spaces_new(request):
    if request.method == 'POST':
        form = space_form(request.POST)
        if form.is_valid():
            obj = Space(**form.cleaned_data)
            obj.user = request.user
            obj.save()

            return HttpResponseRedirect('/spaces')
    else:
        form = space_form()

    return render(request, 'spaces/new.html.haml', { 'form': form })

def home(request):
    return render(request, 'home.html.haml')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home.html.haml')
    else:
        form = SignUpForm()
    if request.user.is_authenticated():
        return render(request, 'home.html.haml')
    else:
        return render(request, 'signup.html.haml', { 'form': form })

def logout_view(request):
    logout(request)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                # Redirect to a success page.
                return render(request, 'home.html.haml')
            else:
                # Return a 'disabled account' error message
                return render(request, 'home.html.haml')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'home.html.haml')
    else:
        form = LoginForm()

    return render(request, 'login.html.haml', { 'form': form })
