from functools import wraps
from datetime import datetime

from flask import Blueprint, jsonify, abort, request
from mongoengine.errors import ValidationError, DoesNotExist

from app import app
from app.models import BaseWidget, Room


def json_response(f):
	@wraps(f)
	def inner(*args, **kwargs):
		return jsonify(f(*args, **kwargs))
	return inner


api = Blueprint('api', __name__, url_prefix='/api')



# Widgets

@api.route('/widgets', methods=['GET'])
@json_response
def widgets_index():
	return [obj.to_dict() for obj in BaseWidget.objects.all()]

@api.route('/widgets', methods=['POST'])
@api.route('/widgets/create', methods=['GET'])
@json_response
def widgets_create():
	type = request.values['type']
	widget_args = {
		'name': request.values['name'],
		'outpin': request.values['outpin'],
	}

	room_id = request.values.get('room')
	if room_id is not None:
		try:
			widget_args['room'] = Room.objects.get(id=room_id)
		except ValidationError:
			abort(400, 'The provided room id is incorrect')
		except DoesNotExist:
			abort(400, 'The room does not exist')

	widget = BaseWidget.new_widget(type, **widget_args)
	widget.save()
	if widget_args['room']:
		widget_args['room'].widgets.append(widget)
		widget_args['room'].save()
	return widget.to_dict()

@api.route('/widgets/<id>', methods=['GET'])
@json_response
def widgets_show(id):
	return BaseWidget.objects.get_or_404(id=id).to_dict()	

@api.route('/widgets/<id>', methods=['PATCH'])
@api.route('/widgets/<id>/update', methods=['GET'])
@json_response
def widgets_update(id):
	value = request.values['value']
	
	widget = BaseWidget.objects.get_or_404(id=id)
	try:
		widget.set_value(value)
		widget.save()
		app.handler_manager.update(widget)
		return widget.to_dict()
	except (ValidationError, ValueError):
		abort(400, 'Invalid value')

@api.route('/widgets/<id>', methods=['DELETE'])
@api.route('/widgets/<id>/delete', methods=['GET'])
@json_response
def widgets_delete(id):
	widget = BaseWidget.objects.get_or_404(id=id)
	widget.delete()
	return widget.to_dict()

@api.route('/widgets/<id>/usage', methods=['GET'])
@json_response
def widgets_usage(id):
	fr = request.values.get('from', None)
	to = request.values.get('to', None)
	if fr is not None:
		fr = datetime.strptime(fr, '%Y-%m-%d')
	if to is not None:
		to = datetime.strptime(to, '%Y-%m-%d')
	return BaseWidget.objects.get_or_404(id=id).get_usage_statistics(fr=fr, to=to)
			# fr=datetime(2016, 12, 10), to=datetime(2016, 12, 13))



# Rooms

@api.route('/rooms', methods=['GET'])
@json_response
def rooms_index():
	return [r.to_dict() for r in Room.objects.all()]

@api.route('/rooms', methods=['POST'])
@api.route('/rooms/create', methods=['GET'])
@json_response
def rooms_create():
	name = request.values['name']
	room = Room(name=name)
	room.save()
	return room.to_dict()

@api.route('/rooms/<id>', methods=['GET'])
@json_response
def rooms_single(id):
	return Room.objects.get_or_404(id=id).to_dict()

@api.route('/rooms/<id>', methods=['DELETE'])
@api.route('/rooms/<id>/delete', methods=['GET'])
@json_response
def rooms_delete(id):
	room = Room.objects.get_or_404(id=id)
	room.delete()
	return room.to_dict(False)

@api.route('/rooms/<id>/usage', methods=['GET'])
@json_response
def rooms_usage(id):
	fr = request.values.get('from', None)
	to = request.values.get('to', None)
	if fr is not None:
		fr = datetime.strptime(fr, '%Y-%m-%d')
	if to is not None:
		to = datetime.strptime(to, '%Y-%m-%d')
	widgets = Room.objects.get_or_404(id=id).widgets
	usages = [w.get_usage_statistics(fr=fr, to=to) for w in widgets]
	return usages
