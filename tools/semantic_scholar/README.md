# Semantic Scholar Search Tool for Open Web UI
This repository contains a Python script designed as a tool for the Open Web UI, providing access to the Semantic Scholar API. This tool allows users to search for academic papers and authors, retrieve detailed metadata, and extract text snippets.

## Features
- Paper Search: Search for papers using various criteria including keywords, publication year, publication type, and more. Supports both relevance-ranked search and bulk search for large-scale data retrieval. Includes options for specifying fields to return.
- Paper Details: Retrieve detailed information about a specific paper given its ID, including authors, citations, references, and more.
- Author Search: Search for authors by name and retrieve their publication history.
- Author Details: Get detailed information about a specific author using their ID.
- Batch Processing: Efficiently retrieve information for multiple papers or authors in a single request.
- Snippet Extraction: Extract relevant text snippets from papers based on a query string.
- Progress Indication: Displays progress messages during API calls within the Open Web UI.

## Requirements
`Python 3.7+`
`pydantic>=2.11.4`
`httpx>=0.28.1`

## Open Web UI Integration
This tool is designed to be integrated with Open Web UI version 0.4.0 or later. You'll need to place the semantic_scholar.py file in the appropriate Open Web UI tools directory and configure the UI to utilize this tool. Refer to the Open Web UI documentation for specific instructions on adding custom tools.

## Usage
The tool exposes several functions, each corresponding to a specific Semantic Scholar API endpoint. The parameters for each function are clearly documented within the code itself. Key functions include:

- fetch_paper(query, limit, fields, ...): Searches for papers based on a query.
- fetch_papers_batch(ids, fields): Retrieves details for multiple papers given their IDs.
- fetch_paper_details(paper_id, fields): Retrieves detailed information for a single paper.
- fetch_author_details(author_id, fields): Retrieves detailed information for a single author.
- fetch_authors_papers(author_id, ...): Retrieves a list of papers authored by a given author.
- fetch_snippet(query, ...): Retrieves text snippets matching a query.

## API Key
This script does not require an API key

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer
This tool is provided as-is and without any warranty. Use of this tool is subject to the terms of service of the Semantic Scholar API. Always respect the API's rate limits and terms of use.
