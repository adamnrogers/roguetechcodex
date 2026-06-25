# Portraits - Design Spec

**Date:** 2026-06-08  
**Status:** Approved

---

## Overview

Surface in-game mech/vehicle portraits on browse cards and chassis detail pages. Portraits are DDS files (vertically-flipped bitmaps) stored inside RT_ROOT. A one-shot conversion script produces local PNG artefacts. The DB gains an `icon` field that maps each chassis to its portrait filename.

Gear/weapon icons are out of scope.

---

## 1. Data Layer

### 1.1 Schema change

Add one nullable column to the `chassis` table:

```sql
ALTER TABLE chassis ADD COLUMN icon TEXT;
```

The pipeline drops and recreates all tables on every run (`DROP TABLE IF EXISTS` + `CREATE TABLE IF NOT EXISTS`), so adding the column to `schema.sql` is sufficient - no migration guard needed.

### 1.2 Pipeline ingestion

In `insert_chassis()` (called for every chassisdef), read `data["Description"]["Icon"]` (may be absent or empty string). Store raw value as-is - it is the stem used to locate the portrait file. Examples: `"adder"`, `"uixTxrIcon_atlas"`, `"AtlasOS"`.

The `icon` column on the `chassis` table is written once per `prefab_base`. Where multiple variants share a chassis, any non-null/non-empty icon value from the first variant processed wins (current `INSERT OR IGNORE` behaviour already handles this - add icon to the INSERT).

### 1.3 API

Add `icon: Optional[str]` to:
- `ChassisSummary` (browse card, `GET /api/v1/mechs` + `/api/v1/vehicles`)
- `ChassisDetail` (detail page, `GET /api/v1/mechs/{id}` + `/api/v1/vehicles/{id}`)

In `mechs.py`, add `c.icon` to the `SELECT` in `list_mechs`, `list_vehicles`, `get_mech`, and `get_vehicle`.

---

## 2. Portrait Conversion Script

**File:** `pipeline/portraits.py`  
**Purpose:** Convert DDS portraits from RT_ROOT → PNG files in `frontend/src/public/portraits/`  
**Trigger:** `make portraits` - independent of `make dev-pipeline`. Run once on initial setup, and again only if RT_ROOT portrait files change. Portraits change far less frequently than the data DB.

### 2.1 Inputs

- `RT_ROOT` env var (same as pipeline; read from `.env` if present)
- `DB_PATH` env var (default `roguetech.db` in project root) - used to fetch all distinct `icon` values

### 2.2 Discovery

Scan RT_ROOT recursively for:
1. Any `.dds` file whose parent directory name is `portrait` or `tankportrait`
2. Any `.png` file whose parent directory name is `portrait` or `tankportrait`

Build a case-insensitive lookup: `stem.lower() → absolute_path`.

### 2.3 Conversion

For each distinct `icon` value in the DB:
1. Look up `icon.lower()` in the discovery map.
2. If `.dds`: open with Pillow, flip vertically (`ImageOps.flip`), save as PNG.
3. If `.png`: copy directly (no flip needed - already correct orientation).
4. Output path: `{FRONTEND_PUBLIC}/portraits/{icon}.png` (lowercase filename, `.png` extension).
5. If no match: log a warning line `MISSING: {icon}` - skip silently, no error.

Skip files that already exist and are newer than the source (modification time check) so re-runs are fast.

### 2.4 DDS support

Pillow reads DDS via its built-in DDS decoder (added in Pillow 9.1). The pipeline `requirements.txt` already pins `Pillow`; confirm version ≥ 9.1. No extra library needed.

### 2.5 Output location

`frontend/src/public/portraits/` - served as static assets by Vite dev server and Nginx in production.

Add to `.gitignore`:

```
frontend/src/public/portraits/
```

### 2.6 Makefile target

```makefile
portraits:
    python pipeline/portraits.py
```

Runs outside Docker (uses local Python, same as the pipeline can be run locally). If Docker-only is preferred, this can be adapted later.

---

## 3. Frontend

### 3.1 Portrait URL helper

Add a small utility in `frontend/src/src/utils/portrait.ts`:

```typescript
export function portraitUrl(icon: string | null | undefined): string | null {
  if (!icon) return null
  return `/portraits/${icon}.png`
}
```

### 3.2 MechCard.vue

Add a portrait image in the card header area. Layout: portrait on the left (fixed ~80×80px), existing text content on the right.

- Source: `portraitUrl(item.icon)`
- If `icon` is null/empty, or the image 404s (`@error` handler sets `src` to `null`/hides the `<img>`): show no image - card layout adjusts gracefully (portrait area collapses).
- No placeholder image: absence of portrait is acceptable.

### 3.3 ChassisPage.vue

Add a portrait in the page header (alongside the chassis name and breadcrumb), sized ~120×120px.

- Source: `portraitUrl(data.icon)` - `data` is `ChassisDetail`.
- Same error/null handling as MechCard.

---

## 4. Scope Boundaries

| In scope | Out of scope |
|---|---|
| Mech + vehicle portraits | Gear / weapon icons |
| DDS + PNG source files | Wiki scraping |
| `make portraits` local artefact | Automated re-run on pipeline rebuild |
| Card + detail page display | Portrait on hover/tooltip in other views |

---

## 5. Files Changed

| File | Change |
|---|---|
| `pipeline/pipeline/schema.sql` | Add `icon TEXT` to chassis table |
| `pipeline/pipeline/ingest.py` | Read + store `Description.Icon` in `insert_chassis` |
| `pipeline/portraits.py` | New conversion script |
| `Makefile` | Add `portraits` target |
| `.gitignore` | Ignore `frontend/src/public/portraits/` |
| `api/models.py` | Add `icon: Optional[str]` to `ChassisSummary` + `ChassisDetail` |
| `api/routers/mechs.py` | Expose `icon` in all four chassis queries |
| `frontend/src/src/utils/portrait.ts` | New URL helper |
| `frontend/src/src/components/MechCard.vue` | Portrait image |
| `frontend/src/src/pages/ChassisPage.vue` | Portrait image in header |
