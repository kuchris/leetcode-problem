"""SQLite-backed harness for the database problems.

LeetCode judges these on PostgreSQL 16 (the `postgresql` langSlug), which is what
the submit driver sends. SQLite is the only engine available locally without an
install, so this harness is an approximation and says so rather than implying
equivalence.

Where they agree: joins, grouping, aggregate functions, subqueries, CTEs, window
functions, string concatenation with `||`, `COALESCE`, `LIMIT`, and
`NULLS FIRST`/`LAST`. Where they differ: date and interval arithmetic, regular
expressions, `DISTINCT ON`, `RETURNING`, type coercion, and the default NULL
ordering under `DESC` (PostgreSQL puts NULLs first, SQLite puts them last).

The schema comes from the problem's `metaData.database_schema` and the rows from
`exampleTestcases`, so a test builds its database from the same definitions the
judge uses instead of hand-writing CREATE TABLE statements that could drift.

Two traps this module exists to absorb, both found by a solver rather than by me:

  - the judge's rows follow the `headers` order, which need not match the schema's
    column order. For `combine-two-tables` they differ, and inserting positionally
    silently transposes first and last names. `build_from_example` reorders.
  - `exampleTestcases` is not always one JSON document. Some problems ship several
    newline-separated ones, and some carry an `argument` key the judge passes to a
    stored function. `parse_example_documents` handles both.
"""
import json
import os
import sqlite3

# LeetCode's type names are PostgreSQL's; SQLite accepts almost any type name and
# applies its own affinity rules, so the mapping is mostly for readability.
TYPE_MAP = {
    'INT': 'INTEGER',
    'INTEGER': 'INTEGER',
    'BIGINT': 'INTEGER',
    'SMALLINT': 'INTEGER',
    'VARCHAR(255)': 'TEXT',
    'VARCHAR': 'TEXT',
    'TEXT': 'TEXT',
    'CHAR': 'TEXT',
    'DATE': 'TEXT',
    'DATETIME': 'TEXT',
    'TIMESTAMP': 'TEXT',
    'DECIMAL': 'REAL',
    'FLOAT': 'REAL',
    'DOUBLE': 'REAL',
}

META_FILENAME = 'sql-shell-meta.json'


def load_sql(filename):
    """Return the SQL text of a solution file, with the header comment stripped.

    The files carry the repository's header block, which SQLite would reject if it
    reached the parser, so leading `--` lines are removed. Comments after the
    first statement are kept: a query may legitimately contain them.
    """
    from _loader import SOLUTIONS_DIR

    path = SOLUTIONS_DIR / filename
    lines = path.read_text(encoding='utf-8').splitlines()
    body = []
    seen_code = False
    for line in lines:
        stripped = line.strip()
        if not seen_code and (not stripped or stripped.startswith('--')):
            continue
        seen_code = True
        body.append(line)
    return '\n'.join(body).strip()


def sqlite_type(declared):
    """Map a PostgreSQL type name to something SQLite will accept."""
    key = (declared or '').strip().upper()
    if key in TYPE_MAP:
        return TYPE_MAP[key]
    for prefix, mapped in TYPE_MAP.items():
        if key.startswith(prefix):
            return mapped
    return 'TEXT'


def build(schema, rows):
    """Build an in-memory database from a schema dict and a rows dict.

    ``schema`` maps table -> {column: type}. ``rows`` maps table -> list of row
    lists **in that same schema column order** - this low-level function does not
    reorder, because a caller passing hand-built fixtures wants exactly what it
    wrote. Use ``build_from_example`` for the judge's own data, which follows the
    ``headers`` order instead and may differ.
    """
    connection = sqlite3.connect(':memory:')
    for table, columns in schema.items():
        definitions = ', '.join(
            f'"{name}" {sqlite_type(declared)}' for name, declared in columns.items()
        )
        connection.execute(f'CREATE TABLE "{table}" ({definitions})')
        values = rows.get(table) or []
        if values:
            placeholders = ', '.join('?' * len(columns))
            connection.executemany(
                f'INSERT INTO "{table}" VALUES ({placeholders})', values
            )
    connection.commit()
    return connection


def query(connection, sql):
    """Run a query and return its rows as a list of tuples."""
    return [tuple(row) for row in connection.execute(sql).fetchall()]


def as_multiset(rows):
    """Sort rows so two results compare as sets, which is how LeetCode compares
    them unless the statement fixes an order."""
    return sorted(rows, key=lambda row: tuple('' if v is None else str(v) for v in row))


def parse_example_documents(text):
    """Parse an exampleTestcases payload into a list of documents.

    The payload is usually one JSON object, but some problems ship several
    separated by newlines, and a document may carry an ``argument`` that the judge
    passes to a stored function. Returns a list of dicts, each with whatever of
    ``headers``, ``rows`` and ``argument`` the payload provided.
    """
    documents = []
    decoder = json.JSONDecoder()
    index = 0
    while index < len(text):
        while index < len(text) and text[index] in ' \t\r\n':
            index += 1
        if index >= len(text):
            break
        document, index = decoder.raw_decode(text, index)
        documents.append(document)
    return documents


def parse_example_testcases(text):
    """The first example document's rows and headers, as a convenience pair."""
    documents = parse_example_documents(text)
    if not documents:
        return {}, {}
    return documents[0].get('rows') or {}, documents[0].get('headers') or {}


def reorder_rows(rows, headers, columns):
    """Put each row into ``columns`` order, reading it in ``headers`` order.

    This is the fix for the transposition: the judge's rows are positional in
    ``headers`` order, while ``build`` wants the schema's column order, and the
    two differ whenever a problem lists its columns differently from its DDL.
    """
    if not headers:
        return rows
    if list(headers) == list(columns):
        return rows
    positions = {name: index for index, name in enumerate(headers)}
    missing = [name for name in columns if name not in positions]
    if missing:
        raise ValueError(
            f'headers {headers} do not cover schema columns {columns}; '
            f'missing {missing}')
    return [[row[positions[name]] for name in columns] for row in rows]


def build_from_example(schema, example_testcases):
    """Build a database from a problem's schema and its example testcases.

    Rows are reordered from ``headers`` order into schema order, so the values land
    in the right columns.
    """
    table_rows, headers = parse_example_testcases(example_testcases)
    ordered = {
        table: reorder_rows(rows, headers.get(table), list(schema[table]))
        for table, rows in table_rows.items()
        if table in schema
    }
    return build(schema, ordered)


def load_problem_meta(slug, state_dir=None):
    """Return one problem's SQL metadata from the pipeline's cache.

    The cache is written by the tooling that fetches the problems; it holds the
    schema, the CREATE statements and the judge's example testcases.
    """
    directory = state_dir or os.environ.get('LC_STATE') or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'tools', 'agent', 'state')
    with open(os.path.join(directory, META_FILENAME), encoding='utf-8') as handle:
        meta = json.load(handle)
    if slug not in meta:
        raise KeyError(f'{slug} is not in {META_FILENAME}')
    return meta[slug]


def build_from_problem(slug, state_dir=None):
    """Build the judge's example database for a problem, and return it with its
    arguments.

    Returns ``(connection, arguments)`` where ``arguments`` is the list of
    ``argument`` values the example documents carried, which is what a stored
    function problem needs.
    """
    meta = load_problem_meta(slug, state_dir)
    connection = build_from_example(meta['databaseSchema'], meta['exampleTestcases'])
    arguments = [
        document['argument']
        for document in parse_example_documents(meta['exampleTestcases'])
        if 'argument' in document
    ]
    return connection, arguments
