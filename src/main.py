# For STDIO servers never use print() to console log errors as this
# writes to STDOUT which will corrupt the JSON-RPC messages!
# Use an HTTPX Client to share config across requests also more performant.
# fastmcp uses Python type hints and docstrings to
# automatically generate tool definitions.
#

from typing import Any
from fastmcp import FastMCP
import os
import httpx
import asyncio
import sys
import sqlite3
import catalogue




token        = os.getenv("T212_CREDS_DEMO")
mcp          = FastMCP("Trading212 Account Management MCP Server",
                       instructions="Provides tools for retrieving account data and managing stock portfolio. Start with get_account_summary() an overview.",
                       version="1.0.0",
                       )
                      
BASE_API_URL = 'https://demo.trading212.com/api/v0/'

# Tools
# Helper functions to make requests to the T212 api
async def make_t212_req(url: str) -> dict[str, Any] | None:
    """Make a get request to the trading212 API with error handling"""

    if not token:
        print("Error: Auth Token invalid or missing", file=sys.stderr)
        # Throw an error
    else:
        headers = {'Authorization': f'Basic {token}'}


    async with httpx.AsyncClient() as client: 
        try: 
            res = await client.get(url, headers=headers, timeout=10.0)
            res.raise_for_status()
            return res.json()
        except Exception:
            return None


async def make_t212_post(url: str, payload: [str, Any]) -> dict[str, Any] | None:
    """Make a post request to the trading212 API with error handling"""

    if not token:
        print("Error: Auth Token invalid or missing", file=sys.stderr)
        # Throw an error
    else:
        headers = {'Authorization': f'Basic {token}'}


    async with httpx.AsyncClient() as client: 
        try: 
            res = await client.post(url,json=payload, headers=headers, timeout=10.0)
            res.raise_for_status()
            return res.json()
        except Exception:
            return None


async def make_t212_del(url: str) -> dict[str, Any] | None:
    """Make a delete request to the trading212 API with error handling"""

    if not token:
        print("Error: Auth Token invalid or missing", file=sys.stderr)
        # Throw an error
    else:
        headers = {'Authorization': f'Basic {token}'}


    async with httpx.AsyncClient() as client: 
        try: 
            res = await client.delete(url, headers=headers, timeout=10.0)
            res.raise_for_status()
            return res.json()
        except Exception:
            return None

@mcp.tool(
    name        = "get_account_summary",
    description = "request a breakdown of your account cash and investment metrics.",
    tags        = {"account","summary"}
)
async def get_account_summary() -> dict[str, Any] | None:
    """Provides a breakdown of the user's cash and investements metrics,
       such as available funds, inested capital and total account value."""

    url = f"{BASE_API_URL}equity/account/summary"
    response = await make_t212_req(url)
    return response

    if not response:
        return "Mission Failed"

@mcp.tool(
    name        = "get_all_exchanges",
    description = "request a list of all available exchanges.",
    tags        = {"catalogue","search"}
)
async def get_exchanges(limit: int | None) -> dict[str, Any] | None:
    """Get All Exchanges"""

    url = f"{BASE_API_URL}equity/metadata/exchanges"
    response = await make_t212_req(url)
    return response

    if not response:
        return "Mission Failed"

@mcp.tool(
    name        = "get_instrument",
    description = "Use a company name to search for an it's ticker symbols.",
    tags        = {"catalogue","search"}
)
async def get_instrument(company_name: str) -> Any | None:
    """Queries the database using the company name and gets the company ticker. 
    Used in conjunction with placing orders."""
    # Open a connection
    connection = sqlite3.connect('stocks.db')

    # create a cursor
    cursor = connection.cursor()

    res = cursor.execute(f"SELECT company_name, company_ticker FROM stocks WHERE company_name = '{company_name.lower()}'")
    rows = res.fetchall()
    print(rows)
    return rows
    connection.close()


@mcp.tool(
    name        = "get_all_transactions",
    description = "Use a company name to search for an it's ticker symbols.",
    tags        = {"account","transactions"}
)

