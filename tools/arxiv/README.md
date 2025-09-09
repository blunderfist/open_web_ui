# arXiv Search Tool

**Author:** [blunderfist](https://github.com/blunderfist)

**Version:** 1.0.0

**License:** MIT

**GitHub:** [https://github.com/blunderfist/open_web_ui/blob/main/tools/arxiv](https://github.com/blunderfist/open_web_ui/blob/main/tools/arxiv)

**Required Open WebUI Version:** ≥ 0.4.0

## Overview

This tool allows Large Language Models (LLMs) integrated with Open WebUI to seamlessly access and utilize the [arXiv API](https://info.arxiv.org/help/api/user-manual.htm).  It retrieves metadata for academic papers, enabling efficient exploration of cutting-edge research directly within your LLM workflow.  Key features include flexible search parameters, pagination for handling large datasets, and customizable sorting options.

## Features

* **Customizable Search Parameters (UserValves):**  Fine-tune search behavior using configurable parameters, offering greater control and precision.


## Requirements

* `pydantic >= 2.11.4`
* `feedparser >= 6.0.11`

## Usage within Open WebUI

This arXiv Search tool is designed for integration with the Open WebUI platform.  To use it:

1. **Access the Open WebUI Tools Section:**  Navigate to the tools section within your Open WebUI instance.

2. **Create a New Tool:**  Add a new tool.

3. **Paste the Code:** Copy the Python code provided below and paste it into the code editor provided by Open WebUI.

4. **Configure (Optional):** Adjust the `UserValves` parameters within the code to customize your search behavior (see "Advanced Usage" below).  You can leave `use_valves` as `False` to use the default settings defined in `UserValves`.

5. **Save:** Save the tool.


## User Valves Explained

The `UserValves` class provides configurable parameters that control how search queries are executed against the arXiv or Semantic Scholar APIs. These valves allow users to fine-tune the behavior of the search tool, enabling more precise and efficient retrieval of academic content.

## Overview

By default, the tool uses the LLM to generate parameter values based on the prompt. However, when `use_valves` is set to `True`, the following user-defined settings are applied:

---

## 🔧 Valve Parameters

ParameterTypeDefaultDescriptionuse_valvesboolFalseEnables manual control over search parameters. If False, the tool auto-selects optimal values based on the query.| `start`        | `int`    | `0`     | The index of the first result to return (0-based). Useful for paginating through large result sets. |
| `max_results`  | `int`    | `10`    | The maximum number of results to return. Must be ≤ 30,000. Ideal for controlling result volume. |
| `sort_by`      | `str`    | `"relevance"` | Determines how results are sorted. Options include: `"relevance"`, `"lastUpdatedDate"`, and `"submittedDate"`. |
| `sort_order`   | `str`    | `"ascending"` | Specifies the sort direction. Options are `"ascending"` or `"descending"`. |

---

## 💡 Usage Tips

- Set `use_valves = True` to override LLM generated parameter values and apply custom search logic.
- Use `start` and `max_results` together to implement pagination.
- Choose `sort_by` and `sort_order` to prioritize freshness or relevance depending on your research goals.

---

## Example

UserValves(
    use_valves=True,
    start=20,
    max_results=50,
    sort_by="submittedDate",
    sort_order="descending"
)

## Example Output
[
  {
    "id": "https://arxiv.org/abs/2105.07865",
    "title": "...",
    "summary": "...",
    "published": "...",
    // ... other metadata ...
  },
  // ... more papers ...
]


Disclaimer
This tool is provided as-is and without any warranty. Use of this tool is subject to the terms of service of the arXiv API. Always respect the API's rate limits and terms of use.
