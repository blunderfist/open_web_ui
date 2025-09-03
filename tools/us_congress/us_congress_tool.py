"""
title: US Congress Bill Search
author: blunderfist
git_url: https://github.com/blunderfist/open_web_ui/blob/main/tools/us_congress/us_congress_tool.py
version: 1.0.0
description: This tool searches US Congress API
required_open_webui_version: 0.4.0
requirements: pydantic>=2.11.4,httpx>=0.28.1
licence: MIT
"""


import os
import datetime
import json
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import httpx
import asyncio


api_key = os.getenv("API_KEY_GOV")



class Tools:
	def __init__(self):
		"""Initialize the Tool."""
		self.api_key = api_key
		self.BASE_URL = "https://api.congress.gov/v3" # Base URL for the API
		self.format = 'application/json'

	async def call_api(
			self, __event_emitter__, 
			endpoint, 
			params=None, 
			msg = None
			) -> Dict[str, Any]:
		"""
		Calls the specified API endpoint with the given parameters.
		"""

		if endpoint is None:
			await __event_emitter__({
				"type": "status",
				"data": {"description": f"API call unsuccessful, model did not select an endpoint.", 
						"done": True, # Displayed while search is being run
						"hidden": False} # True removes message after chat compeletion
			})
			return {"error": "endpoint not supplied"}


		await __event_emitter__({
			"type": "status",
			"data": {"description": f"Searching for {msg}...", 
					 "done": False, # Displayed while search is being run
					 "hidden": True} # True removes message after chat compeletion
		})

		if params is None:
			params = {}
		params['format'] = self.format
		params['api_key'] = self.api_key

		async with httpx.AsyncClient(timeout = 10.0) as client:
			try:
				url = f"{self.BASE_URL}{endpoint}"
				response = await client.get(url, params = params)
				response.raise_for_status()  # Raises an error for non-2xx responses
				return response.json()  # Returns the parsed JSON
			except httpx.HTTPStatusError as exc:
				await __event_emitter__({
					"type": "status",
					"data": {"description": f"HTTP error: {exc.response.status_code}", "done": True}
				})
				return {"error": f"HTTP error: {exc.response.status_code}"}
			except httpx.RequestError as exc:
				await __event_emitter__({
					"type": "status",
					"data": {"description": f"Request error: {exc}", "done": True}
				})
				return {"error": f"Request error: {exc}"}