async def get_all_transactions() -> str:
    """Get All Transactions"""
    url = f"{BASE_API_URL}equity/history/transactions"
    response = await make_t212_req(url)
    return response

    if not response:
        return "Mission Failed"


@mcp.tool(
    name        = "get_open_positions",
    description = "Return a list of all open positions",
    tags        = {"account","open_positions"}
)

async def get_open_positions(ticker: str, country_code: str) -> dict[str, Any] | None:
    """Get all open positions
      This function takes two optional strings, ticker and country_code
      You can specify the ticker symbol for a specific stock if required.
      Make sure to add "US" if it's an american company.
       Args: 
            (optional) ticker: the ticker symbol for the position you are tryng to fetch.
            (optional) country_code: two letter symbol "US" for American stocks. Currently other stocks do not require a country code. 
       """

    url = f"{BASE_API_URL}equity/positions"

    if ticker and country_code:
        url += f"?ticker={ticker}_{country_code}_EQ"

    elif ticker and not country_code:
        url += f"?ticker={ticker.upper()}l_EQ"
 
    response = await make_t212_req(url)
    return response

    if not response:
        return "Mission Failed"


@mcp.tool(
    name        = "get_open_orders",
    description = "Get all open orders",
    tags        = {"account","open_orders"}
)

async def get_all_pending_orders() -> list[dict[str, Any]] | None:
    """Retrieves a list of all orders that are currently active.
       Useful for monitoring the status of open positions
       Make sure to keep a note of the id as that can be used to cancel the order"""
    url = f"{BASE_API_URL}equity/orders"
    response = await make_t212_req(url)
    return response

    if not response:
        return "Mission Failed"

@mcp.tool(
    name        = "place_limit_order",
    description = "Place a limit order",
    tags        = {"account","place_limit_order"}
)

async def place_limit_order(limitPrice: float, quantity: float, ticker: str, country_code: str | None, timeValidity: str) -> dict[str, Any] | None:
    """Create a new limit order which executes at a specified price or better.
       
       To place a sell order, use a negative 'quantity' value. The order will fill at the 'limitPrice' or higher 

       You can specify the ticker symbol for a specific stock if required.
       Make sure to add "US" if it's an american company.

        Args: 
            limitPrice: To place a limit order, use a postive 'quantity' value. The order will fill at the 'limitPrice' or lower.
            quantity: The amount of shares to buy, can be fractional (float)
            ticker: the ticker symbol for the stock you with to place a limit order for.
            country_code: two letter symbol "US" for American stocks. Currently other stocks do not require a country code.
            timeValidity: Specifies how long the order will remain active. 
                    Set to "DAY" for the order to expire if not executed by midnight. 
                    Set to "GOOD_TILL_CANCEL" for the order to remain active indefinitely

       """
    url = f"{BASE_API_URL}equity/orders/limit"
    
    payload = {
        "limitPrice": limitPrice,
        "quantity": quantity,
        "ticker": f"{ticker}_{country_code}_EQ" if ticker and country_code else f"{ticker}l_EQ",
        "timeValidity": f"{timeValidity}"
    }

    response = await make_t212_post(url, payload)
    return response

    if not response:
        return "Mission Failed"

@mcp.tool(
    name        = "cancel_pending_order",
    description = "Cancel a pending open order",
    tags        = {"account","cancel_pending_order"}
)

async def cancel_pending_order(unique_id:int) -> dict[str, Any] | None:
    """Attempts to cancel a pending order by its unique ID a successful response indicates
       the cancellation request was accepted.

        Args: 
            unique_id: The unique identifier of the order you want to cancel.
       """
    url = f"{BASE_API_URL}equity/orders/{unique_id}"

    response = await make_t212_del(url)
    if response:
        return {"status": "success", "detail": "Order cancelled"}

    if not response:
        return {"status":"Mission Failed"}


if __name__ == "__main__":
    catalogue.populate_db()
    mcp.run(
        host      = "0.0.0.0",
        port      = 42070,
        transport = "http"    
    )
