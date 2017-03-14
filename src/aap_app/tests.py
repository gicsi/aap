from django.test import TestCase
from models import LogGeneral, LOG_GENERAL_NIVEL_ERROR
from datetime import datetime

class AAPTests(TestCase):
	"""
	AAP tests cases
	"""

	def test_log(self):
		"""
		Testear que pueden registrarse logs...
		"""

		LogGeneral.objects.create(fechahora=datetime.now(), log="TEST LOG", detalle="", nivel=LOG_GENERAL_NIVEL_ERROR)
		log = LogGeneral.objects.get(pk=1)
		self.assertEqual("TEST LOG", log.log)


	# TODO: otros tests