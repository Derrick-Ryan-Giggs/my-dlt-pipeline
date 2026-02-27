import marimo

__generated_with = "0.20.2"
app = marimo.App()

@app.cell
def _():
    import ibis

    return (ibis,)


@app.cell
def _(ibis):
    from pathlib import Path

    # Open a read-only DuckDB connection via ibis.
    duckdb_path = Path(__file__).with_name("open_library_pipeline.duckdb")
    ibis_con = ibis.duckdb.connect(str(duckdb_path), read_only=True)

    # Default dlt dataset schema name in DuckDB for this pipeline.
    dataset_schema = "open_library_pipeline_dataset"

    return dataset_schema, duckdb_path, ibis_con


@app.cell
def _(dataset_schema, ibis, ibis_con):
    # Access the `books` table and the normalized author table via ibis.
    # dlt normalizes list fields like `author_name` into a child table.
    active_schema = dataset_schema
    try:
        available = set(ibis_con.list_tables(database=active_schema))
    except Exception:
        available = set(ibis_con.list_tables())
        active_schema = None

    if active_schema and "books" in available:
        books = ibis_con.table("books", database=active_schema)
        authors = ibis_con.table("books__author_name", database=active_schema)
    else:
        books = ibis_con.table("books")
        authors = ibis_con.table("books__author_name")

    joined = books.join(authors, books._dlt_id == authors._dlt_parent_id)

    # Aggregate to find the top 10 authors by book count.
    top_authors = (
        joined.group_by(joined.value)
        .aggregate(book_count=joined._dlt_parent_id.nunique())
        .order_by(ibis.desc("book_count"))
        .limit(10)
    )

    # Execute to get a pandas DataFrame for visualization.
    top_authors_df = top_authors.execute()
    top_authors_df
    return (top_authors_df,)


@app.cell
def _(top_authors_df):
    import matplotlib.pyplot as plt

    df = top_authors_df.sort_values("book_count", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(df["value"], df["book_count"])
    ax.set_xlabel("Book count")
    ax.set_ylabel("Author")
    ax.set_title("Top 10 authors by book count (Open Library search: 'python programming')")
    fig.tight_layout()

    fig
    return (fig,)


@app.cell(hide_code=True)
def _():
    import marimo as _mo

    _mo.md(
        r"""
### Top 10 authors by book count

This notebook reads the `open_library_pipeline` DuckDB dataset and queries it with Ibis.

Run:

```bash
marimo edit open_library_authors_marimo.py
```

or:

```bash
marimo run open_library_authors_marimo.py
```
"""
    )
    return


if __name__ == "__main__":
    app.run()
