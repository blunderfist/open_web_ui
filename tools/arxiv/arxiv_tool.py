"""
title: ArXiv Search
author: blunderfist
git_url: https://github.com/blunderfist/open_web_ui/blob/main/tools/arxiv.py
version: 1.0.0
description: This tool searches ArXiv
required_open_webui_version: 0.4.0
requirements: pydantic>=2.11.4,feedparser>=6.0.11
licence: MIT
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Literal, Optional
import json
import feedparser
from urllib.parse import urlencode


class UserValves(BaseModel):
    # if this is toggled off the model should determine parameters based on the query
    use_valves: bool = Field(
        default = False, description="Use Valves"
    )
    start: int = Field(
        default = 0, 
        description = "The index of the first result to return (0-based). Default is 0."
        )
    max_results: int = Field(
        default = 10, 
        description = "The maximum number of results to return. Default is 10. Must be ≤ 30000."
        )
    sort_by: Literal["relevance", "lastUpdatedDate", "submittedDate"] = Field(
        default = "relevance", 
        description = "Field to sort results by"
        )
    sort_order: Literal["ascending", "descending"] = Field(
        default = "ascending", 
        description = "Sort direction"
        )


class Tools:
    def __init__(self):
        """Initialize the Tool."""
        self.base_url = "http://export.arxiv.org/api/query"
        self.max_retries = 3
        self.user_valves = UserValves()


    async def search(
        self, __event_emitter__, __user__,
        search_query: Optional[str] = None,
        id_list: Optional[str] = None,
        start: Optional[int] = None,
        max_results: Optional[int] = None,
        sort_by: Optional[int] = None,
        sort_order: Optional[int] = None
        ) -> List[Dict[str, Any]]:
        """
        Fetch metadata from the arXiv API using the query interface.

        This function constructs and sends a request to the arXiv API to retrieve metadata about scientific papers. It supports searching by keyword, filtering by arXiv IDs, and paginating through large result sets.

        API Endpoint:
            http://export.arxiv.org/api/query

        Parameters:
            search_query (Optional[str]): A plain-text search query string used to find articles.
                - Example: "all:quantum computing"
                - If provided alone, returns articles matching the query.
                - If used with `id_list`, filters the specified IDs by the query.

            id_list (Optional[str]): A comma delimitted string of arXiv IDs to retrieve specific articles.
                - Example: ["2106.15928", "hep-th/9901001"]
                - If provided alone, returns metadata for the listed articles.
                - If used with `search_query`, returns only matching articles from the list.

            start (int): The index of the first result to return (0-based). Default is 0.
                - Used for pagination.

            max_results (int): The maximum number of results to return. Default is 10.
                - Must be ≤ 30000.
                - For large result sets, use paging with `start` and `max_results`.

            sortBy (Optional[str]): Field to sort results by. Options:
                - "relevance", "lastUpdatedDate", "submittedDate"

            sortOrder (Optional[str]): Sort direction. Options:
                - "ascending", "descending"

        Returns:
            List[Dict]: A list of parsed metadata entries for each paper, including fields like:
                - id (URL), title, summary, published date, authors, categories, and links.

        Notes:
            - The API returns results in Atom XML format, which must be parsed.
            - For large queries, use paging and include a delay (e.g., 3 seconds) between requests.
            - Requests with `max_results > 30000` will result in an HTTP 400 error.
            - For bulk harvesting, consider using the OAI-PMH interface instead.

        Example:
            search_arxiv(
                search_query="ti:\"electron thermal conductivity\"",
                sortBy="lastUpdatedDate",
                sortOrder="ascending",
                max_results=5
            )
        """

        params = {}
        optional_params = {
            "search_query": search_query,
            "id_list": id_list
        }

        if self.user_valves.use_valves:
            optional_params.update({
                "start": start,
                "max_results": max_results,
                "sortBy": sort_by,
                "sort_order": sort_order
            })
        else:
            optional_params["start"] = self.user_valves.start
            optional_params["max_results"] = self.user_valves.max_results
            optional_params["sortBy"] = self.user_valves.sort_by
            optional_params["sortOrder"] = self.user_valves.sort_order

        params.update({k:v for k,v in optional_params.items() if v is not None})
        query_string = urlencode(params)
        url = f"{self.base_url}?{query_string}"

        await __event_emitter__({
            "type": "status",
            "data": {"description": f"Searching ArXiv with the following parameters {params}", 
                     "done": False, # Displayed while search is being run
                     "hidden": True} # True removes message after chat compeletion
        })

        attempt = 0
        while attempt < self.max_retries:
            try:
                feed = feedparser.parse(url)
                papers = []
                for entry in feed.entries:
                    paper = {
                        "id": entry.get("id"),
                        "title": entry.get("title"),
                        "summary": entry.get("summary"),
                        "published": entry.get("published") if hasattr(entry, "published") else None,
                        "updated": entry.get("updated") if hasattr(entry, "updated") else None,
                        "authors": [author.name for author in entry.authors] if hasattr(entry, "authors") else None,
                        "categories": [tag.term for tag in entry.tags] if hasattr(entry, "tags") else None,
                        "doi": entry.get("arxiv_doi") if hasattr(entry, "arxiv_doi") else None,
                        "journal_ref": entry.get("arxiv_journal_ref") if hasattr(entry, "arxiv_journal_ref") else None,
                        "comment": entry.get("arxiv_comment") if hasattr(entry, "arxiv_comment") else None,
                        "primary_category": entry.get("arxiv_primary_category", {}).get("term") if hasattr(entry, "arxiv_primary_category") else None,
                        "affiliation": entry.get("arxiv_affiliation") if hasattr(entry, "arxiv_affiliation") else None,
                        "links": [link.href for link in entry.links] if hasattr(entry, "links") else None
                    }
                    # Fix: .items is a method, so you need to call it
                    papers.append({k: v for k, v in paper.items() if v is not None})

                return json.dumps(papers, indent=2)

            except Exception as e:
                await __event_emitter__({
                    "type": "status",
                    "data": {"description": f"Exception: {e}", "done": False, "hidden": True}
                })
                attempt += 1

        return json.dumps({"error": "Failed to fetch data after multiple attempts."}, indent=2)
