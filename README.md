# Tackleberry B-net Scraper (Apify Actor)

Scrape product data from **@Berry Net** (タックルベリーB-net) – https://b-net.tackleberry.co.jp

このアクターは、タックルベリーB-netの商品一覧をスクレイピングするためのApifyアクターです。

## Features

- **Search by keyword**: `https://b-net.tackleberry.co.jp/products/list?name={keyword}`
- **Search by category**: `https://b-net.tackleberry.co.jp/products/list?sale_type[]=3&category_id={categoryId}`
- **Pagination**: `pageno=N` parameter, 60 items per page
- **Retry logic**: 3 retries with exponential backoff
- **Random delay**: 1–3 seconds between page requests
- **Pure SSR**: No browser needed, works with `httpx` only

## Input

| Field         | Type    | Description                               |
|---------------|---------|-------------------------------------------|
| `keyword`     | string  | Search keyword (e.g. シマノ)              |
| `categoryId`  | integer | Category ID from the category URL         |
| `maxItems`    | integer | Maximum number of items to return (default: 100) |
| `proxyConfiguration` | object  | Apify proxy configuration                 |

*Keyword and categoryId are optional, but at least one must be provided.*

## Output

Each result is a JSON object with the following fields:

- `productId` – ID from URL `/products/detail/{id}`
- `title` – product title
- `name` – alt text of the product image
- `price` – tax‑included price (integer)
- `regularPrice` – original price (if available)
- `discountRate` – discount percentage (if available)
- `imageUrl` – absolute image URL
- `productUrl` – absolute product page URL
- `isUsed` – `true` for used items, `false` otherwise
- `categoryId` – category ID used in the query (or `null`)
- `inStock` – `true` if the item appears in stock, `false` otherwise

Example:

```json
{
  "productId": "12345",
  "title": "シマノ アンタレス DC MD",
  "name": "シマノ アンタレス DC MD",
  "price": 29800,
  "regularPrice": 45000,
  "discountRate": 34,
  "imageUrl": "https://b-net.tackleberry.co.jp/upload/save_image/12345.jpg",
  "productUrl": "https://b-net.tackleberry.co.jp/products/detail/12345",
  "isUsed": true,
  "categoryId": 12,
  "inStock": true
}
```

## Usage

Build the actor, then run it with an input like:

```json
{
  "keyword": "シマノ",
  "maxItems": 50
}
```

or

```json
{
  "categoryId": 12,
  "maxItems": 100
}
```

## Technical Notes

- Uses `httpx` with `urllib`-based URL encoding.
- Robust handling of Japanese characters (`urlencode`).
- No external browser dependencies (Playwright / Puppeteer **not** required).
- Respects `robots.txt` for general crawlers.
- Implements a simple retry mechanism with exponential backoff.
- Includes a random delay between page fetches to reduce server load.

---

# タックルベリーB-net スクレイパー (Apify Actor)

タックルベリーB-netの商品一覧をスクレイピングするApifyアクターです。

## 機能

- **キーワード検索**: `name` パラメータで商品を検索
- **カテゴリ検索**: カテゴリIDと中古(`sale_type[]=3`)を指定
- **ページネーション**: `pageno` パラメータで60件ずつ取得
- **リトライ**: 最大3回のリトライ（指数バックオフ）
- **遅延**: ページ間で1〜3秒のランダム待機
- **SSR対応**: ブラウザ不要、`httpx` のみで動作

## 入力

| 項目          | 型       | 説明                                          |
|---------------|----------|-----------------------------------------------|
| `keyword`     | string   | 検索キーワード（例: シマノ）                   |
| `categoryId`  | integer  | カテゴリURLのカテゴリID                        |
| `maxItems`    | integer  | 最大取得件数（デフォルト: 100）                |
| `proxyConfiguration` | object   | Apify プロキシ設定                             |

*`keyword` と `categoryId` は省略可能ですが、どちらか一方は必須です。*

## 出力

各結果は以下のフィールドを含むJSONオブジェクトです。

- `productId` – URL末尾の商品ID
- `title` – 商品名
- `name` – 商品画像のalt属性
- `price` – 税込価格（整数）
- `regularPrice` – 定価（あれば）
- `discountRate` – 割引率（%）
- `imageUrl` – 商品画像の絶対URL
- `productUrl` – 商品ページの絶対URL
- `isUsed` – 中古商品なら `true`、新品なら `false`
- `categoryId` – クエリで使用したカテゴリID
- `inStock` – 在庫ありなら `true`、在庫切れなら `false`

例:

```json
{
  "productId": "12345",
  "title": "シマノ アンタレス DC MD",
  "name": "シマノ アンタレス DC MD",
  "price": 29800,
  "regularPrice": 45000,
  "discountRate": 34,
  "imageUrl": "https://b-net.tackleberry.co.jp/upload/save_image/12345.jpg",
  "productUrl": "https://b-net.tackleberry.co.jp/products/detail/12345",
  "isUsed": true,
  "categoryId": 12,
  "inStock": true
}
```

## 使用方法

ビルド後、次のような入力で実行します。

```json
{
  "keyword": "シマノ",
  "maxItems": 50
}
```

または

```json
{
  "categoryId": 12,
  "maxItems": 100
}
```

## 技術的な注意点

- `httpx` を使用し、日本語URLは `urlencode` で正しくエンコードします。
- WebブラウザやPlaywrightは不要です。
- 一般的なクローラー向け `robots.txt` を尊重します。
- 指数バックオフ付きのリトライとページ間のランダム遅延により、サーバー負荷を軽減します。
