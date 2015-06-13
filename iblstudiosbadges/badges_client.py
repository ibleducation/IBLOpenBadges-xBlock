from importlib import import_module


class BadgesClient():

	backend = None

	def __init__(self, backend):
		
		backend_path = backend.split(".")

		the_class = backend_path[-1]
		del(backend_path[-1])

		the_module = ".".join(backend_path)

		module = import_module(the_module)
		object_class = getattr(module,the_class)

		#instantiate the object class, this is our actual connection object
		self.backend = object_class()


	def get_auth_token():
		pass

	def get_badge_data():
		pass

	def create_obj_badge():
		pass

	def check_earn_badge():
		pass

	def build_badge_preview():
		pass

	def get_award_result():
		pass

	def get_award_result_formatted():
		pass

	def build_badge_form():
		pass

	def set_form_data_to_award():
		pass

	def claim_and_award_single_badge():
		pass
