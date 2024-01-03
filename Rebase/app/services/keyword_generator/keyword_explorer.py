# import requests
#
# class KeywordsExplorer:
#     def __init__(self, api_url):
#         self.api_url = api_url
#
#     def get_keywords(self, input_mes):
#         data = {'text': input_mes}
#         res = requests.post(self.api_url, json=data)
#         result = res.json()
#         return result

import google.generativeai as genai
from fastapi.encoders import jsonable_encoder


class GoogleGenerative:
	def __init__(self, api_key):
		self.api_key = api_key
		genai.configure(api_key=self.api_key)
		self.model = genai.GenerativeModel('gemini-pro')

	def generative(self, input_mes):
		try:
			response = self.model.generate_content(f"Tôi cần phân tích những keyword dành cho ngành công nghệ thông tin và tôi muốn đầu ra chỉ là keyword cách nhau bởi dấu , từ đoạn văn sau : {input_mes}")
			result = response.text.split(', ')
			return result
		except Exception as e:
			return {"status_code": 500, "detail": str(e)}


