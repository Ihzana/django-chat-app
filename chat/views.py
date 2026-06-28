from django.shortcuts import render

# Create your views here.

# chat/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Message


# ── REGISTER ──────────────────────────────────────────────────
def register_view(request):
    if request.method == 'POST':
        # UserCreationForm = Django's built-in registration form
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()       # saves to DB
            login(request, user)     # log them in right away
            return redirect('chat')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# ── LOGIN ─────────────────────────────────────────────────────
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('chat')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# ── LOGOUT ────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')


# ── MAIN CHAT PAGE ────────────────────────────────────────────
@login_required   # ← redirects to /login/ if not logged in
def chat_view(request, user_id=None):
    # Get all users except yourself for the sidebar
    users = User.objects.exclude(id=request.user.id)
    chat_with = None
    messages = []

    if user_id:
        chat_with = get_object_or_404(User, id=user_id)
        
        # Fetch last 15 messages between these two users
        messages = Message.objects.filter(
            sender__in=[request.user, chat_with],
            receiver__in=[request.user, chat_with]
        ).order_by('-timestamp')[:15]   # newest 15
        
        messages = list(reversed(messages))  # flip to show oldest first

    return render(request, 'chat.html', {
        'users': users,
        'chat_with': chat_with,
        'messages': messages,
    })


# ── REST API: Get Messages (used by JavaScript fetch) ─────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('-timestamp')[:15]

    # Convert queryset to JSON-friendly list
    data = [{
        'id': m.id,
        'sender': m.sender.username,
        'content': m.content,
        'timestamp': m.timestamp.strftime('%H:%M'),
        'is_mine': m.sender == request.user,
    } for m in reversed(list(messages))]

    return Response(data)


# ── REST API: Send Message ─────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    content = request.data.get('content', '').strip()

    if not content:
        return Response({'error': 'Message cannot be empty'}, status=400)

    message = Message.objects.create(
        sender=request.user,
        receiver=other_user,
        content=content,
    )
    return Response({
        'id': message.id,
        'sender': message.sender.username,
        'content': message.content,
        'timestamp': message.timestamp.strftime('%H:%M'),
    }, status=201)
