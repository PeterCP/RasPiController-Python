from flask_script import Manager, Server

from app import app

manager = Manager(app)
manager.add_command('runserver', Server(host='0.0.0.0', port=8000))

@manager.command
def seed():
	"""Save mock widgets to the datastore."""
	from app.models import BaseWidget, SliderWidget, ToggleWidget
	# RawWidget(name='Raw Widget', value='Value').save()
	BaseWidget.objects.delete()
	SliderWidget(name='SliderWidget', value=50, outpin=2).save()
	ToggleWidget(name='Toggle Widget', value=False, outpin=3).save()
	print('Mock widgets saved successfully!')

@manager.command
def loadtest():
	from app.models import BaseWidget, WidgetUsageEntry
	from datetime import datetime
	w = BaseWidget.objects.first()
	w.usages.clear()
	w.usages.append(WidgetUsageEntry(value=100, timestamp=datetime(2016, 12, 10, 12)))
	w.usages.append(WidgetUsageEntry(value=0, timestamp=datetime(2016, 12, 10, 13)))
	w.usages.append(WidgetUsageEntry(value=100, timestamp=datetime(2016, 12, 10, 23)))
	w.usages.append(WidgetUsageEntry(value=0, timestamp=datetime(2016, 12, 11, 1)))
	w.usages.append(WidgetUsageEntry(value=100, timestamp=datetime(2016, 12, 11, 23)))
	w.usages.append(WidgetUsageEntry(value=0, timestamp=datetime(2016, 12, 13, 1)))
	w.save()

if __name__ == '__main__':
	manager.run()
