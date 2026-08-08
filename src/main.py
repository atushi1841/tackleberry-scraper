import json
import os
import random
import re
import sys
import time
from urllib.parse import urlencode, urljoin

import httpx

try:
    from apify import Actor
except ImportError:
    Actor = None

BASE_URL = "https://b-net.tackleberry.co.jp"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def build_url(keyword=None, category_id=None, page=1):
    if keyword:
        query = urlencode({"name": keyword})
        url = f"{BASE_URL}/products/list?{query}"
    elif category_id is not None:
        url = f"{BASE_URL}/products/list?sale_type[]=3&category_id={category_id}"
    else:
        raise ValueError("keyword or categoryId is required")
    if page > 1:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}pageno={page}"
    return url


def get_proxy(proxy_config):
    if not proxy_config:
        return None
    if proxy_config.get("proxyUrls"):
        return proxy_config["proxyUrls"][0]
    if proxy_config.get("useApifyProxy"):
        return (
            os.environ.get("HTTP_PROXY")
            or os.environ.get("HTTPS_PROXY")
            or os.environ.get("http_proxy")
            or os.environ.get("https_proxy")
        )
    return None


def fetch_page(url, proxy):
    for attempt in range(3):
        try:
            with httpx.Client(proxy=proxy, timeout=30, follow_redirects=True) as client:
                resp = client.get(url, headers={"User-Agent": UA})
                resp.raise_for_status()
                return resp.text
        except Exception as exc:
            if attempt == 2:
                raise
            wait = 2 ** attempt + random.uniform(0, 1)
            time.sleep(wait)
    raise RuntimeError("should not reach")


def get_total_pages(html):
    m = re.search(r"全\s*(\d+)\s*ページ", html)
    if m:
        return int(m.group(1))
    matches = re.findall(r"pageno=(\d+)", html)
    if matches:
        return max(int(x) for x in matches)
    return 1


def clean_text(value):
    if not value:
        return ""
    return re.sub(r"<[^>]+>", "", value).strip()


def extract_number(value):
    if not value:
        return None
    digits = re.sub(r"[^\d]", "", value)
    if not digits:
        return None
    return int(digits)


def parse_cards(html, category_id, is_used_hint=False):
    base = BASE_URL
    results = []
    pattern = r'<a[^>]*class=["\']prod__main__list__item__link["\'][^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
    for m in re.finditer(pattern, html, re.DOTALL | re.I):
        href = m.group(1)
        inner = m.group(2)

        product_id_match = re.search(r"/products/detail/(\d+)", href)
        if not product_id_match:
            continue
        product_id = product_id_match.group(1)

        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', inner, re.I)
        alt_match = re.search(r'<img[^>]+alt=["\']([^"\']*)["\']', inner, re.I)
        title_match = re.search(
            r'<div[^>]*class=["\']prod__main__list__item__link__title["\'][^>]*>(.*?)</div>',
            inner,
            re.DOTALL | re.I,
        )
        price_match = re.search(
            r'<span[^>]*class=["\']price02-default["\'][^>]*>([^<]+)</span>',
            inner,
            re.I,
        )
        regular_match = re.search(r"<s>([^<]+)</s>", inner, re.I)
        discount_match = re.search(
            r'<span[^>]*class=["\']-discount["\'][^>]*>([^<]+)</span>',
            inner,
            re.I,
        )

        img_src = img_match.group(1) if img_match else None
        image_url = urljoin(base, img_src) if img_src else None

        name = alt_match.group(1).strip() if alt_match else None
        title = clean_text(title_match.group(1)) if title_match else None
        price = extract_number(price_match.group(1) if price_match else "")
        regular = extract_number(regular_match.group(1) if regular_match else "")
        discount_raw = discount_match.group(1) if discount_match else ""
        discount_rate = extract_number(discount_raw)

        text_inner = re.sub(r"<[^>]+>", " ", inner).lower()
        is_used = is_used_hint or "中古" in text_inner or "used" in text_inner
        is_sold_out = any(
            term in text_inner
            for term in ["soldout", "品切れ", "在庫なし", "売り切れ", "在庫切れ"]
        )
        in_stock = not is_sold_out

        product_url = urljoin(base, href)

        results.append(
            {
                "productId": product_id,
                "title": title,
                "name": name,
                "price": price,
                "regularPrice": regular,
                "discountRate": discount_rate,
                "imageUrl": image_url,
                "productUrl": product_url,
                "isUsed": is_used,
                "categoryId": category_id,
                "inStock": in_stock,
            }
        )
    return results


def scrape(keyword=None, category_id=None, max_items=100, proxy=None):
    page = 1
    all_items = []
    total_pages = 1

    while len(all_items) < max_items:
        page_url = build_url(keyword=keyword, category_id=category_id, page=page)
        page_html = fetch_page(page_url, proxy)

        if page == 1:
            total_pages = get_total_pages(page_html)

        items = parse_cards(
            page_html,
            category_id=category_id,
            is_used_hint=category_id is not None,
        )
        if not items:
            break

        all_items.extend(items)

        if page >= total_pages:
            break

        page += 1
        if page > 1:
            time.sleep(random.uniform(1, 3))

    return all_items[:max_items]


def _read_input_legacy():
    raw = os.environ.get("APIFY_INPUT")
    if not raw and len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            raw = f.read()
    if not raw:
        raw = sys.stdin.read()

    try:
        user_input = json.loads(raw or "{}")
    except json.JSONDecodeError:
        user_input = {}
    return user_input


async def _run_actor():
    async with Actor:
        input_data = await Actor.get_input() or {}
        keyword = input_data.get("keyword")
        category_id = input_data.get("categoryId")
        max_items = int(input_data.get("maxItems") or 100)
        proxy_input = input_data.get("proxyConfiguration")
        proxy_url = None
        if proxy_input:
            proxy_config = await Actor.create_proxy_configuration(actor_proxy_input=proxy_input)
            proxy_url = await proxy_config.new_url() if proxy_config else None
        try:
            data = scrape(
                keyword=keyword,
                category_id=category_id,
                max_items=max_items,
                proxy=proxy_url,
            )
            for item in data:
                await Actor.push_data(item)
        except Exception as exc:
            Actor.log.exception("Scraping failed: %s", exc)
            raise


def main():
    if Actor is not None:
        import asyncio
        asyncio.run(_run_actor())
        return 0
    # Legacy fallback (no Apify SDK)
    user_input = _read_input_legacy()
    keyword = user_input.get("keyword")
    category_id = user_input.get("categoryId")
    max_items = int(user_input.get("maxItems") or 100)
    proxy_config = user_input.get("proxyConfig") or user_input.get("proxyConfiguration")
    proxy = get_proxy(proxy_config)
    try:
        data = scrape(
            keyword=keyword,
            category_id=category_id,
            max_items=max_items,
            proxy=proxy,
        )
        for item in data:
            print(json.dumps(item, ensure_ascii=False))
        return 0
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
