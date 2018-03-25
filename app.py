import cherrypy
from jinja2 import Environment, FileSystemLoader
import os
from .src import utils

# environment loader for html files
env = Environment(loader=FileSystemLoader('html'))


class ZerodhaTask(object):

    # index page
    @cherrypy.expose
    def index(self):
        template = env.get_template('index.html')
        return template.render(data=utils.get_top_10_list())

    # search page
    @cherrypy.expose
    def get_stock(self, stock_name):
        template = env.get_template('search.html')
        return template.render(stock=stock_name, item=utils.get_stock_by_name(stock_name))


# server and directories configuration
path = os.path.abspath(os.path.dirname(__file__))
config = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', 5000))
    },
    '/assests': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(path, 'assests')
    },
    '/css': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(path, 'css')
    }
    ,
    '/resources': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(path, 'resources')
    }

}

cherrypy.quickstart(ZerodhaTask(), '/', config=config)
