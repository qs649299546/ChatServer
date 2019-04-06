import copy
import json
import requests
from tornado.websocket import WebSocketHandler
from sqlalchemy import or_

from models.chat import UserMessage
from .base import BaseApiHandler
from settings import UPSTREAM


endpoint = 'message/user_message'


class ChatWebsocketHandler(BaseApiHandler, WebSocketHandler):
    connected_users = set()

    def check_origin(self, origin):
        return True

    def data_received(self, chunk):
        pass

    def open(self):
        token = None
        if "token" in self.request.arguments:
            token = self.get_argument('token')

        if not token:
            return None

        self.write_message('connect success administrator! + token:{}'.format(token))
        self.connected_users.add(self)

        self.token = token

        print("has connected {} users".format(len(self.connected_users)))

    def on_message(self, message):
        print("recieve" + message)

        token = self.get_argument('token')

        try:
            message = json.loads(message, encoding="utf-8")
        except Exception as e:
            raise None

        else:
            data = message.get("data")
            from_type = data.pop("from_type")
            to_token = data.pop("to_token")
            to_type = data.pop("to_type")

            if from_type == UserMessage.TYPE_PROPERTY:
                from_user = requests.get(
                    self._url_join(endpoint, UPSTREAM['p_domain']), token=token)

                if to_type == UserMessage.TYPE_PROPERTY:
                    to_user = requests.get(
                        self._url_join(endpoint, UPSTREAM['p_domain']), token=token)
                    self.user(token, from_user, to_token, to_user, data)

                if to_type == UserMessage.TYPE_INDUSTRY:
                    to_user = requests.get(
                        self._url_join(endpoint, UPSTREAM['indus_domain']), token=token)
                    self.user(token, from_user, to_token, to_user, data)

                if to_type == UserMessage.TYPE_LAWER:
                    to_user = requests.get(
                        self._url_join(endpoint, UPSTREAM['law_domain']), token=token)
                    self.user(token, from_user, to_token, to_user, data)

            if from_type == UserMessage.TYPE_INDUSTRY:
                param = {"token": token}
                response = requests.get(self._url_join(endpoint, UPSTREAM['indus_domain']), params=param)
                user_info = json.loads(response.content)
                from_user = user_info['data']

                if to_type == UserMessage.TYPE_PROPERTY:
                    to_user = requests.get(
                            self._url_join(endpoint, UPSTREAM['p_domain']), token=token)
                    self.user(token, from_user, to_token, to_user, data)

                if to_type == UserMessage.TYPE_INDUSTRY:
                    param = {"token": to_token}
                    response = requests.get(self._url_join(endpoint, UPSTREAM['indus_domain']), params=param)
                    user_info = json.loads(response.content)
                    to_user = user_info['data']
                    self.user(token, from_type, to_type, from_user, to_token, to_user, data)

                if to_type == UserMessage.TYPE_LAWER:
                    to_user = requests.get(
                        self._url_join(endpoint, UPSTREAM['law_domain']), token=token)
                    self.user(token, from_user, to_token, to_user, data)

            if from_type == UserMessage.TYPE_LAWER:
                from_user = requests.get(
                    self._url_join(endpoint, UPSTREAM['law_domain']), token=token)

                if to_type == UserMessage.TYPE_PROPERTY:
                    to_user = requests.get(
                        self._url_join(endpoint, UPSTREAM['p_domain']), token=token)
                    self.user(token, from_user, to_token, to_user, data)

                if to_type == UserMessage.TYPE_INDUSTRY:
                    to_user = requests.get(
                        self._url_join(endpoint, UPSTREAM['indus_domain']), token=token)
                    self.user(token, from_user, to_token, to_user, data)

                if to_type == UserMessage.TYPE_LAWER:
                    to_user = requests.get(
                        self._url_join(endpoint, UPSTREAM['law_domain']), token=token)
                    self.user(token, from_user, to_token, to_user, data)

    def on_close(self):
        self.connected_users.remove(self)

    def user(self, token, from_type, to_type, from_user, to_token, to_user, data):
        user_message = UserMessage()
        user_message.user_id = from_user.get('id')
        user_message.to_user_id = to_user.get('id')
        user_message.from_type = from_type
        user_message.from_name = from_user.get('name')
        user_message.to_type = to_type
        user_message.to_name = to_user.get('name')
        user_message.has_read = 0
        user_message.content = data.get("msg")
        temp_list = [token, to_token]
        temp_list.sort()
        user_message.ticket = temp_list
        self.db_session.add(user_message)

        self.db_session.commit()

        etc = {
            "id": user_message.id,
            "user_id": {
                "id": from_user.get('id'),
                "name": from_user.get('name'),
                "avatar": from_user.get('avatar')
            },
            "has_read": 0,
            "created_at": self.strtime2dt(UserMessage.created_at),
            "content": user_message.content,
            "ticket": user_message.ticket,
            "to_user_id": {
                "id": to_user.get('id'),
                "name": to_user.get('name'),
                "avatar": to_user.get('avatar')
            }
        }

        return_data = {'data': data, "etc": etc}
        return_data = self.return_json(return_data)

        self.write_message(return_data)
        for i in self.connected_users:
            sc_token = i.token
            if sc_token == to_token:
                if from_user and to_user:
                    self.write_message(return_data)


