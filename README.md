# SB9Analysis

`SB9Analysis` is a point-in-time analysis repository for Texas teacher-pay proposals
associated with SB 9 (88-R), related retention-allotment scenarios, and district-level
teacher-experience mapping.

The repository combines notebooks, scripts, spreadsheets, and static outputs to make
legislative compensation proposals easier to inspect outside the Capitol narrative.

## What the Repository Covers

The analysis focuses on questions such as:

- how proposed raises or allotments distribute across districts
- what those proposals imply for total cost and district-level effects
- how district experience profiles vary across Texas
- how downloadable HB 3 raise-report artifacts can be collected and reviewed

## Key Inputs

Important source files in the repository include:

- `Directory.xlsx`
  District directory and enrollment context
- `Staff Salary FTE Report_Statewide_Districts_2022-2023.csv`
  Statewide district staffing / FTE data
- `DSTAF.csv`
  TAPR district staff dataset used for experience analysis
- `2021-2022 TAPR DStaff Legend.xlsx`
  Column dictionary for the TAPR staffing export

## Key Analysis Artifacts

- `SB 9 retention allotment analysis_05.09.23.xlsx`
- `SB 9 retention allotment analysis_05.11.23.xlsx`
- `SB 9 Analysis_raise proposals.xlsx`
- `SB 9 Analysis_raise proposals_v1.xlsx`
- `TX School Districts_% Total Teachers, 6+ Yrs Experience.html`

These outputs capture different slices of the legislative and staffing analysis and
should be read as project artifacts rather than a formal software package.

## Scripts

### `main.py`

Builds a district-level retention-allotment analysis by:

- loading district directory data
- matching total teaching staff from statewide staffing exports
- calculating retention-allotment cost scenarios
- exporting the resulting workbook

### `gen_teacher_experience_map.py`

Builds a district-level teacher-experience map by:

- joining district boundary geometry to district staffing data
- calculating the share of teachers with six or more years of experience
- exporting a GeoJSON artifact and static HTML map

The district-geometry input is configurable through:

```bash
SB9_DISTRICTS_GEOJSON=/path/to/Current_Districts_2023.geojson
```

### `download_hb3_raise_reports.py`

Downloads HB 3 raise-report files referenced in `xlsx_links.txt` for bulk review.

## Quick Start

### 1. Create an environment

```bash
python3 -m venv .venv
.venv/bin/pip install pandas openpyxl geopandas folium branca
```

### 2. Run the retention-allotment analysis

```bash
.venv/bin/python main.py
```

### 3. Generate the teacher-experience map

```bash
SB9_DISTRICTS_GEOJSON=/path/to/Current_Districts_2023.geojson \
.venv/bin/python gen_teacher_experience_map.py
```

### 4. Download additional raise reports

```bash
.venv/bin/python download_hb3_raise_reports.py
```

## Repository Character

This repo is intentionally analysis-heavy rather than package-like. It preserves
source spreadsheets, notebooks, scripts, and published artifacts together so that
the logic, assumptions, and outputs stay inspectable in one place.

## Notes

- The analysis is tied to a specific legislative period and historical data snapshot.
- Some outputs are static artifacts retained for reference rather than regenerated on every run.
- Geographic map generation depends on an external district boundary GeoJSON file, which is why the path is configurable instead of hardcoded.
