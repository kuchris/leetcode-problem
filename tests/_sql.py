"""SQLite-backed harness for the database problems.

LeetCode judges these on PostgreSQL 16 (the `postgresql` langSlug), which is what
the submit driver sends. SQLite is the only engine available locally without an
install, so this harness is an approximation and says so rather than implying
equivalence.

Where they agree: joins, grouping, aggregate functions, subqueries, CTEs,
window functions, string concatenation with `||`, `COALESCE`, `LIMIT`, and
`NULLS FIRST`/`LAST`. Where they differ: date and interval arithmetic, regular
expressions, `DISTINCT ON`, `RETURNING`, and type coercion rules. A solution that
needs one of those cannot be validated here and must be verified by submission.

The schema comes from the problem's `metaData.database_schema`, and the rows from
`exampleTestcases`, so a test builds its database from the same definitions the
judge uses instead of hand-writing CREATE TABLE statements that could drift.
"""
import json
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


def load_sql(filename):
    """Return the SQL text of a solution file, with comments stripped.

    The files carry the repository's header comment block, which SQLite would
    reject if it reached the parser, so leading `--` lines are removed. Comments
    after the first statement are kept: a query may legitimately contain them.
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

    ``schema`` maps table -> {column: type}, ``rows`` maps table -> list of row
    lists in the same column order, which is how LeetCode's exampleTestcases
    encodes them.
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


def parse_example_testcases(text):
    """Turn an exampleTestcases string into (schema_rows, table_rows).

    The payload looks like
    ``{"headers": {"T": [...]}, "rows": {"T": [[...], ...]}}``.
    """
    payload = json.loads(text)
    return payload.get('rows') or {}, payload.get('headers') or {}


def build_from_example(schema, example_testcases):
    """Build a database from the problem's schema and its example testcases."""
    table_rows, _ = parse_example_testcases(example_testcases)
    return build(schema, table_rows)


def schema_from_metadata(meta_data):
    """Extract database_schema from a problem's metaData payload.

    ``meta_data`` may be the raw JSON string LeetCode returns or an already
    parsed dict.
    """
    payload = json.loads(meta_data) if isinstance(meta_data, str) else meta_data
    return payload.get('database_schema') or {}
