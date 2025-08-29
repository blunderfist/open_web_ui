"""
title: Semantic Scholar Search
author: blunderfist
git_url: https://github.com/blunderfist/open_web_ui/blob/main/tools/semantic_scholar/semantic_scholar_tool.py
version: 1.0.0
description: This tool searches semantic scholar
required_open_webui_version: 0.4.0
requirements: pydantic>=2.11.4,httpx>=0.28.1
licence: MIT
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import httpx
import asyncio


class Tools:
    def __init__(self):
        """Initialize the Tool."""
        self.base_url = "https://api.semanticscholar.org/graph/v1/"

    async def fetch_paper(
        self, __event_emitter__,
        query: str,
        limit: int = None,
        fields: str = None,
        publicationTypes: Optional[str] = None,
        openAccessPdf: Optional[str] = None,
        minCitationCount: Optional[int] = None,
        publicationDateOrYear: Optional[str] = None,
        year: Optional[str] = None,
        venue:Optional[str] = None,
        fieldsOfStudy: Optional[str] = None,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Paper relevance search using the Semantic Scholar API.

        Fetches papers based on a query string and optional fields, with support
        for pagination and field selection.

        Examples:
            Search papers about COVID vaccination:
                fetch_paper(query="covid vaccination", limit=3, fields="title,authors,year")

            Search papers with URL and abstract fields:
                fetch_paper(query="covid", limit=100, fields="url,abstract,authors")

        Limitations:
            - Returns up to 1,000 relevance-ranked results per query.
            - Maximum 10 MB of data per request.

        Parameters:
        - query (string, required): A plain-text search query string. No special syntax is supported.
            Example: "generative ai"

        - fields (string, optional): Comma-separated list of fields to return for each paper.
            Default: "paperId,title"
            Examples:
                "title,url"
                "title,embedding.specter_v2"
                "title,authors,citations.title,citations.abstract"

        - limit (integer, optional): Maximum number of results to return. Must be <= 100.
            Default: 100

        - publicationTypes (string, optional): Comma-separated list of publication types to filter by.
        - openAccessPdf (string, optional): Include only papers with a public PDF.
        - minCitationCount (integer, optional): Minimum number of citations to include.
        - publicationDateOrYear (string, optional): Date range or year range filter (YYYY-MM-DD:YYYY-MM-DD).
        - year (string, optional): Specific publication year or range.
        - venue (string, optional): Comma-separated list of venues or ISO4 abbreviations.
        - fieldsOfStudy (string, optional): Comma-separated list of fields of study to filter by.
        - offset (integer, optional): Pagination offset. Default: 0
        """

        url = f"{self.base_url}paper/search"

        params = {
            "query": query
            }

        optional_params = {
            "limit": limit,
            "fields": fields,
            "publicationTypes": publicationTypes,
            "openAccessPdf": openAccessPdf,
            "minCitationCount": minCitationCount,
            "publicationDateOrYear": publicationDateOrYear,
            "year": year,
            "venue": venue,
            "fieldsOfStudy": fieldsOfStudy,
            "offset": offset
        }

        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for papers...", 
                     "done": False, # Displayed while search is being run
                     "hidden": True} # True removes message after chat compeletion
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
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



    async def fetch_papers_partial_match(
            self, __event_emitter__,
            query: str
            ) -> Dict[str, Any]:
        """
        Suggest paper query completions for interactive search.

        Returns minimal information about papers that match a partial query.
        Useful for autocompletion in search interfaces.

        Example:
            fetch_papers_partial_match(query="semanti")

        Limitations:
            - Partial query will be truncated to the first 100 characters.
            - Returns only minimal paper information for speed and interactivity.

        Parameters:
        - query (string, required): Plain-text partial query string.
            Example: "semanti"
        """
        url = f"{self.base_url}paper/autocomplete"

        params = {
            "query": query
        }

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for papers using partial match...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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



    async def fetch_papers_batch(
            self, __event_emitter__, 
            ids: List[str], 
            fields: str
            ) -> Dict[str, Any]:
        """
        Get details for multiple papers at once
        Fields is a single-value string parameter, not a multi-value one.
        It is a query parameter, not to be submitted in the POST request's body.
        Limitations:
        Can only process 500 paper ids at a time.
        Can only return up to 10 MB of data at a time.
        Can only return up to 9999 citations at a time.
        For a list of supported IDs reference the "Details about a paper" endpoint.
        fields	
            string
            A comma-separated list of the fields to be returned. See the contents of Response Schema below for a list of all available fields that can be returned. The paperId field is always returned. If the fields parameter is omitted, only the paperId and title will be returned.

            Use a period (“.”) for fields that have version numbers or subfields, such as the embedding, authors, citations, and references fields:

            When requesting authors, the authorId and name subfields are returned by default. To request other subfields, use the format author.url,author.paperCount, etc. See the Response Schema below for available subfields.
            When requesting citations and references, the paperId and title subfields are returned by default. To request other subfields, use the format citations.title,citations.abstract, etc. See the Response Schema below for available subfields.
            When requesting embedding, the default Spector embedding version is v1. Specify embedding.specter_v2 to select v2 embeddings.
            Examples:
            fields=title,url
            fields=title,embedding.specter_v2
            fields=title,authors,citations.title,citations.abstract
        ids	
            Array of strings
        """

        url = f"{self.base_url}paper/batch"

        data = {
            "ids": ids
        }

        params = {
            "fields": fields
        }

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for batch of papers...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, params=params, json=data)
                response.raise_for_status()
                return response.json()
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



    async def paper_relevancy_search(
            self, __event_emitter__,
            query: str,
            limit: Optional[int] = None,
            fields: Optional[str] = None,
            publicationTypes: Optional[str] = None,
            openAccessPdf: Optional[str] = None,
            minCitationCount: Optional[int] = None,
            publicationDateOrYear: Optional[str] = None,
            year: Optional[str] = None,
            venue:Optional[str] = None,
            fieldsOfStudy: Optional[str] = None,
            offset: Optional[int] = None
            ) -> Dict[str, Any]:
        """
        Semantic Scholar Paper Relevance Search Tool

        This tool enables relevance-ranked search for academic papers using the Semantic Scholar API.

        Example usage:
        https://api.semanticscholar.org/graph/v1/paper/search?query=covid&year=2020-2023&openAccessPdf&fieldsOfStudy=Physics,Philosophy&fields=title,year,authors

        Features:
        - Returns a list of papers matching a plain-text query string.
        - Supports filtering by:
        - Publication year or date range (e.g., 2020–2023)
        - Open access availability (PDFs only)
        - Fields of study (e.g., Physics, Philosophy)
        - Publication types (e.g., JournalArticle, Review)
        - Citation count thresholds
        - Specific venues (e.g., Nature, Radiology)

        Response:
        - Includes metadata such as total results, pagination offset, and a list of paper entries.
        - Each paper can include fields like paperId, title, year, authors, citations, references, and embeddings.
        - Supports nested field selection using dot notation (e.g., authors.name, citations.abstract).

        Limitations:
        - Maximum of 1,000 relevance-ranked results per query.
        - Response payloads are limited to 10 MB.
        - No support for advanced query syntax (e.g., Boolean operators).
        - Hyphenated terms may yield no results—use spaces instead.

        Parameters:
        - `query` (required): Plain-text search string.
        - `fields`: Comma-separated list of fields to return (e.g., title,authors,citations.title).
        - `publicationTypes`: Filter by publication type(s).
        - `openAccessPdf`: Include only papers with public PDFs.
        - `minCitationCount`: Minimum number of citations.
        - `publicationDateOrYear`: Date or year range (e.g., 2015:2020).
        - `year`: Publication year or range (e.g., 2016-2020).
        - `venue`: Comma-separated list of publication venues.
        - `fieldsOfStudy`: Comma-separated list of fields of study.
        - `offset`: Pagination offset (default: 0).
        - `limit`: Number of results to return (max: 100).

        For bulk results or larger datasets, consider using the `/search/bulk` endpoint or the Datasets API.

        """
        url = f"{self.base_url}paper/search"

        params = {
            "query": query
            }

        optional_params = {
            "limit": limit,
            "fields": fields,
            "publicationTypes": publicationTypes,
            "openAccessPdf": openAccessPdf,
            "minCitationCount": minCitationCount,
            "publicationDateOrYear": publicationDateOrYear,
            "year": year,
            "venue": venue,
            "fieldsOfStudy": fieldsOfStudy,
            "offset": offset
        }

        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for relevant papers...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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



    async def paper_relevancy_search_batch(
            self, __event_emitter__,
            query: str,
            token: Optional[str] = None,
            fields: Optional[str] = None,
            sort: Optional[str] = None,
            publicationTypes: Optional[str] = None,
            openAccessPdf: Optional[str] = None,
            minCitationCount: Optional[int] = None,
            publicationDateOrYear: Optional[str] = None,
            year: Optional[str] = None,
            venue:Optional[str] = None,
            fieldsOfStudy: Optional[str] = None,
            ) -> Dict[str, Any]:
        """
            Semantic Scholar Bulk Paper Search Tool

        This tool enables efficient bulk retrieval of academic papers using the Semantic Scholar API. It is optimized for high-volume queries where search relevance ranking is not required.

        Example usage:
        https://api.semanticscholar.org/graph/v1/paper/search/bulk?query=covid&fields=venue,s2FieldsOfStudy

        Features:
        - Retrieves up to 1,000 papers per request, with support for pagination via continuation tokens.
        - Supports advanced boolean query syntax for flexible document matching.
        - Filters available for:
        - Publication year or date range
        - Open access PDFs
        - Fields of study
        - Publication types (e.g., JournalArticle, Review)
        - Minimum citation count
        - Specific publication venues

        Query Syntax:
        - Supports boolean operators:
        - `+` for AND
        - `|` for OR
        - `-` to exclude terms
        - `"` for exact phrases
        - `*` for prefix matching
        - `~N` for fuzzy or proximity matching
        - Examples:
        - `"fish ladder"` matches the exact phrase
        - `fish -ladder` matches papers with "fish" but not "ladder"
        - `(fish ladder) | outflow` matches either both "fish" and "ladder" or "outflow"
        - `"fish ladder"~3` matches phrases like "fish is on a ladder"

        Response:
        - Returns a batch of matching papers with an estimated total count and a continuation token (if more results are available).
        - Each paper includes the `paperId` and any additional fields specified in the `fields` parameter.
        - Sorting options include `paperId`, `publicationDate`, and `citationCount`.

        Limitations:
        - Nested data such as citations, references, and embeddings are not available.
        - Maximum of 10 million papers can be retrieved using this method.
        - For full corpus access, use the Datasets API.

        Parameters:
        - `query` (required): Text query matched against title and abstract.
        - `fields`: Comma-separated list of fields to return (e.g., title,venue,year).
        - `token`: Continuation token for paginated results.
        - `sort`: Sorting format `field:order` (e.g., citationCount:desc).
        - `publicationTypes`: Filter by publication type(s).
        - `openAccessPdf`: Include only papers with public PDFs.
        - `minCitationCount`: Minimum number of citations.
        - `publicationDateOrYear`: Date or year range (e.g., 2015:2020).
        - `year`: Publication year or range (e.g., 2016-2020).
        - `venue`: Comma-separated list of publication venues.
        - `fieldsOfStudy`: Comma-separated list of fields of study.

        Use this tool for large-scale academic data extraction where relevance ranking is not required.

        """
        url = f"{self.base_url}paper/search/bulk"

        params = {
            "query": query
            }

        optional_params = {
            "token": token,
            "sort": sort,
            "fields": fields,
            "publicationTypes": publicationTypes,
            "openAccessPdf": openAccessPdf,
            "minCitationCount": minCitationCount,
            "publicationDateOrYear": publicationDateOrYear,
            "year": year,
            "venue": venue,
            "fieldsOfStudy": fieldsOfStudy,
            "sort": sort
        }

        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for batch of relevant papers...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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



    async def paper_title_search(
            self, __event_emitter__,
            query: str,
            fields: Optional[str] = None,
            publicationTypes: Optional[str] = None,
            openAccessPdf: Optional[str] = None,
            minCitationCount: Optional[int] = None,
            publicationDateOrYear: Optional[str] = None,
            year: Optional[str] = None,
            venue:Optional[str] = None,
            fieldsOfStudy: Optional[str] = None,
            ) -> Dict[str, Any]:
        """
        Semantic Scholar Paper Title Match Tool

        This tool retrieves a single academic paper from Semantic Scholar based on the closest title match to a plain-text query.

        Example usage:
        https://api.semanticscholar.org/graph/v1/paper/search/match?query=Construction of the Literature Graph in Semantic Scholar

        Features:
        - Returns the paper with the highest title match score for the given query.
        - If no match is found, the API returns a 404 error with a "Title match not found" message.
        - Each result includes `paperId`, `title`, and `matchScore`, along with any additional fields specified.

        Limitations:
        - Only one paper is returned per query (the best match).
        - No support for advanced query syntax or relevance ranking beyond title similarity.

        Parameters:
        - `query` (required): A plain-text string representing the paper title to match.
        - `fields`: Comma-separated list of fields to include in the response (e.g., title,authors,citations.title).
            - Use dot notation for nested fields (e.g., authors.name, citations.abstract).
            - If omitted, only `paperId` and `title` are returned.
        - `publicationTypes`: Filter by publication type(s) (e.g., JournalArticle, Review).
        - `openAccessPdf`: Restrict results to papers with publicly available PDFs.
        - `minCitationCount`: Minimum number of citations required.
        - `publicationDateOrYear`: Filter by publication date or year range (e.g., 2015:2020).
        - `year`: Filter by publication year or range (e.g., 2016-2020).
        - `venue`: Comma-separated list of publication venues (e.g., Nature,Radiology).
        - `fieldsOfStudy`: Comma-separated list of fields of study (e.g., Physics,Mathematics).

        Use this tool when you need to locate a specific paper by its title with high precision.
        """

        url = f"{self.base_url}paper/search/match"

        params = {
            "query": query
            }

        optional_params = {
            "fields": fields,
            "publicationTypes": publicationTypes,
            "openAccessPdf": openAccessPdf,
            "minCitationCount": minCitationCount,
            "publicationDateOrYear": publicationDateOrYear,
            "year": year,
            "venue": venue,
            "fieldsOfStudy": fieldsOfStudy
        }
    
        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for papers by title...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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



    async def fetch_paper_details(
            self, __event_emitter__, 
            paper_id: str, 
            fields: str
            ) -> Dict[str, Any]:
        """
        Semantic Scholar Paper Details Tool

        This tool retrieves detailed metadata about a specific academic paper using its unique identifier. It supports multiple ID formats and customizable field selection.

        Example usage:
        - https://api.semanticscholar.org/graph/v1/paper/649def34f8be52c8b66281af98ae884c09aef38b
        → Returns the paper's `paperId` and `title`.
        - https://api.semanticscholar.org/graph/v1/paper/649def34f8be52c8b66281af98ae884c09aef38b?fields=url,year,authors
        → Returns `paperId`, `url`, `year`, and a list of authors (each with `authorId` and `name`).
        - https://api.semanticscholar.org/graph/v1/paper/649def34f8be52c8b66281af98ae884c09aef38b?fields=citations.authors
        → Returns `paperId` and citations, each with their own `paperId` and list of authors.

        Supported ID formats:
        - Semantic Scholar SHA: e.g., `649def34f8be52c8b66281af98ae884c09aef38b`
        - CorpusId: e.g., `CorpusId:215416146`
        - DOI: e.g., `DOI:10.18653/v1/N18-3011`
        - ARXIV, MAG, ACL, PMID, PMCID, and URL-based identifiers from supported domains (e.g., arxiv.org, aclweb.org, acm.org, biorxiv.org)

        Parameters:
        - `paper_id` (required): Unique identifier for the paper.
        - `fields`: Comma-separated list of fields to include in the response.
        - If omitted, only `paperId` and `title` are returned.
        - Use dot notation for nested fields (e.g., `authors.name`, `citations.abstract`, `embedding.specter_v2`).
        - Examples:
            - `fields=title,url`
            - `fields=title,authors,citations.title,citations.abstract`

        Limitations:
        - Maximum response size is 10 MB.
        - For large-scale data access, use the Datasets API.

        Use this tool to fetch structured metadata for a specific paper, including authorship, citations, publication details, and more.
        """

        url = f"{self.base_url}paper/{paper_id}"

        params = {}

        optional_params = {
            "fields": fields
        }
    
        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for paper details...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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



    async def fetch_paper_author_details(
            self, __event_emitter__, 
            paper_id: str, 
            offset: Optional[int], 
            limit: Optional[int], 
            fields: Optional[str]
            ) -> Dict[str, Any]:
        """
        Semantic Scholar Paper Author Details Tool

        This tool retrieves detailed information about the authors of a specific academic paper using the Semantic Scholar API.

        Example usage:
        https://api.semanticscholar.org/graph/v1/paper/{paper_id}/authors

        Features:
        - Returns a list of authors associated with the specified paper.
        - Each author includes their `authorId` and `name` by default.
        - Additional fields such as `affiliations`, `url`, and `papers` can be requested.
        - Supports pagination via `offset` and `limit` parameters.

        Advanced Field Selection:
        - Use dot notation to request nested fields within papers (e.g., `papers.year`, `papers.authors.name`).
        - Examples:
        - `fields=name,affiliations,papers`
        - `fields=url,papers.year,papers.authors`

        Supported Paper Identifiers:
        - Accepts multiple ID formats:
        - Semantic Scholar SHA: `649def34f8be52c8b66281af98ae884c09aef38b`
        - Corpus ID: `CorpusId:215416146`
        - DOI: `DOI:10.18653/v1/N18-3011`
        - arXiv: `ARXIV:2106.15928`
        - MAG: `MAG:112218234`
        - ACL: `ACL:W12-3903`
        - PubMed: `PMID:19872477`
        - PubMed Central: `PMCID:2323736`
        - URL: `URL:https://arxiv.org/abs/2106.15928v1`

        Pagination:
        - `offset`: Starting index for results (default: 0).
        - `limit`: Maximum number of authors to return (default: 100, max: 1000).

        Use this tool to explore author metadata, affiliations, and publication history for any paper indexed by Semantic Scholar.
        """
        url = f"{self.base_url}paper/{paper_id}/authors"

        params = {}

        optional_params = {
            "offset": offset,
            "limit": limit,
            "fields": fields
        }
    
        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for paper authors...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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



    async def fetch_paper_citations(
            self, __event_emitter__, 
            paper_id: str, 
            offset: Optional[int], 
            limit: Optional[int], 
            fields: Optional[str],
            publicationDateOrYear: Optional[str]
            ) -> Dict[str, Any]:
        """
        Semantic Scholar Paper Citations Tool

        This tool retrieves detailed information about academic papers that cite a specified paper—i.e., papers in whose bibliography the target paper appears.

        Example usage:
        https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations

        Features:
        - Returns a list of citing papers, each including metadata such as `paperId`, `title`, and optionally:
        - `contexts`: textual context in which the citation appears
        - `intents`: inferred purpose of the citation (e.g., background, method)
        - `isInfluential`: whether the citation is considered influential
        - `abstract`, `authors`, and other fields as requested
        - Supports pagination via `offset` and `limit` parameters
        - Accepts multiple paper ID formats including Semantic Scholar ID, DOI, arXiv ID, PubMed ID, and more

        Limitations:
        - Only metadata about citing papers is returned; nested data such as their own citations or references is not included.
        - Maximum of 1,000 citations per request
        - Up to 10 million citations can be retrieved per paper using this method

        Path Parameters:
        - `paper_id` (required): Identifier of the target paper. Supported formats include:
        - Semantic Scholar ID (e.g., `649def34f8be52c8b66281af98ae884c09aef38b`)
        - DOI (e.g., `DOI:10.18653/v1/N18-3011`)
        - CorpusId, ARXIV, MAG, ACL, PMID, PMCID, or recognized URLs

        Query Parameters:
        - `fields`: Comma-separated list of fields to include in the response (e.g., `contexts,intents,isInfluential,abstract,authors`)
        - `offset`: Starting index for pagination (default: 0)
        - `limit`: Maximum number of results to return (default: 100, max: 1000)
        - `publicationDateOrYear`: Filter citing papers by publication date or year range (e.g., `2015:2020`)

        Use this tool to explore the academic impact and citation network of a specific paper.
        """

        url = f"{self.base_url}paper/{paper_id}/citations"

        params = {}

        optional_params = {
            "limit": limit,
            "fields": fields,
            "publicationDateOrYear": publicationDateOrYear,
        }
    
        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for paper citations...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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



    async def fetch_paper_references(
            self, __event_emitter__, 
            paper_id: str, 
            offset: Optional[int], 
            limit: Optional[int], 
            fields: Optional[str]
            ) -> Dict[str, Any]:
        """
        Semantic Scholar Paper References Tool

        This tool retrieves detailed information about the papers cited by a specific academic paper (i.e., its bibliography) using the Semantic Scholar API.

        Example usage:
        https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references

        Features:
        - Returns a list of references cited by the specified paper.
        - Each reference includes a `citedPaper` object containing at minimum the `paperId` and `title`.
        - Additional metadata such as `contexts`, `intents`, `isInfluential`, `abstract`, and `authors` can be requested.
        - Supports pagination via `offset` and `limit` parameters.

        Advanced Field Selection:
        - Use dot notation to request nested fields within `citedPaper` (e.g., `citedPaper.authors.name`, `citedPaper.abstract`).
        - Examples:
        - `fields=contexts,isInfluential`
        - `fields=contexts,title,authors`

        Supported Paper Identifiers:
        - Accepts multiple ID formats:
        - Semantic Scholar SHA: `649def34f8be52c8b66281af98ae884c09aef38b`
        - Corpus ID: `CorpusId:215416146`
        - DOI: `DOI:10.18653/v1/N18-3011`
        - arXiv: `ARXIV:2106.15928`
        - MAG: `MAG:112218234`
        - ACL: `ACL:W12-3903`
        - PubMed: `PMID:19872477`
        - PubMed Central: `PMCID:2323736`
        - URL: `URL:https://arxiv.org/abs/2106.15928v1`

        Pagination:
        - `offset`: Starting index for results (default: 0).
        - `limit`: Maximum number of references to return (default: 100, max: 1000).

        Use this tool to explore the citation network and bibliographic context of any paper indexed by Semantic Scholar.
        """

        url = f"{self.base_url}paper/{paper_id}/references"

        params = {}

        optional_params = {
            "offset": offset,
            "limit": limit,
            "fields": fields
        }
    
        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for paper references...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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



    async def fetch_author_batch(
            self, __event_emitter__, 
            fields: str, 
            ids: List[str]
            ) -> Dict[str, Any]:
        """
        Semantic Scholar Author Batch Data Tool

        This tool retrieves detailed information for multiple authors simultaneously using the Semantic Scholar API.

        Example usage:
        POST to https://api.semanticscholar.org/graph/v1/author/batch
        Request body: {"ids": ["1741101", "1780531", "48323507"]}
        Query parameter: fields=url,name,paperCount,papers,papers.title,papers.openAccessPdf

        Features:
        - Accepts up to 1,000 author IDs per request.
        - Returns basic metadata such as `authorId` and `name` by default.
        - Additional fields such as `url`, `affiliations`, `paperCount`, and `papers` can be requested.
        - Nested fields within `papers` can be specified using dot notation (e.g., `papers.title`, `papers.authors.name`).

        Parameters:
        - `fields` (query parameter): A comma-separated string specifying which fields to include in the response.
        - This is a single string value, not a list.
        - Examples:
            - `fields=name,affiliations,papers`
            - `fields=url,papers.year,papers.authors`

        Request Body:
        - `ids`: An array of author identifiers.
        - Supported formats include Semantic Scholar author IDs (e.g., "1741101").

        Limitations:
        - Maximum of 1,000 author IDs per request.
        - Response size is limited to 10 MB.

        Use this tool to efficiently retrieve structured metadata for multiple authors, including their publication history and profile details.
        """
        url = f"{self.base_url}author/batch"

        params = {}
        if fields is not None:
            params["fields"] = fields

        data = {}
        if ids is not None:
            data["ids"] = ids

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for batch of authors...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(url, params=params, json=data)
                response.raise_for_status()
                return response.json()
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



    async def author_search(
            self, __event_emitter__, 
            query: str, 
            offset: Optional[int], 
            limit: Optional[int], 
            fields: Optional[str]
            ) -> Dict[str, Any]:

        """
        Semantic Scholar Author Search Tool

        This tool allows you to search for academic authors by name using the Semantic Scholar API.

        Example usage:
        https://api.semanticscholar.org/graph/v1/author/search?query=adam+smith

        Features:
        - Returns a list of authors matching the query string.
        - Each author includes their `authorId` and `name` by default.
        - Additional fields such as `url`, `affiliations`, and `papers` can be requested.
        - Supports pagination and result limiting to optimize performance and reduce latency.

        Advanced Field Selection:
        - Use dot notation to request nested fields within papers (e.g., `papers.title`, `papers.year`, `papers.authors.name`).
        - Examples:
        - `fields=name,affiliations,papers`
        - `fields=url,papers.year,papers.authors`

        Query Behavior:
        - The `query` parameter is a plain-text string matched against author names.
        - No special query syntax is supported.
        - Hyphenated terms may yield no results—use spaces instead.

        Pagination:
        - `offset`: Starting index for results (default: 0).
        - `limit`: Maximum number of authors to return (default: 100, max: 1000).

        Limitations:
        - Maximum response size is 10 MB.
        - If `papers` fields are included, all linked papers for each author will be returned, which may increase response size.

        Use this tool to identify researchers, explore their publication history, and retrieve metadata for academic profiles indexed by Semantic Scholar.
        """
        url = f"{self.base_url}author/search"

        params = {
            "query": query
        }

        optional_params = {
            "offset": offset,
            "limit": limit,
            "fields": fields
        }
    
        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for authors...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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


    async def fetch_author_details(
            self, __event_emitter__, 
            author_id: str, 
            fields: Optional[str]
            ) -> Dict[str, Any]:
        """
        Semantic Scholar Author Details Tool

        This tool retrieves detailed information about a specific academic author using the Semantic Scholar API.

        Example usage:
        https://api.semanticscholar.org/graph/v1/author/{author_id}

        Features:
        - Returns metadata for the specified author, including `authorId` and `name` by default.
        - Additional fields such as `url`, `affiliations`, and `papers` can be requested.
        - When requesting `papers`, you can include nested fields like `papers.title`, `papers.abstract`, and `papers.authors.name`.

        Advanced Field Selection:
        - Use dot notation to specify subfields within papers.
        - Examples:
        - `fields=url,papers`
        - `fields=papers.abstract,papers.authors`

        Parameters:
        - `author_id` (required): The unique identifier for the author. This can be a Semantic Scholar ID (e.g., `1741101`).
        - `fields`: Comma-separated list of fields to include in the response. If omitted, only `authorId` and `name` are returned.

        Limitations:
        - Maximum response size is 10 MB.

        Use this tool to explore an author's profile, publication history, and scholarly contributions indexed by Semantic Scholar.
        """

        url = f"{self.base_url}author/{author_id}"

        params = {}
        if fields is not None:
            params["fields"] = fields

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for author details...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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



    async def fetch_authors_papers(
            self, __event_emitter__, 
            author_id: str, 
            offset: Optional[int], 
            limit: Optional[int], 
            fields: Optional[str], 
            publicationDateOrYear: Optional[str]
            ) -> Dict[str, Any]:
        """
        Semantic Scholar Author Papers Tool

        This tool retrieves a list of academic papers authored by a specific researcher using the Semantic Scholar API.

        Example usage:
        https://api.semanticscholar.org/graph/v1/author/{author_id}/papers

        Features:
        - Returns a paginated list of papers authored by the specified individual.
        - Each paper includes its `paperId` and `title` by default.
        - Additional fields such as `url`, `year`, `abstract`, `authors`, `citations`, and `references` can be requested.
        - Supports filtering by publication date or year range.

        Advanced Field Selection:
        - Use dot notation to request nested fields within papers, citations, or references.
        - Examples:
        - `fields=url,year,authors`
        - `fields=citations.authors`
        - `fields=title,fieldsOfStudy,references`

        Parameters:
        - `author_id` (required): The unique identifier for the author (e.g., Semantic Scholar ID).
        - `publicationDateOrYear`: Filter papers by publication date or year range (e.g., `2015:2020`, `2020-06`).
        - `offset`: Starting index for results (default: 0).
        - `limit`: Maximum number of papers to return (default: 100, max: 1000).
        - `fields`: Comma-separated list of fields to include in the response. If omitted, only `paperId` and `title` are returned.

        Limitations:
        - Only the most recent 10,000 citations and references are included across all papers in the batch.
        - To retrieve full citation data for a specific paper, use the `/paper/{paper_id}/citations` endpoint.
        - Maximum response size is 10 MB.

        Use this tool to explore an author’s publication history, including metadata and citation relationships for each paper.
        """

        url = f"{self.base_url}author/{author_id}/papers"

        params = {
        }

        optional_params = {
            "offset": offset,
            "limit": limit,
            "fields": fields
        }
    
        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for papers from author...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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



    async def fetch_snippet(
            self, __event_emitter__, 
            query: str,
            limit: Optional[int] = None,
            fields: Optional[List[str]] = None,
            paperIds: Optional[List[str]] = None,
            minCitationCount: Optional[int] = None,
            insertedBefore: Optional[str] = None,
            publicationDateOrYear: Optional[str] = None,
            year: Optional[str] = None,
            venue: Optional[List[str]] = None,
            fieldsOfStudy: Optional[List[str]] = None
            ) -> Dict[str, Any]:
        """
        Semantic Scholar Text Snippet Search Tool

        This tool retrieves text excerpts from academic papers that most closely match a plain-text query. Snippets are approximately 500 words and are drawn from the paper’s title, abstract, and body text (excluding figure captions and bibliographies).

        Example usage:
        https://api.semanticscholar.org/graph/v1/snippet/search?query=The literature graph is a property graph with directed edges&limit=1

        Features:
        - Returns the highest-ranked snippet first, along with metadata about the paper it was found in.
        - Each snippet includes:
        - `text`: the matched excerpt
        - `snippetKind`: type of snippet (e.g., abstract, body)
        - `section`: section of the paper
        - `annotations`: sentence and reference mentions
        - `score`: relevance score
        - Paper metadata includes `corpusId`, `title`, `authors`, and `openAccessInfo`.

        Parameters:
        - `query` (required): A plain-text search string. No special query syntax is supported.
        - `limit`: Number of results to return (default: 10, max: 1000).
        - `fields`: Comma-separated list of snippet fields to include (e.g., `snippet.text`, `snippet.snippetKind`, `snippet.annotations.sentences`).
        - Use dot notation for nested fields.
        - Paper metadata and score are always returned and cannot be customized via `fields`.

        Optional Filters:
        - `paperIds`: Comma-separated list of paper identifiers to restrict search scope.
        - Supported formats: SHA, CorpusId, DOI, ARXIV, MAG, ACL, PMID, PMCID, URL
        - `minCitationCount`: Minimum citation count for source papers.
        - `insertedBefore`: Restrict to papers indexed before a specific date (e.g., `2020-01-01`).
        - `publicationDateOrYear`: Filter by publication date or year range (e.g., `2015:2020`, `2020-06`).
        - `year`: Filter by publication year or range (e.g., `2016-2020`).
        - `venue`: Comma-separated list of publication venues (e.g., `Nature,Radiology`).
        - `fieldsOfStudy`: Comma-separated list of fields of study (e.g., `Physics,Mathematics`).

        Limitations:
        - A query string is required.
        - Maximum response size is 10 MB.
        - Not all nested fields are supported in the `fields` parameter.

        Use this tool to extract relevant textual insights from scholarly literature based on natural language queries.
        """

        url = f"{self.base_url}snippet/search"
        params = {
            "query": query
        }

        optional_params = {
            "limit": limit,
            "fields": fields,
            "paperIds": paperIds,
            "minCitationCount": minCitationCount,
            "insertedBefore": insertedBefore,
            "publicationDateOrYear": publicationDateOrYear,
            "year": year,
            "venue": venue,
            "fieldsOfStudy": fieldsOfStudy
        }
    
        params.update({k:v for k,v in optional_params.items() if v is not None})

        await __event_emitter__({
            "type": "status",
            "data": {"description": "Searching for snippets...", "done": False, "hidden": True}
        })

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
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
