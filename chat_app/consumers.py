import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .models import Room, Message


class ChatConsumer(WebsocketConsumer):

    def connect(self):

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        self.room_group_name = f"chat_{self.room_name}"

        async_to_sync(
            self.channel_layer.group_add
        )(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

        self.send_history()

    def disconnect(self, close_code):

        async_to_sync(
            self.channel_layer.group_discard
        )(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):

        data = json.loads(text_data)

        message = data.get("message", "").strip()
        username = data.get("username") or "Anonymous"

        if not message:
            return

        self.save_message(username, message)

        async_to_sync(
            self.channel_layer.group_send
        )(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    def chat_message(self, event):

        self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "username": event["username"],
                }
            )
        )

    def save_message(self, username, message):

        room, _ = Room.objects.get_or_create(name=self.room_name)

        Message.objects.create(
            room=room,
            username=username,
            content=message,
        )

    def send_history(self):

        messages = (
            Message.objects
            .filter(room__name=self.room_name)
            .order_by("created_at")
            .values("username", "content")
        )

        for msg in messages:
            self.send(
                text_data=json.dumps(
                    {
                        "message": msg["content"],
                        "username": msg["username"],
                    }
                )
            )
