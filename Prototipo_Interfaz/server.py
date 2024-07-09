import json

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.wsgi
from tornado.options import define, options, parse_command_line

define('port', type=int, default=8012)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class NotMainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('control.html')

class AssetHandler(tornado.web.RequestHandler):
    def get(self, path):
        print(path)
        with open("assets/"+ path, 'rb') as f:
            self.write(f.read())

clients = []

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        global clients
        print('new connection')
        # self.write_message("Hello World")
        clients.append(self)
    
    def on_message(self, message):
        print('message received %s' % message)
        for client in clients:
            try:
                client.write_message(message)
            except tornado.websocket.WebSocketClosedError:
                pass

    def on_close(self):
        print('connection closed')
        clients.remove(self)

    def check_origin(self, origin):
        return True

def main():
    parse_command_line()
    app = tornado.web.Application([
        (r'/', MainHandler),
        (r'/control.html', NotMainHandler),
        (r'/ws', WSHandler),
        (r'/assets/(.*)', AssetHandler),
    ],
    static_path='.',
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