class ChatUserHandler(BaseApiHandler):
    def get(self):
        token = self.get_argument('token')

        user_message = self.db_session.query(
            UserMessage
        ).order_by(
            UserMessage.created_at.desc()
        ).all()

        m_list = []
        e_list = []

        for message in user_message:
            ticket = copy.copy(message.ticket)

            if ticket not in m_list:
                if token in ticket:

                    m_list.append(ticket)
                    e_list.append(message)

        return self.return_json({
            'status': 200,
            'message': '',
            'data': {
                'recruits': {
                    'items': [{
                        'id': item.id,
                        'from_name': item.from_name,
                        'from_type': item.from_type,
                        'from_token': item.from_token,
                        'to_name': item.to_name,
                        'to_type': item.to_type,
                        'to_token': item.to_token,
                        'create_at': self.dt2strtime(item.created_at)
                    } for item in e_list]
                }
            }
        })


class ChatHistoryHandler(BaseApiHandler):
    def get(self):
        token = self.get_argument('token')

        query = self.db_session.query(
            UserMessage
        ).filter(
            or_(UserMessage.from_token == token,
                UserMessage.to_token == token)
        )

        return self.return_json({
            'status': 200,
            'message': '',
            'data': {
                'recruits': {
                    'items': [{
                        'id': item.id,
                        'from_name': item.from_name,
                        'from_type': item.from_type,
                        'to_name': item.to_name,
                        'to_type': item.to_type,
                        'content': item.content,
                        'created_at': self.dt2strtime(item.created_at)
                    } for item in query]
                }
            }
        })


class ChatIdentHandler(BaseApiHandler):
    def get(self, chat_id):
        the_user_chat = self.db_session.query(
            UserMessage
        ).filter(
            UserMessage.id == chat_id
        ).first()

        user_message = self.db_session.query(
            UserMessage
        ).order_by(UserMessage.created_at.desc()).all()

        m_list = []
        for m in user_message:
            if m.ticket == the_user_chat.ticket:
                m_list.append(m)

        return self.return_json({
            'status': 200,
            'message': '',
            'data': {
                'message_list': {
                    'items': [{
                        'id': item.id,
                        'from_name': item.from_name,
                        'from_type': item.from_type,
                        'to_name': item.to_name,
                        'to_type': item.to_type,
                        'content': item.content,
                        'created_at': self.dt2strtime(item.created_at)
                    } for item in m_list]
                }
            }
        })
