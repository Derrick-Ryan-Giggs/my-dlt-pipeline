## Open Library dlt Pipeline

This project is a minimal example of using [dlt](https://dlthub.com) to load data from the [Open Library API](https://openlibrary.org/developers/api) into DuckDB, and then exploring it with a [marimo](https://github.com/marimo-team/marimo) notebook and [ibis](https://ibis-project.org).

The pipeline currently:

- Calls the **Open Library Search API** (`/search.json`) to search for books about **“python programming”**
- Loads up to **100** search results into a DuckDB database via dlt
- Exposes a marimo notebook that uses ibis to compute and visualize the **top 10 authors by book count**

---

## Project structure

- `open_library_pipeline.py`  
  dlt pipeline that ingests data from the Open Library Search API into DuckDB.

- `open_library_authors_marimo.py`  
  marimo notebook (Python file) that uses ibis to query the loaded data and plot the top 10 authors.

- `open_library-docs.yaml`  
  Notes / references used to configure the Open Library endpoint.

- `requirements.txt`  
  Python dependencies for running the pipeline and notebook.

- `.gitignore`  
  Git ignore rules (e.g., to avoid committing local databases and IDE artifacts).

> Note: Local config (`.dlt/`) and Cursor IDE files (`.cursor/`) are intentionally not tracked in git.

---

## Prerequisites

- **Python** 3.9+ recommended (project was developed on Python 3.12)
- [pip](https://pip.pypa.io/)
- (Optional) [git](https://git-scm.com/) and [GitHub CLI](https://cli.github.com/) for version control / deployment

Create and activate a virtual environment if you like:

```bash
cd ~/Desktop/my-dlt-pipeline

python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If you’re only interested in the notebook, minimally you’ll need:

```bash
pip install dlt[duckdb] marimo "ibis-framework[duckdb]" matplotlib
```

---

## Open Library pipeline

### What the pipeline does

`open_library_pipeline.py` defines a dlt REST API source and pipeline:

- **Source name**: `open_library_rest_api_source`
- **Endpoint**: `https://openlibrary.org/search.json`
- **Query**: `q="python programming"`
- **Pagination / size**: `limit=100` in a single page (no incremental state yet)
- **Destination**: DuckDB (local file `open_library_pipeline.duckdb`)
- **Pipeline name**: `open_library_pipeline`

The response’s `docs` array is normalized into:

- A main `books` table
- Child tables such as `books__author_name`, `books__ia`, etc.

### Running the pipeline

From the project root:

```bash
python open_library_pipeline.py
```

This will:

1. Call the Open Library Search API
2. Load the results into DuckDB
3. Print:
   - **Tables created** in the dataset
   - **Schema for the `books` table**
   - **Row count** for `books` (via a DuckDB SQL query)

Re-run this command any time you want to refresh the dataset.

---

## Exploring the data with marimo + ibis

### What the notebook does

`open_library_authors_marimo.py` is a marimo notebook that:

1. Connects to the **DuckDB database file** created by the pipeline (`open_library_pipeline.duckdb`).
2. Uses **ibis** to:
   - Read the `books` table
   - Read the normalized `books__author_name` table
   - Join them on `_dlt_id` / `_dlt_parent_id`
   - Compute the **top 10 authors by number of books** in the search results.
3. Displays:
   - A pandas DataFrame of the top 10 authors
   - A **matplotlib** horizontal bar chart of author vs. book count

### Launching marimo (interactive mode)

First, make sure the pipeline has been run at least once so `open_library_pipeline.duckdb` exists.

Then:

```bash
marimo edit open_library_authors_marimo.py
```

You should see output like:

```text
Edit open_library_authors_marimo.py in your browser 📝
  ➜  URL: http://localhost:2718?access_token=...
```

Open the URL in a browser and:

1. Run the cells in order (or “Run all”).
2. You’ll see:
   - The computed top-10-authors DataFrame.
   - A matplotlib bar chart with the author distribution.

### Run mode (read‑only app)

To run in app / report mode:

```bash
marimo run open_library_authors_marimo.py
```

This starts a web server and opens the notebook in **read-only** mode, which is good for sharing a simple dashboard.

---

## DuckDB / locking considerations

- The pipeline and the notebook both use **the same DuckDB file**: `open_library_pipeline.duckdb`.
- DuckDB only allows certain concurrency patterns; if you see an error like:

  ```text
  IO Error: Could not set lock on file "open_library_pipeline.duckdb":
  Conflicting lock is held ...
  ```

  then:

  - Stop any previously running `python open_library_pipeline.py` processes.
  - Stop any old `marimo run ...` sessions that might still be open.
  - Then rerun the pipeline or notebook.

In this project, the notebook connects to DuckDB in **read-only** mode to minimize locking issues.

---

## Deploying to GitHub

Assuming you’re in the project directory and have already staged what you want:

```bash
cd ~/Desktop/my-dlt-pipeline

# If you haven’t yet:
git init

# Stage only the core project files
git add open_library_pipeline.py open_library_authors_marimo.py open_library-docs.yaml requirements.txt .gitignore

git commit -m "Your Commit Message"
```

Create a new empty repository on GitHub (via the web UI), then:

```bash
git remote add origin https://github.com/<YOUR_USER_OR_ORG>/<REPO_NAME>.git
git branch -M main
git push -u origin main
```

From there, you can:

- Share the repo URL with others.
- Run the pipeline and notebook on any machine by cloning the repo and installing `requirements.txt`.

---

## Future improvements

Ideas for extending this project:

- **More endpoints**: add additional Open Library resources (e.g., works, subjects, authors).
- **Incremental loading**: configure dlt’s incremental state to only pull new/updated records.
- **Parameterization**: make the search query (`q`) configurable (via environment variables or CLI args).
- **Richer analytics**: build more marimo notebooks (or dashboards) for:
  - Trends by publication year
  - Breakdown by language or subject
  - Deep dives into specific authors or series

Pull requests and ideas are welcome
```
