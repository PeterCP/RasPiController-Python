# import RPi.GPIO as GPIO


# GPIO.setmode(GPIO.BOARD)


class HandlerManager:

	def __init__(self, widgets=[]):
		self.handlers = {}
		self.register_all(widgets)

	def __del__(self):
		for id in self.handlers:
			del self.handlers[id]
		del self.handlers

	def register(self, widget):
		handler = widget.make_handler()
		self.handlers[widget.id] = handler

	def register_all(self, widgets):
		for widget in widgets:
			self.register(widget)

	def delete(self, widget):
		del self.handlers[widget.id]

	def update(self, widget):
		if not self.handlers.get(widget.id, None):
			self.register(widget)
		self.handlers[widget.id].update(widget)



class ToggleHandler:

	def __init__(self, widget):
		# GPIO.setup(widget.outpin, GPIO.OUT, initial=widget.value)
		self.outpin = widget.outpin

	def __del__(self):
		# GPIO.cleanup(self.outpin)
		pass

	def update(self, widget):
		# GPIO.output(self.outpin, self.widget.value)
		pass



class SliderHandler:
	def __init__(self, widget):
		# self.outpin = widget.outpin
		# GPIO.setup(self.outpin, GPIO.OUT)
		# self.control = GPIO.PWM(self.outpin, 1000)
		# self.control.start(widget.value)
		pass

	def __del__(self):
		# self.control.stop()
		# GPIO.cleanup(self.outpin)
		pass

	def update(self, widget):
		# self.control.ChangeDutyCycle(widget.value)
		pass