###########################################################################################
# Bills
###########################################################################################

	async def get_bills(
			self, __event_emitter__, 
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None, 
			sort: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Retrieves a list of bills.

		Args:
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.
			fromDateTime (str, optional):  Filters results to those created after this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): Filters results to those created before this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			sort (str, optional): The field to sort the results by. Value can be updateDate+asc or updateDate+desc. Defaults to None.

		Returns:
			dict: A dictionary containing the API response. Returns None if the fromDateTime or toDateTime is in the wrong format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if sort:
			params['sort'] = sort
		endpoint = "/bill"
		msg = "bills"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bills_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None, 
			sort: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Retrieves a list of bills for a specific Congress.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.
			fromDateTime (str, optional):  Filters results to those created after this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): Filters results to those created before this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			sort (str, optional): The field to sort the results by. Value can be updateDate+asc or updateDate+desc. Defaults to None.

		Returns:
			dict: A dictionary containing the API response. Returns None if the fromDateTime or toDateTime is in the wrong format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if sort:
			params['sort'] = sort
		endpoint = f"/bill/{congress}"
		msg = "bills by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bills_by_congress_billtype(
			self, __event_emitter__,
			congress: int, 
			bill_type: str, 
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None, 
			sort: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Retrieves a list of bills of a specific type for a specific Congress.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.
			fromDateTime (str, optional):  Filters results to those created after this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): Filters results to those created before this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			sort (str, optional): The field to sort the results by. Value can be updateDate+asc or updateDate+desc. Defaults to None.

		Returns:
			dict: A dictionary containing the API response. Returns None if the fromDateTime or toDateTime is in the wrong format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if sort:
			params['sort'] = sort
		endpoint = f"/bill/{congress}/{bill_type}"
		msg = "bill types"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bill_details(
			self, __event_emitter__,
			congress: int, 
			bill_type: str, 
			bill_number: int
			) -> Dict[str, Any]:
		"""
		Retrieves the details of a specific bill.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			bill_number (int): The bill’s assigned number. For example, the value can be 3076.

		Returns:
			dict: A dictionary containing the API response.
		"""
		params = {}
		endpoint = f"/bill/{congress}/{bill_type}/{bill_number}"
		msg = "bill details"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bill_actions(
			self, __event_emitter__,
			congress: int, 
			bill_type: str, 
			bill_number: int, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves the actions taken on a specific bill.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			bill_number (int): The bill’s assigned number. For example, the value can be 3076.
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.

		Returns:
			dict: A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/bill/{congress}/{bill_type}/{bill_number}/actions"
		msg = "bill actions"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bill_amendments(
			self, __event_emitter__,
			congress: int, 
			bill_type: str, 
			bill_number: int, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves the amendments to a specific bill.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			bill_number (int): The bill’s assigned number. For example, the value can be 3076.
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.

		Returns:
			dict: A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/bill/{congress}/{bill_type}/{bill_number}/amendments"
		msg = "bill ammendments"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bill_committees(
			self, __event_emitter__,
			congress: int, 
			bill_type: str, 
			bill_number: int, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves the committees to which a specific bill has been referred.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			bill_number (int): The bill’s assigned number. For example, the value can be 3076.
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.

		Returns:
			dict: A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/bill/{congress}/{bill_type}/{bill_number}/committees"
		msg = "bill committees"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bill_cosponsors(
			self, __event_emitter__,
			congress: int, 
			bill_type: str, 
			bill_number: int, 
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None, 
			sort: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Retrieves the cosponsors of a specific bill.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			bill_number (int): The bill’s assigned number. For example, the value can be 3076.
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.
			fromDateTime (str, optional):  Filters results to those created after this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): Filters results to those created before this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			sort (str, optional): The field to sort the results by. Value can be updateDate+asc or updateDate+desc. Defaults to None.

		Returns:
			dict: A dictionary containing the API response. Returns None if the fromDateTime or toDateTime is in the wrong format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if sort:
			params['sort'] = sort
		endpoint = f"/bill/{congress}/{bill_type}/{bill_number}/cosponsors"
		msg = "bill cosponsors"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bill_relatedbills(
			self, __event_emitter__
			, congress: int
			, bill_type: str
			, bill_number: int
			, offset: int = 0
			, limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves the bills related to a specific bill.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			bill_number (int): The bill’s assigned number. For example, the value can be 3076.
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.

		Returns:
			dict: A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/bill/{congress}/{bill_type}/{bill_number}/relatedbills"
		msg = "related bills"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bill_subjects(
			self, __event_emitter__
			,congress: int
			, bill_type: str
			, bill_number: int
			, offset: int = 0
			, limit: int = 10
			, fromDateTime: Optional[str] = None
			, toDateTime: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Retrieves the subjects of a specific bill.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			bill_number (int): The bill’s assigned number. For example, the value can be 3076.
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.
			fromDateTime (str, optional):  Filters results to those created after this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): Filters results to those created before this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.

		Returns:
			dict: A dictionary containing the API response. Returns None if the fromDateTime or toDateTime is in the wrong format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None

		endpoint = f"/bill/{congress}/{bill_type}/{bill_number}/subjects"
		msg = "bill subjects"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bill_summaries(
			self, __event_emitter__,
			congress: int, 
			bill_type: str, 
			bill_number: int, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves the summaries of a specific bill.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			bill_number (int): The bill’s assigned number. For example, the value can be 3076.
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.

		Returns:
			dict: A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/bill/{congress}/{bill_type}/{bill_number}/summaries"
		msg = "bill summaries"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bill_text(
			self, __event_emitter__,
			congress: int, 
			bill_type: str, 
			bill_number: int, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves the text of a specific bill.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			bill_number (int): The bill’s assigned number. For example, the value can be 3076.
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.

		Returns:
			dict: A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/bill/{congress}/{bill_type}/{bill_number}/text"
		msg = "bill text"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_bill_titles(
			self, __event_emitter__,
			congress: int, 
			bill_type: str, 
			bill_number: int, 
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Retrieves the titles of a specific bill.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			bill_type (str): The type of bill. Values mapped to types below. Can be hr, s, hjres, sjres, hconres, sconres, hres, or sres.
			    "House Bill (H.R.)": "hr"
				"Senate Bill (S.)": "s"
				"House Joint Resolution (H.J. Res.)": "hjres"
				"Senate Joint Resolution (S.J. Res.)": "sjres"
				"House Concurrent Resolution (H. Con. Res.)": "hconres"
				"Senate Concurrent Resolution (S. Con. Res.)": "sconres"
				"House Simple Resolution (H. Res.)": "hres"
				"Senate Simple Resolution (S. Res.)": "sres"
			bill_number (int): The bill’s assigned number. For example, the value can be 3076.
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.
			fromDateTime (str, optional):  Filters results to those created after this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): Filters results to those created before this date and time. Format: YYYY-MM-DDT00:00:00Z. Defaults to None.

		Returns:
			dict: A dictionary containing the API response. Returns None if the fromDateTime or toDateTime is in the wrong format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		endpoint =  f"/bill/{congress}/{bill_type}/{bill_number}/titles"
		msg = "bill titles"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_laws_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves a list of laws for a specific Congress.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.

		Returns:
			dict: A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/law/{congress}"
		return await self.call_api(__event_emitter__, endpoint, params)

	async def get_laws_by_congress_lawtype(
			self, __event_emitter__,
			congress: int, 
			law_type: str, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves a list of laws of a specific type for a specific Congress.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			law_type (str): The type of law.
			offset (int, optional): The starting position of the results. Defaults to 0.
			limit (int, optional): The maximum number of results to return. Defaults to 10.

		Returns:
			dict: A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/law/{congress}/{law_type}"
		msg = "congress law type"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_law_details(
			self, __event_emitter__,
			congress: int, 
			law_type: str, 
			law_number: int
			) -> Dict[str, Any]:
		"""
		Retrieves the details of a specific law.

		Args:
			congress (int): The number of the Congress (e.g., 118).
			law_type (str): The type of law.
			law_number (int): The number of the law (e.g., 1).

		Returns:
			dict: A dictionary containing the API response.
		"""
		params = {}
		endpoint = f"/law/{congress}/{law_type}/{law_number}"
		msg = "law details"
		return await self.call_api(__event_emitter__, endpoint, params, msg)


###########################################################################################
# Ammendments
###########################################################################################

	async def get_amendments(
			self, __event_emitter__,
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Retrieves a list of amendments from the API.

		Args:
			offset: The offset for pagination. Defaults to 0.
			limit: The maximum number of results to return. Defaults to 10.
			fromDateTime: Filter amendments created after this datetime (YYYY-MM-DDTHH:MM:SSZ). Defaults to None.
			toDateTime: Filter amendments created before this datetime (YYYY-MM-DDTHH:MM:SSZ). Defaults to None.

		Returns:
			A dictionary containing the API response, or None if there is an error in the date format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		endpoint = "/amendment"
		msg = "ammendments"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_amendments_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Retrieves a list of amendments for a specific congress from the API.

		Args:
			congress: The congress number (e.g., 117).
			offset: The offset for pagination. Defaults to 0.
			limit: The maximum number of results to return. Defaults to 10.
			fromDateTime: Filter amendments created after this datetime (YYYY-MM-DDTHH:MM:SSZ). Defaults to None.
			toDateTime: Filter amendments created before this datetime (YYYY-MM-DDTHH:MM:SSZ). Defaults to None.

		Returns:
			A dictionary containing the API response, or None if there is an error in the date format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		endpoint = f"/amendment/{congress}"
		msg = "ammendments by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_amendments_by_congress_amendmenttype(
			self, __event_emitter__,
			congress: int, 
			amendment_type: str, 
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Retrieves a list of amendments for a specific congress and amendment type from the API.

		Args:
			congress: The congress number (e.g., 117).
			amendment_type: The type of amendment (e.g., 's', 'hr').
			offset: The offset for pagination. Defaults to 0.
			limit: The maximum number of results to return. Defaults to 10.
			fromDateTime: Filter amendments created after this datetime (YYYY-MM-DDTHH:MM:SSZ). Defaults to None.
			toDateTime: Filter amendments created before this datetime (YYYY-MM-DDTHH:MM:SSZ). Defaults to None.

		Returns:
			A dictionary containing the API response, or None if there is an error in the date format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		endpoint = f"/amendment/{congress}/{amendment_type}"
		msg = "ammendments by type"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_amendment_details(
			self, __event_emitter__,
			congress: int, 
			amendment_type: str, 
			amendment_number: int
			) -> Dict[str, Any]:
		"""
		Retrieves details for a specific amendment from the API.

		Args:
			congress: The congress number (e.g., 117).
			amendment_type: The type of amendment (e.g., 's', 'hr').
			amendment_number: The amendment number (e.g., 1).

		Returns:
			A dictionary containing the API response.
		"""
		params = {}
		endpoint = f"/amendment/{congress}/{amendment_type}/{amendment_number}"
		msg = "ammendment details"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_amendment_actions(
			self, __event_emitter__,
			congress: int, 
			amendment_type: str, 
			amendment_number: int, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves the actions taken on a specific amendment from the API.

		Args:
			congress: The congress number (e.g., 117).
			amendment_type: The type of amendment (e.g., 's', 'hr').
			amendment_number: The amendment number (e.g., 1).
			offset: The offset for pagination. Defaults to 0.
			limit: The maximum number of results to return. Defaults to 10.

		Returns:
			A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/amendment/{congress}/{amendment_type}/{amendment_number}/actions"
		msg = "ammendment actions"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_amendment_cosponsors(
			self, __event_emitter__,
			congress: int, 
			amendment_type: str, 
			amendment_number: int, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves the cosponsors of a specific amendment from the API.

		Args:
			congress: The congress number (e.g., 117).
			amendment_type: The type of amendment (e.g., 's', 'hr').
			amendment_number: The amendment number (e.g., 1).
			offset: The offset for pagination. Defaults to 0.
			limit: The maximum number of results to return. Defaults to 10.

		Returns:
			A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/amendment/{congress}/{amendment_type}/{amendment_number}/cosponsors"
		msg = "ammendment cosponsors"
		return await self.call_api(__event_emitter__, endpoint, params, msg)
	
	async def get_amendment_amendments(
			self, __event_emitter__,
			congress: int, 
			amendment_type: str, 
			amendment_number: int, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves the amendments related to a specific amendment from the API.

		Args:
			congress: The congress number (e.g., 117).
			amendment_type: The type of amendment (e.g., 's', 'hr').
			amendment_number: The amendment number (e.g., 1).
			offset: The offset for pagination. Defaults to 0.
			limit: The maximum number of results to return. Defaults to 10.

		Returns:
			A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/amendment/{congress}/{amendment_type}/{amendment_number}/amendments"
		msg = "ammendments"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_amendment_text(
			self, __event_emitter__,
			congress: int, 
			amendment_type: str, 
			amendment_number: int, 
			offset: int = 0, 
			limit: int = 10
			) -> Dict[str, Any]:
		"""
		Retrieves the text of a specific amendment from the API.
		Note: This endpoint is for the 117th Congress and onwards.

		Args:
			congress: The congress number (e.g., 117).
			amendment_type: The type of amendment (e.g., 's', 'hr').
			amendment_number: The amendment number (e.g., 1).
			offset: The offset for pagination. Defaults to 0.
			limit: The maximum number of results to return. Defaults to 10.

		Returns:
			A dictionary containing the API response.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		endpoint = f"/amendment/{congress}/{amendment_type}/{amendment_number}/text"
		msg = "ammendment text"
		return await self.call_api(__event_emitter__, endpoint, params, msg)



###########################################################################################
# Summaries
###########################################################################################

	async def get_summaries(
			self, __event_emitter__,
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None, 
			sort: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Calls the /summaries endpoint and returns the data.

		Args:
			offset (int): The offset to start the data from. Defaults to 0.
			limit (int): The limit of the data to return. Defaults to 10.
			fromDateTime (Optional[str]): The start date and time to filter the data from, in the format YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (Optional[str]): The end date and time to filter the data to, in the format YYYY-MM-DDT00:00:00Z. Defaults to None.
			sort (Optional[str]): The field to sort the data by. Value can be updateDate+asc or updateDate+desc. Defaults to None.

		Returns:
			Optional[Dict[str, Any]]: The data returned from the /summaries endpoint, or None if there is an error with the date format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if sort:
			params['sort'] = sort
		endpoint = "/summaries"
		msg = "summaries"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_summaries_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None, 
			sort: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Calls the /summaries/{congress} endpoint and returns the data.

		Args:
			congress (int): The congress number to filter the data by.
			offset (int): The offset to start the data from. Defaults to 0.
			limit (int): The limit of the data to return. Defaults to 10.
			fromDateTime (Optional[str]): The start date and time to filter the data from, in the format YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (Optional[str]): The end date and time to filter the data to, in the format YYYY-MM-DDT00:00:00Z. Defaults to None.
			sort (Optional[str]): The field to sort the data by. Value can be updateDate+asc or updateDate+desc. Defaults to None.

		Returns:
			Optional[Dict[str, Any]]: The data returned from the /summaries/{congress} endpoint, or None if there is an error with the date format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if sort:
			params['sort'] = sort
		endpoint = f"/summaries/{congress}"
		msg = "summaries by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_summaries_by_congress_billtype(
			self, __event_emitter__,
			congress: int, 
			bill_type: str, 
			offset: int = 0, 
			limit: int = 10, 
			fromDateTime: Optional[str] = None, 
			toDateTime: Optional[str] = None, 
			sort: Optional[str] = None
			) -> Dict[str, Any]:
		"""
		Calls the /summaries/{congress}/{billType} endpoint and returns the data.

		Args:
			congress (int): The congress number to filter the data by.
			bill_type (str): The bill type to filter the data by.
			offset (int): The offset to start the data from. Defaults to 0.
			limit (int): The limit of the data to return. Defaults to 10.
			fromDateTime (Optional[str]): The start date and time to filter the data from, in the format YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (Optional[str]): The end date and time to filter the data to, in the format YYYY-MM-DDT00:00:00Z. Defaults to None.
			sort (Optional[str]): The field to sort the data by. Value can be updateDate+asc or updateDate+desc. Defaults to None.

		Returns:
			Optional[Dict[str, Any]]: The data returned from the /summaries/{congress}/{billType} endpoint, or None if there is an error with the date format.
		"""
		params = {}
		params['offset'] = offset
		params['limit'] = limit
		if fromDateTime:
			try:
				datetime.datetime.strptime(fromDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['fromDateTime'] = fromDateTime
			except ValueError:
				print("Incorrect fromDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if toDateTime:
			try:
				datetime.datetime.strptime(toDateTime, '%Y-%m-%dT%H:%M:%SZ')
				params['toDateTime'] = toDateTime
			except ValueError:
				print("Incorrect toDateTime format, should be YYYY-MM-DDT00:00:00Z")
				return None
		if sort:
			params['sort'] = sort
		endpoint = f"/summaries/{congress}/{bill_type}"
		msg = "summaries by bill type"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

###########################################################################################
# Congress
###########################################################################################

	async def get_congress_list(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns a list of congresses and congressional sessions.

		Args:
			offset: The offset for pagination. Defaults to None.
			limit: The maximum number of results to return. Defaults to None.

		Returns:
			A dictionary containing the list of congresses.
		"""
		endpoint = "/congress"
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		msg = "congress list"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_congress(
			self, __event_emitter__,
			congress_number: int
			) -> Dict[str, Any]:
		"""
		Returns detailed information for a specified congress.

		Args:
			congress_number: The number of the congress to retrieve.

		Returns:
			A dictionary containing the details of the specified congress.
		"""
		params = {}
		endpoint = f"/congress/{congress_number}"
		msg = "congress information"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_current_congress(
			self, __event_emitter__ ,
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns detailed information for the current congress.

		Args:
			offset: The offset for pagination. Defaults to None.
			limit: The maximum number of results to return. Defaults to None.

		Returns:
			A dictionary containing the details of the current congress.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = "/congress/current"
		msg = "current congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)
	
###########################################################################################
# Members
###########################################################################################

	async def get_members(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None, 
			currentMember: bool = None
			) -> Dict[str, Any]:
		"""
		Returns a list of congressional members.

		Args:
			offset: The offset for pagination. Defaults to None.
			limit: The maximum number of results to return. Defaults to None.
			fromDateTime: filter members from a certain date. Defaults to None.
			toDateTime: Filter members to a certain date. Defaults to None.
			currentMember: Filter to include only current members. The status of the member. Use true or false. Use currentMember=True for the current congress data only. Defaults to None.

		Returns:
			A dictionary containing the list of congressional members.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		if currentMember:
			params['currentMember'] = currentMember
		
		endpoint = "/member"
		msg = "members"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_member_by_bioguide(
			self, __event_emitter__,
			bioguideId: str
			) -> Dict[str, Any]:
		"""
		Returns detailed information for a specified congressional member.

		Args:
			bioguideId: The bioguide ID of the member to retrieve.

		Returns:
			A dictionary containing the details of the specified congressional member.
		"""
		params = {}
		endpoint = f"/member/{bioguideId}"
		msg = "member bios"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_sponsored_legislation(
			self, __event_emitter__,
			bioguideId: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns the list of legislation sponsored by a specified congressional member.

		Args:
			bioguideId: The bioguide ID of the member.
			offset: The offset for pagination. Defaults to None.
			limit: The maximum number of results to return. Defaults to None.

		Returns:
			A dictionary containing the list of sponsored legislation.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/member/{bioguideId}/sponsored-legislation"
		msg = "sponsored legislation"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_cosponsored_legislation(
			self, __event_emitter__,
			bioguideId: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns the list of legislation cosponsored by a specified congressional member.

		Args:
			bioguideId: The bioguide ID of the member.
			offset: The offset for pagination. Defaults to None.
			limit: The maximum number of results to return. Defaults to None.

		Returns:
			A dictionary containing the list of cosponsored legislation.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/member/{bioguideId}/cosponsored-legislation"
		msg = "cosponsored legislation"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_members_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = None, 
			currentMember: bool = None
			) -> Dict[str, Any]:
		"""
		Returns the list of members specified by Congress

		Args:
			congress: The congress number.
			offset: The offset for pagination. Defaults to None.
			limit: The maximum number of results to return. Defaults to None.
			currentMember: Filter to include only current members. The status of the member. Use true or false. Use currentMember=True for the current congress data only. Defaults to None.

		Returns:
			A dictionary containing the list of members.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if currentMember:
			params['currentMember'] = currentMember
		endpoint = f"/member/congress/{congress}"
		msg = "members specified by Congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_members_by_state(
			self, __event_emitter__,
			stateCode: str, 
			limit: int = None, 
			currentMember: bool = None
			) -> Dict[str, Any]:
		"""
		Returns a list of members filtered by state.

		Args:
			stateCode: The two-letter state code (e.g., 'CA', 'NY').
			limit: The maximum number of results to return. Defaults to None.
			currentMember: Filter to include only current members. The status of the member. Use true or false. Use currentMember=True for the current congress data only. Defaults to None.

		Returns:
			A dictionary containing the list of members.
		"""
		params = {}
		if limit:
			params['limit'] = limit
		if currentMember:
			params['currentMember'] = currentMember
		endpoint = f"/member/{stateCode}"
		msg = "members by state"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_members_by_state_district(
			self, __event_emitter__,
			stateCode: str, 
			district: int, 
			currentMember: bool = None
			) -> Dict[str, Any]:
		"""
		Returns a list of members filtered by state and district.

		Args:
			stateCode: The two-letter state code (e.g., 'CA', 'NY').
			district: The district number.
			currentMember: Filter to include only current members. The status of the member. Use true or false. Use currentMember=True for the current congress data only. Defaults to None.

		Returns:
			A dictionary containing the list of members.
		"""
		params = {}
		if currentMember:
			params['currentMember'] = currentMember
		endpoint = f"/member/{stateCode}/{district}"
		msg = "members by district"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_members_by_congress_state_district(
			self, __event_emitter__,
			congress: int, 
			stateCode: str, 
			district: int, 
			currentMember: bool = None
			) -> Dict[str, Any]:
		"""
		Returns a list of members filtered by congress, state and district.

		Args:
			congress: The congress number.
			stateCode: The two-letter state code (e.g., 'CA', 'NY').
			district: The district number.
			currentMember: Filter to include only current members. The status of the member. Use true or false. Use currentMember=True for the current congress data only. Defaults to None.

		Returns:
			A dictionary containing the list of members.
		"""
		params = {}
		if currentMember:
			params['currentMember'] = currentMember
		endpoint = f"/member/congress/{congress}/{stateCode}/{district}"
		msg = "members by state district"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

###########################################################################################
# Committees
###########################################################################################

	async def get_committees(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:
		"""
		Returns a list of congressional committees.

		Args:
			offset (int, optional): The offset for pagination. Defaults to None.
			limit (int, optional): The limit for pagination. Defaults to None.
			fromDateTime (str, optional): The start date for filtering. Defaults to None.
			toDateTime (str, optional): The end date for filtering. Defaults to None.

		Returns:
			The response from the API call.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = "/committee"
		msg = "committees"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committees_by_chamber(
			self, __event_emitter__,
			chamber: str, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:
		"""
		Returns a list of congressional committees filtered by the specified chamber.

		Args:
			chamber (str): The chamber to filter by.
			offset (int, optional): The offset for pagination. Defaults to None.
			limit (int, optional): The limit for pagination. Defaults to None.
			fromDateTime (str, optional): The start date for filtering. Defaults to None.
			toDateTime (str, optional): The end date for filtering. Defaults to None.

		Returns:
			The response from the API call.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee/{chamber}"
		msg = "committees by chamber"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committees_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:
		"""
		Returns a list of congressional committees filtered by the specified congress.

		Args:
			congress (int): The congress to filter by.
			offset (int, optional): The offset for pagination. Defaults to None.
			limit (int, optional): The limit for pagination. Defaults to None.
			fromDateTime (str, optional): The start date for filtering. Defaults to None.
			toDateTime (str, optional): The end date for filtering. Defaults to None.

		Returns:
			The response from the API call.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee/{congress}"
		msg = "committees by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committees_by_congress_and_chamber(
			self, __event_emitter__,
			congress: int, 
			chamber: str, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:
		"""
		Returns a list of committees filtered by the specified congress and chamber.

		Args:
			congress (int): The congress to filter by.
			chamber (str): The chamber to filter by.
			offset (int, optional): The offset for pagination. Defaults to None.
			limit (int, optional): The limit for pagination. Defaults to None.
			fromDateTime (str, optional): The start date for filtering. Defaults to None.
			toDateTime (str, optional): The end date for filtering. Defaults to None.

		Returns:
			The response from the API call.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee/{congress}/{chamber}"
		msg = "committees by congress and chamber"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_details(
			self, __event_emitter__,
			chamber: str, 
			committeeCode: str
			) -> Dict[str, Any]:
		"""
		Returns detailed information for a specified congressional committee.

		Args:
			chamber (str): The chamber of the committee.
			committeeCode (str): The code of the committee.

		Returns:
			The response from the API call.
		"""
		params = {}
		endpoint = f"/committee/{chamber}/{committeeCode}"
		msg = "committee details"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_bills(
			self, __event_emitter__,
			chamber: str, 
			committeeCode: str, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:
		"""
		Returns the list of legislation associated with the specified congressional committee.

		Args:
			chamber (str): The chamber of the committee.
			committeeCode (str): The code of the committee.
			offset (int, optional): The offset for pagination. Defaults to None.
			limit (int, optional): The limit for pagination. Defaults to None.
			fromDateTime (str, optional): The start date for filtering. Defaults to None.
			toDateTime (str, optional): The end date for filtering. Defaults to None.

		Returns:
			The response from the API call.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee/{chamber}/{committeeCode}/bills"
		msg = "committee bills"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_reports(
			self, __event_emitter__,
			chamber: str, 
			committeeCode: str, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:
		"""
		Returns the list of committee reports associated with a specified congressional committee.

		Args:
			chamber (str): The chamber of the committee.
			committeeCode (str): The code of the committee.
			offset (int, optional): The offset for pagination. Defaults to None.
			limit (int, optional): The limit for pagination. Defaults to None.
			fromDateTime (str, optional): The start date for filtering. Defaults to None.
			toDateTime (str, optional): The end date for filtering. Defaults to None.

		Returns:
			The response from the API call.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee/{chamber}/{committeeCode}/reports"
		msg = "committee reports"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_nominations(
			self, __event_emitter__,
			chamber: str, 
			committeeCode: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns the list of nominations associated with a specified congressional committee.

		Args:
			chamber (str): The chamber of Congress ('house' or 'senate').
			committeeCode (str): The code of the committee (e.g., 'HSFA' for House Foreign Affairs).
			format (str, optional): The desired format of the response ('xml' or 'json'). Defaults to None (json).
			offset (int, optional): The starting record number for pagination. Defaults to None (start from the beginning).
			limit (int, optional): The maximum number of records to return. Defaults to None (API default).

		Returns:
			dict: A dictionary containing the list of nominations, or None if the API call fails.

		Example Usage:
		```python
		tools = Tools()
		nominations = tools.get_committee_nominations(chamber="senate", committeeCode="SSBK", limit=5)
		if nominations:
			print(nominations)
		else:
			print("Failed to retrieve committee nominations.")
		```
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/committee/{chamber}/{committeeCode}/nominations"
		msg = "committee nominations"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_house_communications(
			self, __event_emitter__,
			chamber: str, 
			committeeCode: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns the list of House communications associated with a specified congressional committee.

		Args:
			chamber (str): The chamber of Congress ('house' or 'senate').
			committeeCode (str): The code of the committee (e.g., 'HSFA' for House Foreign Affairs).
			format (str, optional): The desired format of the response ('xml' or 'json'). Defaults to None (json).
			offset (int, optional): The starting record number for pagination. Defaults to None (start from the beginning).
			limit (int, optional): The maximum number of records to return. Defaults to None (API default).

		Returns:
			dict: A dictionary containing the list of House communications, or None if the API call fails.

		Example Usage:
		```python
		tools = Tools()
		communications = tools.get_committee_house_communications(chamber="house", committeeCode="HSFA", limit=5)
		if communications:
			print(communications)
		else:
			print("Failed to retrieve House communications.")
		```
		"""
		params = {}		
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/committee/{chamber}/{committeeCode}/house-communication"
		msg = "House communications associated with a specified congressional committee"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_senate_communications(
			self, __event_emitter__,
			chamber: str, 
			committeeCode: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns the list of Senate communications associated with a specified congressional committee.

		Args:
			chamber (str): The chamber of Congress ('house' or 'senate').
			committeeCode (str): The code of the committee (e.g., 'SSBK' for Senate Banking, Housing, and Urban Affairs).
			format (str, optional): The desired format of the response ('xml' or 'json'). Defaults to None (json).
			offset (int, optional): The starting record number for pagination. Defaults to None (start from the beginning).
			limit (int, optional): The maximum number of records to return. Defaults to None (API default).

		Returns:
			dict: A dictionary containing the list of Senate communications, or None if the API call fails.

		Example Usage:
		```python
		tools = Tools()
		communications = tools.get_committee_senate_communications(chamber="senate", committeeCode="SSBK", limit=5)
		if communications:
			print(communications)
		else:
			print("Failed to retrieve Senate communications.")
		```
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/committee/{chamber}/{committeeCode}/senate-communication"
		msg = "Senate communications associated with a specified congressional committee"
		return await self.call_api(__event_emitter__, endpoint, params, msg)


###########################################################################################
# Committee report
###########################################################################################

	async def get_committee_reports(
			self, __event_emitter__ , 
			conference: str = None, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Returns a list of committee reports.
		Args:
			conference (str, optional): Flag to indicate conference reports. Value can be true or false. Defaults to None.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
		Returns:
			dict: A dictionary containing the committee reports, or None if the API call fails.
		Example Usage:
		```python
		tools = Tools()
		reports = tools.get_committee_reports(conference="true", limit=10)
		if reports:
			print(reports)
		else:
			print("Failed to retrieve committee reports.")
		```
		"""
		params = {}
		if conference:
			params['conference'] = conference
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = "/committee-report"
		msg = "committee reports"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_reports_by_congress(
			self, __event_emitter__,
			congress: int, 
			conference: str = None, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Returns a list of committee reports filtered by the specified congress.
		Args:
			congress (int): The congress number. For example, the value can be 116.
			conference (str, optional): Flag to indicate conference reports. Value can be true or false. Defaults to None.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
		Returns:
			dict: A dictionary containing the committee reports, or None if the API call fails.
		Example Usage:
		```python
		tools = Tools()
		reports = tools.get_committee_reports_by_congress(congress=116, conference="true", limit=10)
		if reports:
			print(reports)
		else:
			print("Failed to retrieve committee reports.")
		```
		"""
		params = {}
		if conference:
			params['conference'] = conference
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee-report/{congress}"
		msg = "committee reports by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_reports_by_congress_and_type(
			self, __event_emitter__,
			congress: int, 
			reportType: str, 
			conference: str = None, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Returns a list of committee reports filtered by the specified congress and report type.
		Args:
			congress (int): The congress number. For example, the value can be 116.
			reportType (str): The type of committee report. Value can be hrpt, srpt, or erpt.
			conference (str, optional): Flag to indicate conference reports. Value can be true or false. Defaults to None.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
		Returns:
			dict: A dictionary containing the committee reports, or None if the API call fails.
		Example Usage:
		```python
		tools = Tools()
		reports = tools.get_committee_reports_by_congress_and_type(congress=116, reportType="hrpt", conference="true", limit=10)
		if reports:
			print(reports)
		else:
			print("Failed to retrieve committee reports.")
		```
		"""
		params = {}
		if conference:
			params['conference'] = conference
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee-report/{congress}/{reportType}"
		msg = "committee reports by congress and type"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_report_details(
			self, __event_emitter__,
			congress: int, 
			reportType: str, 
			reportNumber: int
			) -> Dict[str, Any]:

		"""
		Returns detailed information for a specified committee report.
		Args:
			congress (int): The congress number. For example, the value can be 116.
			reportType (str): The type of committee report. Value can be hrpt, srpt, or erpt.
			reportNumber (int): The committee report’s assigned number. For example, the value can be 617.
			
		Returns:
			dict: A dictionary containing the details of the committee report, or None if the API call fails.
		Example Usage:
		```python
		tools = Tools()
		report_details = tools.get_committee_report_details(congress=116, reportType="hrpt", reportNumber=617)
		if report_details:
			print(report_details)
		else:
			print("Failed to retrieve committee report details.")
		```
		"""
		params = {}
		endpoint = f"/committee-report/{congress}/{reportType}/{reportNumber}"
		msg = "committee report details"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_report_text(
			self, __event_emitter__,
			congress: int, 
			reportType: str, 
			reportNumber: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Returns the list of texts for a specified committee report.
		Args:
			congress (int): The congress number. For example, the value can be 116.
			reportType (str): The type of committee report. Value can be hrpt, srpt, or erpt.
			reportNumber (int): The committee report’s assigned number. For example, the value can be 617.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
		Returns:
			dict: A dictionary containing the text formats and URLs for the committee report, or None if the API call fails.
		Example Usage:
		```python
		tools = Tools()
		report_text = tools.get_committee_report_text(congress=116, reportType="hrpt", reportNumber=617)
		if report_text:
			print(report_text)
		else:
			print("Failed to retrieve committee report text.")
		```
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/committee-report/{congress}/{reportType}/{reportNumber}/text"
		msg = "committee report text"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

###########################################################################################
# Committee print
###########################################################################################



	async def get_committee_prints(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Returns a list of committee prints.

		Args:
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.

		Returns:
			dict: A dictionary containing the committee prints, or None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = "/committee-print"
		msg = "committee prints"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_prints_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Returns a list of committee prints filtered by the specified congress.

		Args:
			congress (int): The congress number. For example, the value can be 117.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.

		Returns:
			dict: A dictionary containing the committee prints, or None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee-print/{congress}"
		msg = "committee prints by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_prints_by_congress_and_chamber(
			self, __event_emitter__,
			congress: int, 
			chamber: str, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Returns a list of committee prints filtered by the specified congress and chamber.

		Args:
			congress (int): The congress number. For example, the value can be 117.
			chamber (str): The chamber name. Value can be house, senate, or nochamber.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.

		Returns:
			dict: A dictionary containing the committee prints, or None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee-print/{congress}/{chamber}"
		msg = "committee prints by congress and chamber"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_print_details(
			self, __event_emitter__,
			congress: int, 
			chamber: str, 
			jacketNumber: int
			) -> Dict[str, Any]:

		"""
		Returns detailed information for a specified committee print.

		Args:
			congress (int): The congress number. For example, the value can be 117.
			chamber (str): The chamber name. Value can be house, senate, or nochamber.
			jacketNumber (int): The jacket number for the print. For example, the value can be 48144.
			
		Returns:
			dict: A dictionary containing the committee print details, or None if the API call fails.
		"""
		params = {}
		endpoint = f"/committee-print/{congress}/{chamber}/{jacketNumber}"
		msg = "committee print details"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_print_texts(
			self, __event_emitter__,
			congress: int, 
			chamber: str, 
			jacketNumber: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Returns the list of texts for a specified committee print.

		Args:
			congress (int): The congress number. For example, the value can be 117.
			chamber (str): The chamber name. Value can be house, senate, or nochamber.
			jacketNumber (int): The jacket number for the print. For example, the value can be 48144.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		Returns:
			dict: A dictionary containing the list of texts for the committee print, or None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/committee-print/{congress}/{chamber}/{jacketNumber}/text"
		msg = "committee print texts"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

###########################################################################################
# Committee meeting
###########################################################################################


	async def get_committee_meetings(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Retrieves a list of committee meetings from the API.

		Args:
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.

		Returns:
			dict: A dictionary containing the committee meetings data, or None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee-meeting"
		msg = "committee meetings"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_meetings_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Retrieves a list of committee meetings for a specific congress from the API.

		Args:
			congress (int): The congress number. For example, the value can be 118.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.

		Returns:
			dict: A dictionary containing the committee meetings data, or None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee-meeting/{congress}"
		msg = "committee meetings by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_meetings_by_congress_and_chamber(
			self, __event_emitter__,
			congress: int, 
			chamber: str, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Retrieves a list of committee meetings for a specific congress and chamber from the API.

		Args:
			congress (int): The congress number. For example, the value can be 118.
			chamber (str): The chamber name. Value can be house, senate, or nochamber.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.

		Returns:
			dict: A dictionary containing the committee meetings data, or None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/committee-meeting/{congress}/{chamber}"
		msg = "committee meetings by congress and chamber"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_committee_meeting_details(
			self, __event_emitter__,
			congress: int, 
			chamber: str, 
			eventId: str) -> Dict[str, Any]:
		"""
		Retrieves detailed information for a specified committee meeting from the API.

		Args:
			congress (int): The congress number. For example, the value can be 118.
			chamber (str): The chamber name. Value can be house, senate, or nochamber.
			eventId (str): The event identifier. For example, the value can be 115538.
			
		Returns:
			dict: A dictionary containing the detailed committee meeting information, or None if the API call fails.
		"""
		params = {}
		endpoint = f"/committee-meeting/{congress}/{chamber}/{eventId}"
		msg = "committee meeting details"
		return await self.call_api(__event_emitter__, endpoint, params, msg)


###########################################################################################
# Committee hearing
###########################################################################################


	async def get_hearings(
			self, __event_emitter__,
			congress=None, 
			chamber=None, 
			jacket_number=None, 
			format=None, 
			offset=None, 
			limit=None) -> Dict[str, Any]:
		"""
		Retrieves hearing data from the Congress.gov API.

		This method allows you to retrieve a list of hearings or a specific hearing based on the provided parameters.
		You can filter the hearings by congress, chamber, and jacket number.

		Args:
			congress (int, optional): The congress number to filter hearings by. Defaults to None.
			chamber (str, optional): The chamber to filter hearings by (house, senate, or nochamber). Defaults to None.
			jacket_number (int, optional): The jacket number of the specific hearing to retrieve. Defaults to None.
			format (str, optional): The desired data format (xml or json). Defaults to None (json).
			offset (int, optional): The starting record number for pagination. Defaults to None (0).
			limit (int, optional): The number of records to return per page. Defaults to None (API default).  Maximum is 250.

		Returns:
			dict: A dictionary containing the hearing data in JSON format, or None if the API request fails.
				  The structure of the dictionary depends on the specific endpoint being called.

		Examples:
			# Get all hearings:
			get_hearings()

			# Get hearings for a specific congress:
			get_hearings(congress=116)

			# Get hearings for a specific congress and chamber:
			get_hearings(congress=116, chamber="house")

			# Get a specific hearing by congress, chamber, and jacket number:
			get_hearings(congress=116, chamber="house", jacket_number=41365)

			# Get hearings with a specific format and limit:
			get_hearings(format="xml", limit=100)
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if congress:
			endpoint += f"/{congress}"
			if chamber:
				endpoint += f"/{chamber}"
				if jacket_number:
					endpoint += f"/{jacket_number}"
		endpoint = "/hearing"
		msg = "hearings"
		return await self.call_api(__event_emitter__, endpoint, params, msg)


###########################################################################################
# Congressional record
###########################################################################################

	
	async def get_congressional_record(
			self, __event_emitter__,
			year=None, 
			month=None, 
			day=None, 
			format=None, 
			offset=None, 
			limit=None) -> Dict[str, Any]:
		"""
		Retrieves Congressional Record data from the Congress.gov API for a specific date.

		This method allows you to retrieve a list of congressional record issues published on a specific date.

		Args:
			year (int, optional): The year the issue was published. Defaults to None.
			month (int, optional): The month the issue was published. Defaults to None.
			day (int, optional): The day the issue was published. Defaults to None.
			format (str, optional): The desired data format (xml or json). Defaults to None (json).
			offset (int, optional): The starting record number for pagination. Defaults to None (0).
			limit (int, optional): The number of records to return per page. Defaults to None (API default). Maximum is 250.

		Returns:
			dict: A dictionary containing the Congressional Record data in JSON format, or None if the API request fails.
				  The dictionary contains a 'Results' key, which then has an 'Issues' key with a list of issues.

		Example:
			# Get the congressional record for June 28, 2022:
			get_congressional_record(year=2022, month=6, day=28)

			#Get the congressional record for June 28, 2022 in XML format:
			get_congressional_record(year=2022, month=6, day=28, format="xml")
		"""
		params = {}
		if year:
			params['y'] = year
		if month:
			params['m'] = month
		if day:
			params['d'] = day
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = "/congressional-record/"
		msg = "Congressional Record data for a specific date"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

###########################################################################################
# Daily congressional record
###########################################################################################



	async def get_daily_congressional_record(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Retrieves a list of daily congressional record issues sorted by most recent.

		Args:
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		Returns:
			dict: A dictionary containing the daily congressional record data, or None if the API call fails.

		Example Usage:
			tools = Tools()
			record = tools.get_daily_congressional_record(limit=10)
			print(record)
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = "/daily-congressional-record"
		msg = "daily congressional record issues"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_daily_congressional_record_by_volume(
			self, __event_emitter__,
			volumeNumber: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Retrieves a list of daily Congressional Records filtered by the specified volume number.

		Args:
			volumeNumber (str): The specified volume of the daily Congressional record, for example 166.
			
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		Returns:
			dict: A dictionary containing the daily congressional record data, or None if the API call fails.

		Example Usage:
			tools = Tools()
			record = tools.get_daily_congressional_record_by_volume(volumeNumber="166", limit=10)
			print(record)
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/daily-congressional-record/{volumeNumber}"
		msg = "daily congressional record by volume"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_daily_congressional_record_by_volume_and_issue(
			self, __event_emitter__,
			volumeNumber: str, 
			issueNumber: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Returns a list of daily Congressional Records filtered by the specified volume number and specified issue number.

		Args:
			volumeNumber (str): The specified volume of the daily Congressional record, for example 168.
			issueNumber (str): The specified issue of the daily Congressional record, for example 153.
			
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		Returns:
			dict: A dictionary containing the daily congressional record data, or None if the API call fails.

		Example Usage:
			tools = Tools()
			record = tools.get_daily_congressional_record_by_volume_and_issue(volumeNumber="168", issueNumber="153", limit=10)
			print(record)
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/daily-congressional-record/{volumeNumber}/{issueNumber}"
		msg = "daily congressional record by volumne and issue"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_daily_congressional_record_articles(
			self, __event_emitter__,
			volumeNumber: str, 
			issueNumber: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Returns a list of daily Congressional Record articles filtered by the specified volume number and specified issue number.

		Args:
			volumeNumber (str): The specified volume of the daily Congressional record, for example 167.
			issueNumber (str): The specified issue of the daily Congressional record, for example 21.
			
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		Returns:
			dict: A dictionary containing the daily congressional record articles, or None if the API call fails.

		Example Usage:
			tools = Tools()
			articles = tools.get_daily_congressional_record_articles(volumeNumber="167", issueNumber="21", limit=10)
			print(articles)
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/daily-congressional-record/{volumeNumber}/{issueNumber}/articles"
		msg = "daily congressional record articles"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

###########################################################################################
# Nomination
###########################################################################################
	async def get_nominations(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Retrieves a list of nominations.

		Args:
			format (str, optional): The data format.  Can be 'xml' or 'json'. Defaults to None.
			offset (int, optional): The starting record number to return.  0 is the first record. Defaults to None.
			limit (int, optional): The maximum number of records to return. Maximum is 250. Defaults to None.

		Returns:
			dict: A dictionary containing the nominations data, or None if the API request fails.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = "/nominations"
		msg = "nominations"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_nomination(
			self, __event_emitter__,
			nomination_number: str) -> Dict[str, Any]:
		"""
		Retrieves a specific nomination by its nomination number.

		Args:
			nomination_number (str): The nomination number to retrieve (e.g., PN1234).
			format (str, optional): The data format. Can be 'xml' or 'json'. Defaults to None.

		Returns:
			dict: A dictionary containing the nomination data, or None if the API request fails.
		"""
		params = {}
		endpoint = f"/nomination/{nomination_number}"
		msg = "nomination by number"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_nominations_by_congress(
			self, __event_emitter__,
			congress: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Retrieves nominations for a specific Congress.

		Args:
			congress (str): The Congress number (e.g., '117').
			format (str, optional): The data format. Can be 'xml' or 'json'. Defaults to None.
			offset (int, optional): The starting record number to return. 0 is the first record. Defaults to None.
			limit (int, optional): The maximum number of records to return. Maximum is 250. Defaults to None.

		Returns:
			dict: A dictionary containing the nominations data, or None if the API request fails.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/nominations/{congress}"
		msg = "nomination by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_latest_nominations(
			self, __event_emitter__, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Retrieves the latest nominations.

		Args:
			format (str, optional): The data format. Can be 'xml' or 'json'. Defaults to None.
			offset (int, optional): The starting record number to return. 0 is the first record. Defaults to None.
			limit (int, optional): The maximum number of records to return. Maximum is 250. Defaults to None.

		Returns:
			dict: A dictionary containing the latest nominations data, or None if the API request fails.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = "/nominations/latest"
		msg = "latest nominations"
		return await self.call_api(__event_emitter__, endpoint, params, msg)


###########################################################################################
# House-communication
###########################################################################################
	
	async def get_house_communication(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Retrieves a list of House communications.

		Args:
			format (str, optional): The desired data format.  Valid values are "xml" or "json". Defaults to None, which uses the default API format.
			offset (int, optional): The index of the first record to return (0-based).  Defaults to None, which starts at the beginning.
			limit (int, optional): The maximum number of records to return.  Must be a positive integer no greater than 250. Defaults to None, which uses the API default.

		Returns:
			dict: A dictionary containing the House communications, or None if the API request fails.

		Example:
			To retrieve the first 50 house communications in JSON format:
			```python
			communications = api.get_house_communication(format="json", limit=50)
			```
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = "/house-communication"
		msg = "house communication"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_house_communication_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Retrieves a list of House communications filtered by the specified congress.

		Args:
			congress (int): The congress number (e.g., 117).
			format (str, optional): The desired data format. Valid values are "xml" or "json". Defaults to None, which uses the default API format.
			offset (int, optional): The index of the first record to return (0-based). Defaults to None, which starts at the beginning.
			limit (int, optional): The maximum number of records to return. Must be a positive integer no greater than 250. Defaults to None, which uses the API default.

		Returns:
			dict: A dictionary containing the House communications, or None if the API request fails.

		Example:
			To retrieve the first 100 house communications from the 117th congress in XML format:
			```python
			communications = api.get_house_communication_by_congress(congress=117, format="xml", limit=100)
			```
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/house-communication/{congress}"
		msg = "house communication by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_house_communication_by_congress_type(
			self, __event_emitter__,
			congress: int, 
			communicationType: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Retrieves a list of House communications filtered by the specified congress and communication type.

		Args:
			congress (int): The congress number (e.g., 117).
			communicationType (str): The type of communication. Valid values are "ec", "ml", "pm", or "pt".
			format (str, optional): The desired data format. Valid values are "xml" or "json". Defaults to None, which uses the default API format.
			offset (int, optional): The index of the first record to return (0-based). Defaults to None, which starts at the beginning.
			limit (int, optional): The maximum number of records to return. Must be a positive integer no greater than 250. Defaults to None, which uses the API default.

		Returns:
			dict: A dictionary containing the House communications, or None if the API request fails.

		Example:
			To retrieve the first 20 "ec" type communications from the 118th congress in JSON format:
			```python
			communications = api.get_house_communication_by_congress_type(congress=118, communicationType="ec", format="json", limit=20)
			```
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/house-communication/{congress}/{communicationType}"
		msg = "house communication by congress type"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_house_communication_by_congress_type_number(
			self, __event_emitter__,
			congress: int, 
			communicationType: str, 
			communicationNumber: int
			) -> Dict[str, Any]:

		"""
		Retrieves detailed information for a specified House communication.

		Args:
			congress (int): The congress number (e.g., 117).
			communicationType (str): The type of communication. Valid values are "ec", "ml", "pm", or "pt".
			communicationNumber (int): The communication's assigned number (e.g., 3324).
			format (str, optional): The desired data format. Valid values are "xml" or "json". Defaults to None, which uses the default API format.

		Returns:
			dict: A dictionary containing the detailed information for the specified House communication, or None if the API request fails.

		Example:
			To retrieve the details for communication number 1234 of type "ml" from the 116th congress in XML format:
			```python
			communication = api.get_house_communication_by_congress_type_number(congress=116, communicationType="ml", communicationNumber=1234, format="xml")
			```
		"""
		params = {}
		endpoint = f"/house-communication/{congress}/{communicationType}/{communicationNumber}"
		msg = "house communication by congress type number"
		return await self.call_api(__event_emitter__, endpoint, params, msg)



###########################################################################################
# House-requirement
###########################################################################################


	async def get_house_requirements(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns a list of House requirements.

		Args:
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		Returns:
			dict: A dictionary containing a list of house requirements.
					Returns None if the API request fails.

		Example:
			tool = Tools(api_key="YOUR_API_KEY")
			requirements = tool.get_house_requirements(limit=10)
			print(requirements)
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = "/house-requirement"
		msg = "House requirements"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_house_requirement_details(
			self, __event_emitter__,
			requirement_number: int
			) -> Dict[str, Any]:
		"""
		Returns detailed information for a specified House requirement.

		Args:
			requirement_number (int): The requirement’s assigned number. For example, the value can be 8070.
			
		Returns:
			dict: A dictionary containing detailed information for a specified House requirement.
				  Returns None if the API request fails.

		Example:
			tool = Tools(api_key="YOUR_API_KEY")
			details = tool.get_house_requirement_details(requirement_number=8070)
			print(details)
		"""
		params = {}
		endpoint = f"/house-requirement/{requirement_number}"
		msg = "House requirement details"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_house_requirement_matching_communications(
			self, __event_emitter__,
			requirement_number: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns a list of matching communications to a House requirement.

		Args:
			requirement_number (int): The requirement’s assigned number. For example, the value can be 8070.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		Returns:
			dict: A dictionary containing a list of matching communications to a House requirement.
				  Returns None if the API request fails.

		Example:
			tool = Tools(api_key="YOUR_API_KEY")
			communications = tool.get_house_requirement_matching_communications(requirement_number=8070, limit=5)
			print(communications)
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/house-requirement/{requirement_number}/matching-communications"
		msg = "House requirement matching communications"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

###########################################################################################
# Senate-communication
###########################################################################################


	async def get_senate_communications(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns a list of Senate communications.

		Args:
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		Returns:
			dict: A dictionary containing a list of senate communications.
				  Returns None if the API request fails.

		Example:
			tool = Tools(api_key="YOUR_API_KEY")
			communications = tool.get_senate_communications(limit=10)
			print(communications)
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = "/senate-communication"
		msg = "Senate communications"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_senate_communications_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Returns a list of Senate communications filtered by the specified congress.

		Args:
			congress (int): The congress number. For example, the value can be 117.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		Returns:
			dict: A dictionary containing a list of senate communications filtered by congress.
				  Returns None if the API request fails.

		Example:
			tool = Tools(api_key="YOUR_API_KEY")
			communications = tool.get_senate_communications_by_congress(congress=117, limit=10)
			print(communications)
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/senate-communication/{congress}"
		msg = "Senate communications by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_senate_communications_by_congress_and_type(
			self, __event_emitter__,
			congress: int, 
			communication_type: str, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Returns a list of Senate communications filtered by the specified congress and communication type.

		Args:
			congress (int): The congress number. For example, the value can be 117.
			communication_type (str): The type of communication. Value can be ec, pm, or pom.
			    "Executive Communication (EC)": "ec"
				"Presidential Message (PM)": "pm"
				"Petition or Memorial (POM)": "pom"
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		Returns:
			dict: A dictionary containing a list of senate communications filtered by congress and type.
				  Returns None if the API request fails.

		Example:
			tool = Tools(api_key="YOUR_API_KEY")
			communications = tool.get_senate_communications_by_congress_and_type(congress=117, communication_type='ec', limit=10)
			print(communications)
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/senate-communication/{congress}/{communication_type}"
		msg = "Senate communications by congress and type"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_senate_communication_details(
			self, __event_emitter__,
			congress: int, 
			communication_type: str, 
			communication_number: int
			) -> Dict[str, Any]:

		"""
		Returns detailed information for a specified Senate communication.

		Args:
			congress (int): The congress number. For example, the value can be 117.
			communication_type (str): The type of communication. Value can be ec, pm, or pom.
			    "Executive Communication (EC)": "ec"
				"Presidential Message (PM)": "pm"
				"Petition or Memorial (POM)": "pom"
			communication_number (int): The communication’s assigned number. For example, the value can be 2561.
			
		Returns:
			dict: A dictionary containing detailed information for a specified senate communication.
				  Returns None if the API request fails.

		Example:
			tool = Tools(api_key="YOUR_API_KEY")
			details = tool.get_senate_communication_details(congress=117, communication_type='ec', communication_number=2561)
			print(details)
		"""
		params = {}
		endpoint = f"/senate-communication/{congress}/{communication_type}/{communication_number}"
		msg = "Senate communication details"
		return await self.call_api(__event_emitter__, endpoint, params, msg)


###########################################################################################
# Nomination
###########################################################################################


	async def get_nominations(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Returns a list of nominations sorted by date received from the President.
		
		Args:
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
		
		Returns:
			dict: A dictionary containing the nominations data, or None if the API call fails.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = "/nomination"
		msg = "nominations"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_nominations_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Returns a list of nominations filtered by the specified congress and sorted by date received from the President.
		
		Args:
			congress (int): The congress number. For example, the value can be 117.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
		
		Returns:
			dict: A dictionary containing the nominations data for the specified congress, or None if the API call fails.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/nomination/{congress}"
		msg = "nominations filtered by the specified congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_nomination_details(
			self, __event_emitter__,
			congress: int, 
			nominationNumber: int
			) -> Dict[str, Any]:

		"""
		Returns detailed information for a specified nomination.
		
		Args:
			congress (int): The congress number. For example, the value can be 117.
			nominationNumber (int): The nomination’s assigned number. For example, the value can be 2467.
			
		Returns:
			dict: A dictionary containing the details of the specified nomination, or None if the API call fails.
		"""
		params = {}
		endpoint = f"/nomination/{congress}/{nominationNumber}"
		msg = "detailed information for a specified nomination"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_nominee_list(
			self, __event_emitter__,
			congress: int, 
			nominationNumber: int, 
			ordinal: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Returns the list nominees for a position within the nomination.
		
		Args:
			congress (int): The congress number. For example, the value can be 117.
			nominationNumber (int): The nomination’s assigned number. For example, the value can be 2467.
			ordinal (int): The ordinal number. For example, the value can be 1.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
		
		Returns:
			dict: A dictionary containing the list of nominees for the specified position, or None if the API call fails.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/nomination/{congress}/{nominationNumber}/{ordinal}"
		msg = "list nominees for a position within the nomination"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_nomination_actions(
			self, __event_emitter__,
			congress: int, 
			nominationNumber: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Returns the list of actions on a specified nomination.
		
		Args:
			congress (int): The congress number. For example, the value can be 117.
			nominationNumber (int): The nomination’s assigned number. For example, the value can be 2467.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
		
		Returns:
			dict: A dictionary containing the list of actions on the specified nomination, or None if the API call fails.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/nomination/{congress}/{nominationNumber}/actions"
		msg = "actions on a specified nomination"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_nomination_committees(
			self, __event_emitter__,
			congress: int, 
			nominationNumber: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Returns the list of committees associated with a specified nomination.
		
		Args:
			congress (int): The congress number. For example, the value can be 117.
			nominationNumber (int): The nomination’s assigned number. For example, the value can be 2467.
			
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
		
		Returns:
			dict: A dictionary containing the list of committees associated with the specified nomination, or None if the API call fails.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/nomination/{congress}/{nominationNumber}/committees"
		msg = "committees associated with a specified nomination"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_nomination_hearings(
			self, __event_emitter__,
			congress: int, 
			nominationNumber: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:

		"""
		Returns the list of printed hearings associated with a specified nomination.
		
		Args:
			congress (int): The congress number. For example, the value can be 116.
			nominationNumber (int): The nomination’s assigned number. For example, the value can be 389.
			
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
		
		Returns:
			dict: A dictionary containing the list of printed hearings associated with the specified nomination, or None if the API call fails.
		"""
		params = {}
		if offset:
			params['offset'] = offset
		if limit:
			params['limit'] = limit
		endpoint = f"/nomination/{congress}/{nominationNumber}/hearings"
		msg = "hearings associated with a specified nomination"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

###########################################################################################
# CRS Report
###########################################################################################


	async def crsreport(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Retrieves Congressional Research Service (CRS) report data from the API.
		
		Args:
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
		
		Returns:
			dict: A dictionary containing the CRS report data, or None if the API call fails.
		
		Example:
			To retrieve the first 10 CRS reports in JSON format updated between 2025-02-05 and 2025-02-07:
			crs_reports = tools.crsreport(format="json", offset=0, limit=10, fromDateTime="2025-02-05T00:00:00Z", toDateTime="2025-02-07T00:00:00Z")
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = "/crsreport"
		msg = "Congressional Research Service (CRS) report data"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def crsreport_by_report_number(
			self, __event_emitter__,
			reportNumber: str) -> Dict[str, Any]:
		"""
		Retrieves detailed information for a specified Congressional Research Service (CRS) report.
		
		Args:
			reportNumber (str): The number or ID of the report. For example, R47175. This is a required argument.
		
		Returns:
			dict: A dictionary containing the detailed information for the specified CRS report, or None if the API call fails.
		
		Example:
			To retrieve the CRS report with report number R47175 in JSON format:
			report_details = tools.crsreport_by_report_number(reportNumber="R47175", format="json")
		"""
		if not reportNumber:
			raise ValueError("reportNumber is a required argument.")
		params = {}
		endpoint = f"/crsreport/{reportNumber}"
		msg = "Congressional Research Service (CRS) report data by number"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

###########################################################################################
# Treaty
###########################################################################################


	async def get_treaties(
			self, __event_emitter__ , 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Returns a list of treaties sorted by date of last update.
		
		Args:
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			
		Returns:
			dict: A dictionary containing treaty data.  Returns None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = "/treaty"
		msg = "treaties"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_treaties_by_congress(
			self, __event_emitter__,
			congress: int, 
			offset: int = 0, 
			limit: int = None, 
			fromDateTime: str = None, 
			toDateTime: str = None
			) -> Dict[str, Any]:

		"""
		Returns a list of treaties for the specified congress, sorted by date of last update.
		
		Args:
			congress (int): The congress number. For example, value can be 117.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			fromDateTime (str, optional): The starting timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			toDateTime (str, optional): The ending timestamp to filter by update date. Use format: YYYY-MM-DDT00:00:00Z. Defaults to None.
			
		Returns:
			dict: A dictionary containing treaty data. Returns None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		if fromDateTime:
			params['fromDateTime'] = fromDateTime
		if toDateTime:
			params['toDateTime'] = toDateTime
		endpoint = f"/treaty/{congress}"
		msg = "treaties by congress"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_treaty_details(
			self, __event_emitter__,
			congress: int, 
			treatyNumber: int
			) -> Dict[str, Any]:

		"""
		Returns detailed information for a specified treaty.
		
		Args:
			congress (int): The congress number. For example, value can be 117.
			treatyNumber (int): The treaty’s assigned number. For example, value can be 3.
			
		Returns:
			dict: A dictionary containing detailed treaty information. Returns None if the API call fails.
		"""
		params = {}
		endpoint = f"/treaty/{congress}/{treatyNumber}"
		msg = "treaty details"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_treaty_partition(
			self, __event_emitter__,
			congress: int, 
			treatyNumber: int, 
			treatySuffix: str) -> Dict[str, Any]:
		"""
		Returns detailed information for a specified partitioned treaty.
		
		Args:
			congress (int): The congress number. For example, the value can be 114.
			treatyNumber (int): The treaty’s assigned number. For example, the value can be 13.
			treatySuffix (str): The treaty’s partition letter value. For example, the value can be A.
			
		Returns:
			dict: A dictionary containing detailed partitioned treaty information. Returns None if the API call fails.
		"""
		params = {}
		endpoint = f"/treaty/{congress}/{treatyNumber}/{treatySuffix}"
		msg = "information for a specified partitioned treaty"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_treaty_actions(
			self, __event_emitter__,
			congress: int, 
			treatyNumber: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		Returns the list of actions on a specified treaty.
		
		Args:
			congress (int): The congress number. For example, the value can be 117.
			treatyNumber (int): The treaty’s assigned number. For example, the value can be 3.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			
		Returns:
			dict: A dictionary containing a list of actions. Returns None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/treaty/{congress}/{treatyNumber}/actions"
		msg = "actions on a specified treaty"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_treaty_partition_actions(
			self, __event_emitter__,
			congress: int, 
			treatyNumber: int, 
			treatySuffix: str, 
			offset: int = 0, 
			limit: int = None) -> Dict[str, Any]:
		"""
		Returns the list of actions on a specified partitioned treaty.
		
		Args:
			congress (int): The congress number. For example, the value can be 114.
			treatyNumber (int): The treaty’s assigned number. For example, the value can be 13.
			treatySuffix (str): The treaty’s partition letter value. For example, the value can be A.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.
			
		Returns:
			dict: A dictionary containing a list of actions. Returns None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/treaty/{congress}/{treatyNumber}/{treatySuffix}/actions"
		msg = "actions on a specified partitioned treaty"
		return await self.call_api(__event_emitter__, endpoint, params, msg)

	async def get_treaty_committees(
			self, __event_emitter__,
			congress: int, 
			treatyNumber: int, 
			offset: int = 0, 
			limit: int = None
			) -> Dict[str, Any]:
		"""
		  Returns the list of committees associated with a specified treaty.

		  Args:
			congress (int): The congress number. For example, the value can be 116.
			treatyNumber (int): The treaty’s assigned number. For example, the value can be 3.
			offset (int, optional): The starting record returned. 0 is the first record. Defaults to 0
			limit (int, optional): The number of records returned. The maximum limit is 250. Defaults to None.

		  Returns:
			dict: A dictionary containing a list of committees. Returns None if the API call fails.
		"""
		params = {}
		if offset is not None:
			params['offset'] = offset
		if limit is not None:
			params['limit'] = limit
		endpoint = f"/treaty/{congress}/{treatyNumber}/committees"
		msg = "committees associated with a specified treaty"
		return await self.call_api(__event_emitter__, endpoint, params, msg)
