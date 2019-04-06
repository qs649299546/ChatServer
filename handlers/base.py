import json
from datetime import datetime
from urllib.parse import urljoin

from sqlalchemy import event
from tornado.web import RequestHandler
from raven.contrib.tornado import SentryMixin

from lib.store import DB_Session
from lib.utils import filter_keys
from lib.date import FORMAT_DATETIME


__all__ = ['BaseApiHandler']


class UtilMixin:
    @classmethod
    def dt2strtime(cls, dt):
        return dt.strftime(FORMAT_DATETIME)

    @classmethod
    def strtime2dt(cls, strtime):
        return datetime.strptime(strtime, FORMAT_DATETIME)


class BaseHandler(RequestHandler, SentryMixin, UtilMixin):

    def initialize(self):
        pass

    @staticmethod
    def _url_join(endpoint, prop=None, law=None, indust=None):
        if prop:
            return urljoin(prop, endpoint)
        if law:
            return urljoin(law, endpoint)
        if indust:
            return urljoin(indust, endpoint)

    @property
    def db_session(self):
        if not hasattr(self, '_db_session'):
            self._db_session = DB_Session()
            self._need_close_db_session = True

            @event.listens_for(self._db_session, 'after_commit')
            def receive_after_commit(session):
                self._need_close_db_session = False

            @event.listens_for(self._db_session, 'after_begin')
            def receive_after_begin(session, transaction, connection):
                self._need_close_db_session = True

        return self._db_session

    def return_json(self, data, keys=None, **kwargs):
        ret = filter_keys(data, keys)
        if isinstance(data, dict):
            ret.update(kwargs)

        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.finish(json.dumps(ret, cls=json.JSONEncoder))

    def return_status(self, status=500, message='', **kwargs):
        self.return_json({
            'status': status,
            'message': message
        }, **kwargs)

    def on_finish(self):
        super().on_finish()

        if hasattr(self, '_db_session') and self._need_close_db_session:
            self._db_session.close()


class BaseApiHandler(BaseHandler):

    def options(self, *args, **kwargs):
        # 解决请求跨域问题
        # https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Access_control_CORS

        is_preflight_request = ('Access-Control-Request-Method' in self.request.headers or
                                'Access-Control-Allow-Headers' in self.request.headers)

        if is_preflight_request:
            self.add_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')

            # 设置缓存时间, 但这个时间可能小于浏览器允许的最大时间
            # http://stackoverflow.com/questions/23543719/cors-access-control-max-age-is-ignored
            self.add_header('Access-Control-Max-Age', 86400 * 10)  # 10天

        if 'Access-Control-Request-Headers' in self.request.headers:
            self.add_header('Access-Control-Allow-Headers', self.request.headers['Access-Control-Request-Headers'])

        self.finish()

    def finish(self, chunk=None):
        # 解决请求跨域问题

        if 'Origin' in self.request.headers:
            self.add_header('Access-Control-Allow-Origin', '*')

        super().finish(chunk)
