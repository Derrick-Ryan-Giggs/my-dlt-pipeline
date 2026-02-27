"""dlt pipeline to ingest data from the Open Library Books REST API."""

import json

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def open_library_rest_api_source():
    """Define dlt resources for the Open Library Search API."""
    config: RESTAPIConfig = {
        "client": {
            # Open Library public API base URL
            "base_url": "https://openlibrary.org/",
        },
        "resources": [
            {
                "name": "books",
                "endpoint": {
                    # Search API: https://openlibrary.org/search.json
                    "path": "search.json",
                    "method": "GET",
                    "params": {
                        # Search for books about "python programming".
                        "q": "python programming",
                        # Request up to 100 results in a single paginated response.
                        "limit": 100,
                    },
                    # The response JSON has a "docs" array with individual works.
                    "data_selector": "$.docs[*]",
                    # We request all needed results in a single page (limit=100).
                    "paginator": {
                        "type": "single_page",
                    },
                },
            },
        ],
        # No incremental loading configured for now.
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name="open_library_pipeline",
    destination="duckdb",
    # `refresh="drop_sources"` ensures the data and the state is cleaned
    # on each `pipeline.run()`; remove the argument once you have a
    # working pipeline.
    refresh="drop_sources",
    # show basic progress of resources extracted, normalized files and load-jobs on stdout
    progress="log",
)


if __name__ == "__main__":
    load_info = pipeline.run(open_library_rest_api_source())
    print("Load info:", load_info)  # noqa: T201

    # 1. What tables were created in the pipeline?
    schema = pipeline.default_schema
    tables = list(schema.tables.keys())
    print("\nTables created in the pipeline:")  # noqa: T201
    for table_name in tables:
        print(f"- {table_name}")  # noqa: T201

    # 2. Show me the schema for the books table.
    books_table = schema.tables.get("books")
    if books_table:
        # `columns` contains the column definitions for the table.
        print("\nSchema for the `books` table (columns definition):")  # noqa: T201
        print(json.dumps(books_table.get("columns", {}), indent=2))  # noqa: T201
    else:
        print("\nNo `books` table found in the schema.")  # noqa: T201

    # 3. How many rows were loaded?
    try:
        with pipeline.destination_client() as client:
            # Query the destination (DuckDB) for the row count in the books table.
            result = client.sql_client.execute_sql("SELECT COUNT(*) AS c FROM books")
            # `result` is typically a list/sequence of rows; take the first value.
            row_count = result[0][0] if result else 0
        print(f"\nNumber of rows loaded into `books`: {row_count}")  # noqa: T201
    except Exception as exc:  # pragma: no cover - defensive logging only
        print(f"\nCould not determine row count for `books`: {exc}")  # noqa: T201
