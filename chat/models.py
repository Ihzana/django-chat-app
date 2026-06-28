# from django.db import models
# Create your models here.
# chat/models.py
from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    # Who sent the message
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    # Who receives the message
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    
    # The actual message text
    content = models.TextField()
    
    # Auto-saved when message is created
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']  # oldest message first

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:30]}"
