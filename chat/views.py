from django.shortcuts import render,get_object_or_404

# Create your views here.
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Thread, Message
from django.http import Http404

def register(request):
    if request.user.is_authenticated:
        return redirect('thread_list')
    if request.method == 'POST':
        form = UserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login
            return redirect('thread_list')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('thread_list')
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('thread_list')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'auth/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def test(request):
    return render(request, 'chat/test.html')

# ----------------
@login_required
def thread_list(request):
    threads = Thread.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )
    return render(request, 'chat/thread_list.html', {'threads': threads})


@login_required
def chat_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    if request.method == 'POST':
        text = request.POST.get('text')
        reply_to_id = request.POST.get('reply_to')
        reply_to = Message.objects.filter(id=reply_to_id).first() if reply_to_id else None
        image = request.FILES.get("file") if request.FILES.get("file") and request.FILES.get("file").content_type.startswith('image') else None
        file = request.FILES.get("file") if request.FILES.get("file") and not request.FILES.get("file").content_type.startswith('image') else None

        # image = request.FILES.get('image')
        # file = request.FILES.get('file')

        Message.objects.create(
            thread=thread,
            sender=request.user,
            text=text,
            reply_to=reply_to,
            image=image,
            file=file
        )
        return redirect('chat_home', thread_id=thread.id)

    messages = thread.messages.order_by('timestamp')
    return render(request, 'chat/chat.html', {'thread': thread, 'messages': messages})



@login_required
def start_new_chat(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        other_user = User.objects.get(id=user_id)

        # Ensure a unique thread for these 2
        thread, created = Thread.objects.get_or_create(
            user1=min(request.user, other_user, key=lambda u: u.id),
            user2=max(request.user, other_user, key=lambda u: u.id),
        )
        return redirect('chat_home', thread_id=thread.id)

    # GET request -> show the user list
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/start_new_chat.html', {'users': users})