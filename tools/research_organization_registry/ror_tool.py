"""
title: Research Organization Registry Search
author: blunderfist
git_url: https://github.com/blunderfist/open_web_ui/blob/main/tools/research_organization_registry/ror_tool.py
version: 1.0.0
description: This tool searches Research Organization Registry
required_open_webui_version: 0.4.0
requirements: pydantic>=2.11.4,httpx>=0.28.1
licence: MIT
"""

import os
import datetime
import json
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import httpx
import asyncio



class Tools:
	def __init__(self):
		"""Initialize the Tool."""
		self.BASE_URL = "https://api.ror.org/v2/organizations" # Base URL for the API


	async def call_api(
			self,
			params=None, 
			msg = None,
			__event_emitter__ = None
			) -> Dict[str, Any]:
		"""
		Calls the specified API endpoint with the given parameters.
		"""

		if __event_emitter__:
			await __event_emitter__({
				"type": "status",
				"data": {"description": f"Executing {msg} ROR query...", 
						"done": False, # Displayed while search is being run
						"hidden": True} # True removes message after chat compeletion
			})

		async with httpx.AsyncClient(timeout = 10.0) as client:
			try:
				# url = f"{self.BASE_URL}{endpoint}"
				response = await client.get(self.BASE_URL, params = params)
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
# Organizations
###########################################################################################


	async def query(
		self,
		organization: Optional[List[str]] = None, 
		status: Optional[str] = None,
		types: Optional[str] = None,
		country_code: Optional[str] = None,
		country_name: Optional[str] = None,
		continent_code: Optional[str] = None,
		continent_name: Optional[str] = None,
		__event_emitter__ = None
		) -> Dict[str, Any]:

		"""
		The query parameter is a "quick search" of only the names and external_ids fields in ROR. The query parameter works best for the following purposes:
			Keyword-based searching for organization names
			Form field auto-suggests / typeaheads
			Searching for exact matches of an organization name
			Searching for external identifiers

		:param organization: name of organzation(s)

		Filter records based on status, organization type, country, and continent information.

		:param status: Filter records by record status. Valid values are:
			- "active"
			- "inactive"
			- "withdrawn"

		:param types: Filter records by organization type. Valid values are:
			- "archive"
			- "company"
			- "education"
			- "facility"
			- "funder"
			- "government"
			- "healthcare"
			- "other"

		:param country_code: Filter records by ISO 3166-2 country code (2-character, uppercase).
			Can be matched against:
			- `country.country_code`
			- `locations.geonames_details.country_code`

		:param country_name: Filter records by country name.
			Can be matched against:
			- `country.country_name`
			- `locations.geonames_details.country_name`

		:param continent_code: Filter records by continent code.
			Valid values are:
			- "AF" (Africa)
			- "AN" (Antarctica)
			- "AS" (Asia)
			- "EU" (Europe)
			- "NA" (North America)
			- "OC" (Oceania)
			- "SA" (South America)

			Can be matched against:
			- `locations.geonames_details.continent_code`

		:param continent_name: Filter records by continent name.
			Valid values are:
			- "Africa"
			- "Antarctica"
			- "Asia"
			- "Europe"
			- "North America"
			- "Oceania"
			- "South America"

			Can be matched against:
			- `locations.geonames_details.continent_name`

		:return: Dict
		"""

		msg = "basic"
		params = {}
		filters = []
		if organization:
			params["query"] = organization
		if status:
			filters.append(f"status:{status}")
		if types:
			filters.append(f"types:{types}")
		if country_code:
			filters.append(f"country_code:{country_code}")
		if country_name:
			filters.append(f"country_name:{country_name}")
		if continent_code:
			filters.append(f"continent_code:{continent_code}")
		if continent_name:
			filters.append(f"continent_name:{continent_name}")

		# check if filters before adding
		if len(filters) > 0:
			params["filter"] = ",".join(filters)

		if isinstance(organization, list) and len(organization) > 1:
			results = []
			for org in organization:
				org_params = params
				org_params['query'] = org
				results.append(await self.call_api(org_params, __event_emitter__))
			return {'results': results}
		else:
			return await self.call_api(params, msg, __event_emitter__)
	



