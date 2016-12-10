from datetime import datetime, timedelta

import mongoengine
from flask_mongoengine import MongoEngine

from app.handlers import SliderHandler, ToggleHandler

db = MongoEngine()
# gpio_min_pin = app.config['GPIO_MIN_PIN']
# gpio_max_pin = app.config['GPIO_MAX_PIN']
gpio_min_pin = 2
gpio_max_pin = 27

# An LED uses around 0.01 kWh, which is 10 Wh, which in turn
# is 0.002777777778 Ws. Since the value in WidgetUsageEntry
# is expressed as a percentage (an int between 0 and 100),
# this number must be divided between 100.
K = 0.00002777777778



class WidgetUsageEntry(db.EmbeddedDocument):

	value = db.IntField(required=True, min_value=0, max_value=100)
	timestamp = db.DateTimeField(required=True, default=datetime.now)



class BaseWidget(db.Document):

	__type_registry = {}

	@classmethod
	def register_type(cls, widget_cls):
		cls.__type_registry[widget_cls.type] = widget_cls

	@classmethod
	def new_widget(cls, type, **kwargs):
		return cls.__type_registry[type](**kwargs)

	meta = {
		'allow_inheritance': True,
		'collection': 'widgets',
	}

	name = db.StringField(required=True)
	outpin = db.IntField(required=True, min_value=gpio_min_pin, max_value=gpio_max_pin)
	room = db.ReferenceField('Room', required=False)
	usages = db.ListField(db.EmbeddedDocumentField(WidgetUsageEntry))

	def __init__(self, *args, **kwargs):
		db.Document.__init__(self, *args, **kwargs)

		# Ensure BaseWidget is never instantiated
		if type(self) == BaseWidget:
			raise RuntimeError('BaseWidget cannot be instantiated')

	def to_dict(self):
		return {
			'id': str(self.id),
			'name': self.name,
			'value': self.value,
			'type': self.type,
			'room': self.room.to_dict(False) if self.room else None,
		}
	
	def get_usage_statistics(self, fr=None, to=None):
		one_day = timedelta(days=1)
		now = datetime.now()
		to = to if type(to) == datetime else now
		fr = fr if type(fr) == datetime else (to - timedelta(days=7))
		day_start = fr
		day_end = day_start + one_day
		usages = [u for u in self.usages]
		entries = []
		current = 0
		while day_start.date() <= to.date():
			for i in range(len(usages)):
				ts_start = usages[i].timestamp
				try:
					ts_end = usages[i+1].timestamp
				except IndexError:
					ts_end = now if now > ts_start else ts_start
				
				if ts_start <= day_end and ts_end >= day_start:
					if ts_start <= day_start and ts_end >= day_end:
						current += K * usages[i].value * (day_end - day_start).total_seconds()
					elif ts_start <= day_start and ts_end < day_end:
						current += K * usages[i].value * (ts_end - day_start).total_seconds()
					elif ts_start > day_start and ts_end >= day_end:
						current += K * usages[i].value * (day_end - ts_start).total_seconds()
					elif ts_start > day_start and ts_end < day_end:
						current += K * usages[i].value * (ts_end - ts_start).total_seconds()
			
			entries.append({'date': day_start.strftime('%Y-%m-%d'), 'usage': current})
			day_start = day_end
			day_end += one_day
			current = 0
		
		return {
			'widget': self.to_dict(),
			'from': fr.date().strftime('%Y-%m-%d'),
			'to': to.date().strftime('%Y-%m-%d'),
			'usages': entries
		}



class SliderWidget(BaseWidget):

	type = 'slider'
	value = db.IntField(required=True, default=0,
						min_value=0, max_value=100)

	def make_handler(self):
		return SliderHandler(self)

	def set_value(self, value):
		self.value = int(value)
		self.usages.append(WidgetUsageEntry(value=self.value))

BaseWidget.register_type(SliderWidget)



class ToggleWidget(BaseWidget):

	type = 'toggle'
	value = db.BooleanField(required=True, default=False)

	def make_handler(self):
		return ToggleHandler(self)

	def set_value(self, value):
		self.value = value in [1, '1', True, 'true']
		usage_entry_value = 100 if self.value else 0
		self.usages.append(WidgetUsageEntry(value=usage_entry_value))

BaseWidget.register_type(ToggleWidget)



class Room(db.Document):

	meta = {
		'collection': 'rooms',
	}

	name = db.StringField(required=True)
	widgets = db.ListField(db.ReferenceField('BaseWidget',
			reverse_delete_rule=mongoengine.NULLIFY))
	
	def to_dict(self, with_widgets=True):
		ret = {
			'id': str(self.id),
			'name': self.name,
		}
		if with_widgets:
			ret['widgets'] = [w.to_dict() for w in self.widgets]
		return ret
