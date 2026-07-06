# Hi-Tec Shopify Automation

Freelance automation work for Hi-Tec Bearings, a bearings retailer running a Shopify store with thousands of product variants. Their stock system and their Shopify catalogue lived in separate spreadsheets, and keeping quantities, costs, and product specs in sync by hand took hours per update cycle. These tools do that reconciliation automatically, working directly on the CSV/XLSX files exported from the Shopify admin. Solo work by Salman Adnan (2023).

Nothing here touches the Shopify API. The workflow the client used was: export products from Shopify admin, run a tool, review the output spreadsheet, re-import. That kept a human review step in front of every catalogue change.

## The tools

### 1. `quantity_pricing_updater/`

`update_quantity_pricing.py` merges the client's internal stock list into a Shopify product export. It matches each Shopify product (by `Title` for single-variant products, by `Option1 Value` for variants) against HI-TEC brand rows in the stock list, and adds `Updated Quantity` and `Updated Cost` columns with the current warehouse figures. Output is written next to the input as `updated_<name>.csv`.

Run headless with file paths, or with no arguments to get a file picker:

```
python quantity_pricing_updater/update_quantity_pricing.py sample_data/sample_stock_list.csv sample_data/sample_shopify_stock.csv
```

### 2. `dimensions_extractor/`

`dimensions_extractor.py` pulls structured bearing dimensions (bore diameter, outside diameter, width) out of the HTML product descriptions in a Shopify export. The descriptions contain dimension tables as raw HTML; the script strips tags, scans the remaining lines for the dimension labels, and writes the numbers into three new columns so they can be used as filterable metafields. Output: `updated_<name>.csv`.

```
python dimensions_extractor/dimensions_extractor.py sample_data/sample_shopify_stock.csv
```

### 3. `stock_updater_gui/`

`shopify_stock_updater.py` is the version handed to the client: a tkinter desktop app that bundles both tools above plus a third, variant detection, behind three buttons. Variant detection parses bearing designation suffixes in variant names (K, E, F, MB, CA, CC, 2RS, Z, ...) into human-readable `Bore`, `Cage`, and `Seal Type` columns. The GUI version also accepts XLSX input, writes XLSX output, and avoids overwriting existing output files. The `.spec` files in the other two folders are PyInstaller configs used to ship the tools as Windows executables.

```
python stock_updater_gui/shopify_stock_updater.py
```

## Setup

Python 3.10+ with tkinter (included in most Python installs; on Debian/Ubuntu install `python3-tk`).

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No credentials or environment variables are needed (see `.env.example`). The only access requirement in real use is a Shopify admin login to export and re-import product CSVs, which is not part of this repo.

## Sample data

The original repo contained the client's real stock list and product export: about 1,600 stock rows with actual cost prices, sale prices, quantities, and supplier names, plus an 11,000-line Shopify export including per-item costs. That is client-internal data, so it has been removed and replaced with a small fabricated sample in `sample_data/` that has the same column layout and HTML description structure. All prices and quantities in the sample are made up.

Both command-line tools were verified against this sample: quantity/cost merging picks the HI-TEC brand rows correctly (including non-default variants), and the dimensions extractor recovers all three dimensions from the sample HTML. The GUI was smoke-tested to the point of building its window. End-to-end runs against a live Shopify store (export, process, re-import) were done during the original engagement in 2023 and were not re-verified here.

## Challenges

- There is no Shopify API in this workflow, so everything had to round-trip through CSV/XLSX exports. That constraint shaped the whole design: the tools read a Shopify admin export, add columns, and write a new file for re-import, with a human reviewing the spreadsheet in between. It also meant I couldn't rely on stable product IDs to join records, only on the text fields the export happens to include.
- The stock list and the Shopify export don't share a key. A stock item like `6205` can appear more than once under different brands, and only the `HI-TEC` row is the one to trust. I filter the stock list to `Brand == 'HI-TEC'` before matching, then join on `Title` for single-variant products and on `Option1 Value` for variants. Without the brand filter the wrong quantity and cost get pulled in. You can see this in the sample: `6205` and `6304 2RS` both have a competing `OTHER` row, and the output correctly takes the HI-TEC figures.
- Bearing dimensions were locked inside HTML product descriptions, not in real columns. Each description carries a small dimensions table as raw HTML. I strip the tags, split the text into lines, and look for the label lines (bore diameter, outside diameter, width) with the numeric value on the following line. "Width" needed a fallback because some rows label it "total width". This recovers all three numbers into filterable columns, but it depends on the label-then-value ordering, which is the store's template and not guaranteed elsewhere.
- The original repo shipped with the client's real data: roughly 1,600 stock rows with actual costs, sale prices, and supplier names, plus an 11,000-line Shopify export with per-item costs. None of that could stay in a portfolio repo. I removed it and rebuilt a small fabricated sample with the same column layout and the same HTML description structure so the tools still run and can be verified, without exposing anything client-internal.
- Handing this to a non-technical client meant no command line. The GUI version wraps the three operations behind tkinter buttons and adds XLSX in/out plus a "don't overwrite" save that bumps a counter on the filename. The two CLI scripts were packaged as standalone Windows executables with PyInstaller (the `.spec` files), so the client could double-click rather than install Python.

## What I learned

- Matching records without a shared key is mostly about picking the right disambiguator first. Filtering to the HI-TEC brand before joining removed a whole class of wrong matches that no amount of fuzzy title matching would have fixed.
- Parsing data out of HTML by flattening to text and reading line pairs is quick to write and easy to reason about, but it's brittle. It rides on the exact template. A parser keyed on the table structure would survive layout changes that this approach silently misses.
- pandas punishes writing into filtered slices. Splitting the frame into default-title and non-default-title views and assigning back into them raises `SettingWithCopyWarning` and is why `requirements.txt` pins `pandas<3`: copy-on-write in pandas 3.0 would turn those silent warnings into lost writes. Building the result with a proper merge would have been both correct and faster.
- Shipping to a client is a real requirement, not an afterthought. Bundling to an executable and adding non-destructive saves and file pickers took as much thought as the matching logic, because that's the part the client actually touches.

## What I'd do differently

- The GUI script duplicates the two standalone scripts almost line for line. The processing logic should live in one shared module, with the CLI and tkinter frontends both importing it.
- Matching is O(n*m): for every Shopify row the stock list is re-filtered and converted to a list. A single `merge` on `Item`/`Brand` would replace both loops and run in a fraction of the time on the real 11k-row export.
- The pandas code leans on chained assignment (`df[value][x[0]] = ...`) and writes to filtered views, which produces `SettingWithCopyWarning` and will break outright under pandas 3.0's copy-on-write. That's why `requirements.txt` pins `pandas<3`.
- Debug `print` statements were left in from development; they should be removed or replaced with logging.
- The dimension extractor assumes a label line is immediately followed by its value line. It worked on this store's description template but would silently miss dimensions on any other layout. A proper HTML parser keyed on the table structure would be less brittle.
- No tests. Even a handful of fixture-based tests around the matching and extraction logic would have caught regressions between the CLI and GUI versions.