###########################################################################################
# Advanced Query
###########################################################################################



	async def advanced_query(
			self,
			advanced_query: Optional[str] = None,
			__event_emitter__ = None
			) -> Dict[str, Any]:
		"""
		Retrieve metadata about a research organization from the ROR API.

		This function returns detailed information about a research organization, including identifiers, names, location, relationships, and external references. 
		It also supports advanced querying using Elasticsearch query string syntax for precise and flexible search capabilities.

		Advanced Query Usage:
			The `advanced_query` parameter allows thorough and precise searching of any and all ROR record fields using Elasticsearch query string syntax.

			Recommended for:
				- Analyzing the ROR registry to answer research questions
				- Searching for records with specific or complex combinations of characteristics

			Syntax Features:
				- Field-specific queries (e.g., `name:"University of Oxford"`)
				- Boolean operators: AND, OR, NOT
				- Wildcards: `*` and `?`
				- Range queries: `[2020 TO 2023]`
				- Grouping with parentheses: `(type:education AND country.country_code:GB)`
				- Phrase matching with quotation marks: `"University of Oxford"`

			Reserved Characters:
				Elasticsearch treats certain characters as special. These must be escaped with a backslash (`\`) and URL-encoded:
				`+ - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /`

			Case Sensitivity:
				- Queries are case-sensitive. For best results, use correct capitalization (e.g., `Panama` not `panama`).

			Date Filtering:
				- Use range queries on `created` and `last_updated` fields.
				- Example: `created:[2020-01-01 TO 2023-12-31]`
				- Reserved characters `[ ] { }` must be escaped or URL-encoded.

		:param id: Unique ROR ID for the organization.

		:param admin: Administrative metadata about the record.
			- `admin.created.date` (str): Date the record was added to ROR (format: YYYY-MM-DD).
			- `admin.created.schema_version` (str): ROR schema version at creation. Allowed values: "1.0", "2.0", "2.1".
			- `admin.last_modified.date` (str): Date the record was last modified (format: YYYY-MM-DD).
			- `admin.last_modified.schema_version` (str): ROR schema version at last modification. Allowed values: "1.0", "2.0", "2.1".

		:param domains: List of fully-qualified domain names associated with the organization.
			- Each domain must be unique across ROR and not a subdomain of another listed domain.

		:param established: Year the organization was established (format: YYYY).

		:param external_ids: External identifiers associated with the organization.
			- `external_ids.type` (str): Identifier system. Allowed values: "fundref", "grid", "isni", "wikidata".
			- `external_ids.all` (List[str]): All external identifiers of the specified type.
			- `external_ids.preferred` (str): Preferred external identifier of the specified type.

		:param links: URLs related to the organization.
			- `links.type` (str): Type of link. Allowed values: "website", "wikipedia".
			- `links.value` (str): Valid URI (RFC 3986) of the link.

		:param locations: Location metadata for the organization.
			- `locations.geonames_id` (int): GeoNames ID for the city or region.
			- `locations.geonames_details` (dict): Metadata from GeoNames including:
				- `continent_code` (str): 2-character continent code.
				- `continent_name` (str): Name of the continent.
				- `country_code` (str): ISO 3166-2 country code (uppercase).
				- `country_name` (str): Name of the country.
				- `country_subdivision_code` (str): ISO 3166-2 subdivision code (2–3 characters).
				- `country_subdivision_name` (str): Name of the subdivision.
				- `lat` (float): Latitude of the location.
				- `lng` (float): Longitude of the location.
				- `name` (str): Name of the location (e.g., city or town).

		:param names: Name metadata for the organization.
			- `names.lang` (str): ISO 639-1 language code (lowercase).
			- `names.types` (List[str]): Types of name. Allowed values: "acronym", "alias", "label", "ror_display".
			- `names.value` (str): Name the organization is or was known by.

		:param relationships: List of relationships to other organizations.
			Each relationship includes:
			- `id` (str): ROR ID of the related organization.
			- `label` (str): Name of the related organization.
			- `type` (str): Relationship type. Allowed values: "child", "parent", "related", "successor", "predecessor".

		:param status: Status of the organization. Allowed values:
			- "active"
			- "inactive"
			- "withdrawn"

		:param types: List of organization types. Allowed values:
			- "archive"
			- "company"
			- "education"
			- "facility"
			- "funder"
			- "government"
			- "healthcare"
			- "other"

		:return: A dictionary
		"""
		msg = "advanced"
		params = {}
		if advanced_query:
			params["query.advanced"] = advanced_query
		
		return await self.call_api(params, msg, __event_emitter__)




