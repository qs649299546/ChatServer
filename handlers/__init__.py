import json

from tornado.web import RequestHandler


class NotFoundHandler(RequestHandler):
    def prepare(self):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        return self.finish(json.dumps({
            'status': 404,
            'message': 'Not Found'
        }))

