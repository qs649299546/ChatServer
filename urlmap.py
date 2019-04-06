from handlers import chat


urlpatterns = (
    (r'/api/1.0/chat/?', chat.ChatWebsocketHandler),
    (r'/api/1.0/chat_user/?', chat.ChatUserHandler),
    (r'/api/1.0/chat_history/?', chat.ChatHistoryHandler),
    (r'/api/1.0/chat/(?P<chat_id>[0-9]+)/ident/?', chat.ChatIdentHandler),
)
