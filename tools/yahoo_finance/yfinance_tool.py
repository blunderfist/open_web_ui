"""
title: Yahoo Finance Tool
author: blunderfist
git_url: https://github.com/blunderfist/open_web_ui/blob/main/tools/yahoo_finance/yfinance_tool.py
version: 1.0.0
description: This tool searches Yahoo Finance using the yfinance library
required_open_webui_version: 0.4.0
requirements: pydantic>=2.11.4,yfinance,pandas
licence: MIT
"""

import yfinance as yf
import json
from datetime import datetime, timedelta
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import pandas as pd

# --- User Valves ---
class UserValves(BaseModel):
	include_dividends: bool = Field(
		default=True, description="Include dividend payouts in historical data"
	)
	include_splits: bool = Field(
		default=True, description="Include stock splits in historical data"
	)
	auto_adjust: bool = Field(
		default=False, description="Automatically adjust prices for splits and dividends"
	)
	include_prepost: bool = Field(
		default=False, description="Include pre-market and after-hours trading data"
	)

# --- Tools Class ---
class Tools:
	def __init__(self, user_valves: Optional[UserValves] = None):
		"""Initialize the Tool with user-controlled valves."""
		self.user_valves = user_valves or UserValves()


	def make_json_serializable(self, obj):
		"""Recursively convert any non-JSON-serializable objects (like Timestamps) to strings."""
		if isinstance(obj, pd.DataFrame):
			df = obj.copy()
			df.index = df.index.tz_convert("US/Eastern").tz_localize(None) if df.index.tz else df.index
			df.reset_index(inplace=True)
			df.rename(columns={"index": "Datetime"}, inplace=True)
			for col in df.columns:
				if pd.api.types.is_datetime64_any_dtype(df[col]):
					df[col] = df[col].astype(str)
			return df.to_dict(orient="records")
		elif isinstance(obj, pd.Series):
			return obj.apply(lambda x: str(x) if pd.api.types.is_datetime64_any_dtype(x) else x).to_dict()
		elif isinstance(obj, dict):
			return {k: self.make_json_serializable(v) for k, v in obj.items()}
		elif isinstance(obj, list):
			return [self.make_json_serializable(v) for v in obj]
		else:
			return obj


	async def fetch_single_ticker(self, __event_emitter__, ticker, start_date, end_date, data_type, period, interval, extra):
		await __event_emitter__({"type": "status", "data": {"description": f"Fetching {ticker} ({data_type})...", "done": False}})

		t = yf.Ticker(ticker)
		try:
			kwargs = {"interval": interval, "actions": self.user_valves.include_dividends or self.user_valves.include_splits,
						"auto_adjust": self.user_valves.auto_adjust, "prepost": self.user_valves.include_prepost}
			if data_type == "history":
				# do not use start, end and period, choose <= 2 e.g.(end and period or just period)
				if start_date and end_date:
					kwargs["start"] = start_date
					kwargs["end"] = end_date
				elif start_date and period:
					kwargs["start"] = start_date
					kwargs["period"] = period
				elif end_date and period:
					kwargs["end"] = end_date
					kwargs["period"] = period
				elif period:
					kwargs["period"] = period
				else: #Defaults to yesterday and day before yesterday if neither provided
					kwargs["start"] = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
					kwargs["end"] = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

				data = t.history(**kwargs)
			elif data_type in ["info", "fast_info", "financials", "balance_sheet", "cashflow"]:
				data = getattr(t, data_type)()
				if data_type == "fast_info": data = dict(data)
			else:
				return {ticker: {"error": f"Unknown data_type '{data_type}'"}}

			if extra and hasattr(t, extra):
				extra_data = getattr(t, extra)
				if hasattr(extra_data, "to_json"):
					extra_data = json.loads(extra_data.to_json(orient="records", date_format="iso"))
				data = {"main": data, extra: extra_data}
			data = self.make_json_serializable(data)
			await __event_emitter__({"type": "status", "data": {"description": f"Fetched {ticker} successfully", "done": True}})
			return {ticker: data}
		except Exception as e:
			await __event_emitter__({"type": "status", "data": {"description": f"Error fetching {ticker}: {e}", "done": True}})
			return {ticker: {"error": str(e)}}



	async def fetch_yfinance_data(
		self, __event_emitter__,
		tickers: List[str],
		start_date: str = None,
		end_date:str = None,
		data_type: str = "history",
		period: str = None,
		interval: str = "1d",
		extra: Optional[str] = None
	) -> str:
		"""
		Fetch data from yfinance for one or more tickers asynchronously.

		Parameters:
			tickers (List[str]): List of stock ticker symbols.
			data_type (str): Type of data to fetch. Options:
				- "history": Historical data (default)
				- "info": Full company info
				- "fast_info": Lightweight info (faster)
				- "financials": Income statement
				- "balance_sheet": Balance sheet
				- "cashflow": Cash flow statement
			start_date (str): Starting date for data. Format YYYY - MM - DD e.g("2023 - 01 - 01")
			end_date (str): Ending date for data. Format YYYY - MM - DD e.g("2023 - 01 - 02")
			historical_data = apple.history(start = start_date, end = end_date)		period: str = "1mo",
			period (str): Used only if data_type="history" and not (start_date and end_date) supplied. Controls how far back the data goes (e.g., "1mo", "6mo", "1y", "5y", "max").
			interval (str): Interval for historical data.
				examples of intervals:
					"2m": 2 minutes
					"15m": 15 minutes
					"90m": 1.5 hours
					"1d": 1 day (default)
					"5d": 5 days
					"1wk": 1 week
					"3mo": 3 months
			extra (str): Optional parameter for sub-fields (e.g., "dividends", "splits").
				dividends         # Series of dividend payouts
				splits            # Series of stock splits
				capital_gains     # Capital gains (if available)
				actions           # DataFrame with Dividends + Splits
				earnings_dates    # Upcoming and past earnings reports
				financials        # Income statement
				balance_sheet     # Balance sheet
				cashflow          	  # Cash flow statement
				institutional_holders # institutional holders
				major_holders 		  # major holders
				mutualfund_holders 	  # mutual fund holders

		Note: Do not use start_date, end_date, and period.
			Choose from the following selections
				period
				period and (start_date or end_date)
				start_date and end_date
		Returns:
			str: JSON-formatted string containing data for all requested tickers.
		"""

		await __event_emitter__({
			"type": "status",
			"data": {"description": f"Fetching {data_type} for {len(tickers)} tickers...", "done": False}
		})

		tasks = [
			self.fetch_single_ticker(__event_emitter__, t, start_date, end_date, data_type, period, interval, extra)
			for t in tickers
		]
		results = await asyncio.gather(*tasks)
		combined = {}
		for r in results:
			combined.update(r)

		await __event_emitter__({
			"type": "status",
			"data": {"description": "Stock data retrieved successfully", "done": True, "hidden": False}
		})

		return json.dumps(combined, indent=2)
