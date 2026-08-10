# Tackleberry B-net Japan Fishing Tackle Scraper

Extract product data from **@Berry Net** (タックルベリーB-net), one of Japan's largest new & used fishing tackle marketplaces — capture JDM reels, rods, and lures in real time.

## Output Sample

```json
{
  "productId": "1234888",
  "title": "エメラルダスXボート65LS-S・E",
  "name": "エメラルダスXボート65LS-S・E",
  "price": 15246,
  "regularPrice": 21780,
  "discountRate": 30,
  "imageUrl": "https://b-net.tackleberry.co.jp/html/upload/save_image/no_image_product.png",
  "productUrl": "https://b-net.tackleberry.co.jp/products/detail/1234888",
  "isUsed": true,
  "categoryId": 12,
  "inStock": true
}
```

## Input

| Field | Type | Description |
|-------|------|-------------|
| `keyword` | string | Search keyword, e.g. `シマノ`, `アンタレス`, `ロッド` |
| `categoryId` | integer | Category ID from the category URL |
| `maxItems` | integer | Maximum number of results to return (default: 100) |
| `proxyConfiguration` | object | Apify proxy configuration |

*You must provide either `keyword` or `categoryId`.*

## Use Cases

- **Track JDM reel and rod prices across 200+ Tackleberry stores** — monitor price drops and stock changes for reselling.
- **Monitor used tackle inventory for rare discontinued lures** — never miss a hard‑to‑find item when it goes on sale.
- **Build a fishing gear price‑comparison dashboard** — aggregate Japanese tackle prices for your own app or website.
- **Market research on Japan used tackle pricing trends** — analyze historical data to spot pricing patterns.

## Integrations

- **Apify MCP Connectors** – push results to Slack, Notion, Supabase, or GitHub automatically.
- **Scheduling** – use the Schedule tab to run this Actor every day with no manual work.
- **Webhooks** – get a POST request to your endpoint whenever the Actor finishes.

## Pricing

- **$0.01 per 1,000 results** + **$0.00005 per run start**.
- A typical 100‑item run costs **under $0.01**.
- No minimum monthly fee — pay only for what you use.

## Limitations

- The Actor reads **listing pages** only. Some product details (e.g., precise stock status) may not be available for every item.
- The website is **Japanese‑only**, and all titles/names will be in Japanese.
- To respect rate limits, the Actor waits **1–3 seconds** between page requests.

## FAQ

**Can I search used items only?**

Yes — use category search with `sale_type[]=3`. Provide a `categoryId` and the Actor will only return used products.

**How fresh is the data?**

Real‑time. The Actor fetches data at execution time directly from the website.

**Can I schedule runs?**

Yes — open the Schedule tab in Apify and set a daily (or any custom) interval.

**Is the site TOS‑compliant?**

The site's `robots.txt` allows general crawlers, and this Actor respects those rules.

## Changelog

### 0.1.0 (2026-08-08)
- Initial release.
- Keyword search.
- Category search with used‑item support (`sale_type[]=3`).
- Pagination (60 items per page).
- Stock detection.

## Integrations

Works with Apify [Connectors](https://apify.com/integrations) — push results to Slack, Google Sheets, Notion, or Supabase with one click. Trigger on a [Schedule](https://apify.com/docs/schedules) for daily price tracking.
