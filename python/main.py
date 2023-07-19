import json
from collections import defaultdict
from datetime import datetime, timedelta
from os import environ, path
from pathlib import Path
from pprint import pprint

import requests
from retry import retry

from tt.simple_json_file_cache import SimpleJSONFileCache

API_URL = "https://api.tokenterminal.com"
API_KEY = environ["API_KEY"]
MINUTE_IN_SECS = 60
CACHE_DIR = Path("/tmp").joinpath(
    f"tt-api-cache-{datetime.now().strftime('%Y-%m-%d-%H')}"
)

cache = SimpleJSONFileCache(CACHE_DIR)


class RateLimitError(Exception):
    pass


@retry(RateLimitError, tries=10, delay=1, backoff=2, max_delay=60)
def GET(path: str):
    """GET request to TT API for a given path with rate limiting and retrying."""
    # Check if exists in cache
    if path in cache and cache[path] is not None:
        return cache[path]

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] GET {path}", flush=True)
    response = requests.get(
        API_URL + path, headers={"authorization": f"Bearer {API_KEY}"}
    )

    if response.status_code == 429:
        print(response.text)
        raise RateLimitError("too many calls")

    if response.status_code != 200:
        print(f"expected response 200, got {response.status_code}: {response.text}")
        raise Exception(response.text)

    data = response.json()["data"]
    cache[path] = data
    return cache[path]


def projects_by_market_sector():
    """Return a dict of market sector to list of projects."""
    _projects_by_market_sector = defaultdict(list)
    projects = GET("/v2/projects")
    for project in projects:
        project = GET(project["url"])
        market_sectors = project["market_sectors"]
        for market_sector in market_sectors:
            _projects_by_market_sector[market_sector].append(project)
    return _projects_by_market_sector


def main():
    all_projects_by_market_sector = projects_by_market_sector()

    # Select projects from Blockchain L1 market sector that have fees available
    l1_projects_with_fees = [
        x
        for x in all_projects_by_market_sector["blockchains-l1"]
        if x["metric_availability"]["fees"] == True
    ]

    # Get fees for each project
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    fees = []
    for projects in chunks(l1_projects_with_fees, 20):
        project_ids = ",".join([x["project_id"] for x in projects])
        path = f"/v2/metrics/fees?start={yesterday}&project_ids={project_ids}"
        metrics = GET(path)
        fees.extend(metrics)

    pprint(fees)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


if __name__ == "__main__":
    main()
