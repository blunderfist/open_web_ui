"""
title: Datetime Tool
author: blunderfist
git_url: https://github.com/blunderfist/open_web_ui/blob/main/tools/datetime/datetime_tool.py
version: 1.0.0
description: This tool returns the current dateime
required_open_webui_version: 0.4.0
requirements: pydantic>=2.11.4,pytz>=2025.2
licence: MIT No Attribution
"""

from datetime import datetime
import pytz  # It's good practice to include timezone
from pydantic import BaseModel, Field

# --- User Valves ---
class UserValves(BaseModel):
	set_datetime: bool = Field(
		default = True, description = "Set tool use"
	)

# --- Tools Class ---
class Tools:
    def __init__(self):
        """Initialize the Tool with user-controlled valves."""
        # Eastern Daylight Time (EDT)
        self.timezone = pytz.timezone("US/Eastern") # modify as needed
        self.user_valves = UserValves()

    def get_current_datetime(self):
        """
        Returns the current date, time, and timezone.
        Use this tool to get the ground truth for the current moment.
        """
        now = datetime.now(self.timezone)
        return now.strftime("%A, %B %d, %Y at %I:%M:%S %p %Z")
