from django.db import models
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Thread(models.Model):
    user1 = models.ForeignKey(User, related_name='threads_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='threads_as_user2', on_delete=models.CASCADE)

    class Meta:
        unique_together = [['user1', 'user2']]
    
    def __str__(self):
        return f"Thread between {self.user1.username} and {self.user2.username}"

class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)  # Optional text
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)  # Images
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)  # For files
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)  # Reply
    reactions = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


    def __str__(self):
        if self.text:
            return f"{self.sender.username}: {self.text}"
        elif self.image:
            return f"{self.sender.username}: [Image]"
        elif self.file:
            return f"{self.sender.username}: [File]"
        else:
            return f"{self.sender.username}: [Empty Message]"



class GroupThread(models.Model):
    name = models.CharField(max_length=100, unique=True)
    participants = models.ManyToManyField(User, related_name='group_threads')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroupMessage(models.Model):
    group_thread = models.ForeignKey(GroupThread, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='group_images/', blank=True, null=True)
    file = models.FileField(upload_to='group_files/', blank=True, null=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)  # Reply
    reactions = models.JSONField(default=dict, blank=True)  # ✅ New field
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.text or '[Media]'}"


