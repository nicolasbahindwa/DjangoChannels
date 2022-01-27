from channels.db import database_sync_to_async
import json
from channels.consumer import SyncConsumer, AsyncConsumer
from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.models import User
from chatapp.models import Thread, Message


class EchoConsumer(SyncConsumer):

    def websocket_connect(self, event):
        # print("connect event is called")
        self.room_name = 'broadcast'
        self.send({
            'type': 'websocket.accept'
        })
        async_to_sync(self.channel_layer.group_add)(
            self.room_name, self.channel_name)
        print(f'[{self.channel_name }] - you are connected')

    def websocket_receive(self, event):
        # print("new event is received")
        print(f'[{self.channel_name }] - Received message [{event["text"]}')
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'websocket.message',
                'text': event.get('text')
            }
        )
        # print(event)
        # self.send({
        #     'type': 'websocket.send',
        #     'text': event.get('text')
        # })

    def websocket_message(self, event):
        print(f'[{self.channel_name }] - message sent {event["text"]}')
        self.send({
            'type': 'websocket.send',
            'text': event.get('text')
        })

    def websocket_disconnect(self, event):
        # print("disconnected")
        print(f'[{self.channel_name }] - disconnected {event["text"]}')
        async_to_sync(self.channel_layer.discard)(
            self.room_name, self.channel_name)
        print(event)


class ChatConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        # print("connect event is called")
        self.me = self.scope['user']
        # print('==============================' + str(self.me))
        other_username = self.scope['url_route']['kwargs']['username']
        # print('==============================' + str(other_username))
        othe_user = await sync_to_async(User.objects.get)(
                            username=other_username)
        # print('==============================' + str(othe_user))
        self.thread_obj = await sync_to_async(
            Thread.objects.get_or_create_personal_thread)(self.me, othe_user)
        # print(thread_obj)
        self.room_name = f'personala_thread_{self.thread_obj.id}'

        await self.channel_layer.group_add(
            self.room_name, self.channel_name)

        await self.send({
            'type': 'websocket.accept'
        })
        print(f'[{self.channel_name }] - you are connected')

    async def websocket_receive(self, event):
        # print("new event is received")
        print(f'[{self.channel_name }] - Received message {event["text"]}')
        msg = json.dumps({
            'text': event.get('text'),
            'username': self.scope['user'].username
        })

        await self.store_message(event.get('text'))
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'websocket.message',
                'text': msg
            }
        )
        # print(event)
        # self.send({
        #     'type': 'websocket.send',
        #     'text': event.get('text')
        # })

    async def websocket_message(self, event):
        print(f'[{self.channel_name }] - message sent [{event["text"]}')
        await self.send({
            'type': 'websocket.send',
            'text': event.get('text')
        })

    async def websocket_disconnect(self, event):
        # print("disconnected")
        print(f'[{self.channel_name }] - disconnected [{event["text"]}')
        await self.channel_layer.discard(
            self.room_name, self.channel_name)
        print(event)

    @database_sync_to_async
    def store_message(self, text):
        Message.objects.create(
            thread=self.thread_obj,
            sender=self.scope['user'],
            text=text
        )
