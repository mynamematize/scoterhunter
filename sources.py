"""
Source adapter placeholder.

Do not assume OLX permits unrestricted scraping. Before implementing automated
collection, verify OLX's current terms, robots/access restrictions, and whether
an official or otherwise permitted feed/API is available for the target category.
Keep this module separate from the Telegram bot so the data source can be replaced.
"""

async def scan_olx():
    # TODO: connect a permitted data source and normalize its results into:
    # {"url": ..., "title": ..., "price": ..., "location": ..., "description": ...}
    return []
