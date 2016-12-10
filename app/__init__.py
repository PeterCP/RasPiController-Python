from flask import Flask

from app.handlers import HandlerManager
from app.models import db, BaseWidget

class App(Flask):

	def __init__(self, *args, **kwargs):
		Flask.__init__(self, *args, **kwargs)
		self.config.from_object('config')
		db.init_app(self)
		self.handler_manager = HandlerManager()
		self.handler_manager.register_all(BaseWidget.objects.all())

app = App('raspi-gpio-control')
from app.routes import *
app.register_blueprint(api)