###########################################################################################
# Affiliations
###########################################################################################



	async def get_affiliation_matches(
		self,
		affiliation: str,
		__event_emitter__ = None
		) -> Dict[str, Any]:
		"""
		The affiliation parameter is designed to match messy text to ROR records. 
		It breaks long search strings into multiple substrings, performs multiple searches of only the names field in ROR using several different search algorithms, 
		limits results to records matching any country names or ISO codes in the text, and finally returns (if possible!) its best guess about the mostly likely match to a ROR record, 
		plus additional possibilities ranked in descending order by matching confidence score.
		The affiliation parameter is designed for the following purposes:
			- Matching ROR IDs to legacy author affiliations in publishing systems
			- Matching ROR IDs to long and heavily-punctuated text strings that contain not just organization names, but also extraneous information such as addresses and academic departments

		:param id: Unique ROR ID for the organization.

		:param admin: Administrative metadata about the record.
			- `admin.created.date` (str): Date the record was added to ROR (format: YYYY-MM-DD).
			- `admin.created.schema_version` (str): ROR schema version at creation. Allowed values: "1.0", "2.0", "2.1".
			- `admin.last_modified.date` (str): Date the record was last modified (format: YYYY-MM-DD).
			- `admin.last_modified.schema_version` (str): ROR schema version at last modification. Allowed values: "1.0", "2.0", "2.1".

		:param domains: List of fully-qualified domain names associated with the organization.
			- Each domain must be unique across ROR and not a subdomain of another listed domain.

		:param established: Year the organization was established (format: YYYY).

		:param external_ids: External identifiers associated with the organization.
			- `external_ids.type` (str): Identifier system. Allowed values: "fundref", "grid", "isni", "wikidata".
			- `external_ids.all` (List[str]): All external identifiers of the specified type.
			- `external_ids.preferred` (str): Preferred external identifier of the specified type.

		:param links: URLs related to the organization.
			- `links.type` (str): Type of link. Allowed values: "website", "wikipedia".
			- `links.value` (str): Valid URI (RFC 3986) of the link.

		:param locations: Location metadata for the organization.
			- `locations.geonames_id` (int): GeoNames ID for the city or region.
			- `locations.geonames_details` (dict): Metadata from GeoNames including:
				- `continent_code` (str): 2-character continent code.
				- `continent_name` (str): Name of the continent.
				- `country_code` (str): ISO 3166-2 country code (uppercase).
				- `country_name` (str): Name of the country.
				- `country_subdivision_code` (str): ISO 3166-2 subdivision code (2–3 characters).
				- `country_subdivision_name` (str): Name of the subdivision.
				- `lat` (float): Latitude of the location.
				- `lng` (float): Longitude of the location.
				- `name` (str): Name of the location (e.g., city or town).

		:param names: Name metadata for the organization.
			- `names.lang` (str): ISO 639-1 language code (lowercase).
			- `names.types` (List[str]): Types of name. Allowed values: "acronym", "alias", "label", "ror_display".
			- `names.value` (str): Name the organization is or was known by.

		:param relationships: List of relationships to other organizations.
			Each relationship includes:
			- `id` (str): ROR ID of the related organization.
			- `label` (str): Name of the related organization.
			- `type` (str): Relationship type. Allowed values: "child", "parent", "related", "successor", "predecessor".

		:param status: Status of the organization. Allowed values:
			- "active"
			- "inactive"
			- "withdrawn"

		:param types: List of organization types. Allowed values:
			- "archive"
			- "company"
			- "education"
			- "facility"
			- "funder"
			- "government"
			- "healthcare"
			- "other"

		:return: A dictionary containing the full metadata record for the organization.

		Examples of affiliation text:
			"Department of Civil and Industrial Engineering, University of Pisa, Largo Lucio Lazzarino 2, Pisa 56126, Italy"
			"UCL School of Slavonic and East European Studies"
		"""
		msg = "affiliation"
		params = {"affiliation": affiliation}
		return await self.call_api(params, msg, __event_emitter__)
