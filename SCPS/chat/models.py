import json

from django.contrib.auth import get_user_model
from django.db import models

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = get_user_model()


class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    def last_10_messages(self):
        return Message.objects.order_by('-timestamp').all()[:10]


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.TextField(max_length=100)
    is_seen = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        notification_objs = Notification.objects.filter(is_seen=False).count()
        data = {'count': notification_objs, 'current_notification': self.notification}
        async_to_sync(channel_layer.group_send)(
            'chat_test',  # group _ name
            {
                'type': 'chat_message',
                'message': json.dumps(data)
            }
        )

        super(Notification, self).save(*args,**kwargs)

