# Database schema: CarListings

This document describes the **CarListings** table used by ReCarmend for car search and data maintenance. The table lives in Supabase (PostgreSQL). The API reads from it via `SupabaseService`; uploads come from CSV via `upload_all_listings` / `_prepare_data`.

---

## Table: `CarListings`

| Column        | Type         | Nullable | Description |
|---------------|--------------|----------|-------------|
| `id`          | integer      | NO       | Primary key, auto-increment. Reset to 1 when table is cleared and repopulated. |
| `year`        | integer      | YES      | Model year. |
| `make`        | text         | YES      | Manufacturer (e.g. Toyota, Honda). Filtered case-insensitively. |
| `model`       | text         | YES      | Model name. Filtered with partial match (ilike). |
| `price`       | integer      | YES      | Price in dollars. Stored as integer; "CALL" in CSV is converted to 0. |
| `mileage`     | integer      | YES      | Odometer mileage. "CALL" in CSV is converted to 0. |
| `color`       | text         | YES      | Color name. Filtered with partial match (ilike). |
| `url`         | text         | YES      | Listing URL. May be stored as `url` or `listing_url` depending on source. |
| `body_type`   | text         | YES      | Body type (e.g. SUV, Sedan, Hatchback). Some sources use column name `carType`; code accepts both. |
| `created_at`  | timestamptz  | YES      | Row creation time (Supabase default). Dropped from CSV on upload. |
| `updated_at`  | timestamptz  | YES      | Row update time (Supabase default). Dropped from CSV on upload. |

Optional columns (if present in CSV or migrations):

| Column          | Type   | Nullable | Description |
|-----------------|--------|----------|-------------|
| `listing_url`   | text   | YES      | Alternative to `url` for listing link. |
| `carType`       | text   | YES      | Alternative to `body_type`. |
| `battery_range` | int/float | YES  | Used for electric/hybrid (ElectricCar). Column may be `batteryRange`. |

---

## Query behavior (SupabaseService)

- **Search filters:** `price` (≤ max), `mileage` (≤ max), `year` (min ≤ year ≤ max), `color`, `make`, `model`, `body_type` or `carType`.
- **Pagination:** Cursor-based via `id` (e.g. `WHERE id > :last_id`), limit 10.
- **Text filters:** Case-insensitive; `make` exact match, `model` and `color` partial match.

---

## CSV upload (data maintenance)

- **Source:** `data/all_listings.csv` (from Webscraping/Controller pipeline).
- **Preprocessing:** "CALL" → 0 for `price` and `mileage`; nulls allowed; columns `id`, `created_at`, `updated_at` stripped before insert so Supabase can generate them.
- **Expected CSV columns (minimal):** `year`, `make`, `model`, `price`, `mileage`, `color`, `url`, `body_type`. Column names in CSV should match the table (e.g. `body_type` preferred; if the table uses `carType`, CSV should match that).

---

## API response shape (from this table)

The REST API does not return DB rows directly. Rows are mapped to the **CarResponse** shape (see `Controller/services/schemas.py`): `id`, `make`, `model`, `year`, `price`, `mileage`, `fuelType` (derived), `bodyType`, `color`, `url`, `colorHex`, `imageUrl`, `image`. `fuelType` and images are added in the backend; the rest come from CarListings (or equivalents like `body_type` → `bodyType`).
