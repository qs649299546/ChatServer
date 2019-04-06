import os
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.log import gen_log
from tornado.web import Application as BaseApplication
from tornado.options import define, options, parse_command_line
from raven.contrib.tornado import AsyncSentryClient

from handlers import NotFoundHandler
from settings import SETTINGS
from urlmap import urlpatterns


class Application(BaseApplication):
    def __init__(self, handlers=None, default_host='', transforms=None,
                 **settings):
        super().__init__(handlers=handlers, default_host=default_host,
                         transforms=transforms, **settings)

        self.sentry_client = AsyncSentryClient(SETTINGS.get('sentry_dsn'))


def make_app():
    define('host', default='127.0.0.1', type=str)
    define('port', default=1992, type=int)
    define('main_process', default=True, type=bool)
    define('debug', default=False, type=bool)
    parse_command_line()

    app = Application(
        handlers=urlpatterns,
        default_host=options.host,
        debug=options.debug,
        default_handler_class=NotFoundHandler,
        **SETTINGS
    )

    server = HTTPServer(app, xheaders=True)
    server.listen(options.port, options.host)
    gen_log.info('Listen: http://{0}:{1} Debug: {2} && MainProcess: {3}'.format(
        options.host,
        options.port,
        options.debug,
        options.main_process))

    import logging
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
    if options.debug:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    if options.main_process:
        # 主进程
        pass

    IOLoop.current().start()


if __name__ == '__main__':
    make_app()

