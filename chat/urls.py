# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/',          views.login_view,    name='login'),
    path('logout/',         views.logout_view,   name='logout'),
    path('register/',       views.register_view, name='register'),
    path('chat/',           views.chat_view,     name='chat'),
    path('chat/<int:user_id>/', views.chat_view, name='chat_with'),

    # REST API endpoints (called by JavaScript)
    path('api/messages/<int:user_id>/', views.get_messages, name='api_messages'),
    path('api/send/<int:user_id>/',     views.send_message, name='api_send'),
]