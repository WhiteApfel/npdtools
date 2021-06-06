from httpx._models import Response
import json


class FNSError(Exception):
	__module__ = "npdtools"

	def __init__(self, response: Response):
		self.status_code = response.status_code
		try:
			self.r_json = response.json()
			self.message = f"#{self.r_json['code']}: {self.r_json['message']}"
		except json.decoder.JSONDecodeError:
			self.message = response.text
		super().__init__(f"Ooops. HTTP_{self.status_code}. {self.message}")
