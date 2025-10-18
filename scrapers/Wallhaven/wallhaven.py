import json
import requests
import sys

from py_common.util import scraper_args
from py_common import log
from py_common.deps import ensure_requirements

ensure_requirements("cloudscraper", "lxml")

import cloudscraper  # noqa: E402

# FIxME how to pull in configured user agent?
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0'
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language' :'en-US,en;q=0.5',
    'Priority': 'u=0, i',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-GPC': '1',
    'TE': 'trailers',
    'Upgrade-Insecure-Requests': '1'
}
EXTRA_GET_HEADERS = {
    'Sec-Fetch-Site': 'none',
}
EXTRA_POST_HEADERS = {
    'Sec-Fetch-Site': 'same-origin',
}

# FIXME what about enabled authentication?
# FIXME need better aproach than hard-coding server URL
SERVER_BASE_URL = 'http://localhost:9999'

def fetch_image_thumbnail(image_id: str) -> bytes | None:
    response = requests.get(f"{SERVER_BASE_URL}/image/{image_id}/thumbnail")
    if response.status_code == 200:
        return response.content
    else:
        return None

#
# main
#

input = sys.stdin.read()
FRAGMENT = json.loads(input)
log.trace(f"fragment: {FRAGMENT}")

if "imageByFragment" in sys.argv:
    log.debug("invoked imageByFragment")
    
    ret = {}
    
    thumbnail = fetch_image_thumbnail(FRAGMENT['id'])

    if thumbnail is not None:
        scraper = cloudscraper.create_scraper()
        response = scraper.get("https://wallhaven.cc/")
        if response.status_code != 200:
            raise RuntimeError(f"unexpected response status {response.status_code} to {response.request}")
        log.debug(f"cookies after page request: {scraper.cookies}")

        response2 = scraper.post("https://wallhaven.cc/search", files={
            'q': (None, '', None),
            'search_image': ('thumbnail.jpg', thumbnail, 'image/jpeg'),
        }, headers={'Referer':'https://wallhaven.cc/latest'})

        # FIXME always fails right now, with error 419 (session expired)
        if response2.status_code != 200:
            log.debug(f"cookies after search request: {scraper.cookies}")
            log.debug(f"request headers: {response2.request.headers}")
            log.debug(f"response headers: {response2.headers}")
            raise RuntimeError(f"unexpected response status {response2.status_code} to {response2.request}")
        
        log.trace(f"response text: {response2.text}")

        # FIXME actual logic called here
        raise RuntimeError("sucess not acutally implemented yet")

    if len(ret) > 0:
        print(json.dumps(ret))
        sys.exit(0)
    else:
        print(json.dumps({}))
        sys.exit(1)

else:
    log.error("no supported command detected")
    print(json.dumps({}))
    sys.exit(255)

print(json.dumps({}))
sys.exit(1)
