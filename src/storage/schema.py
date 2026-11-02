from sqlite3 import Connection

CREATE_TOPICS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS topics (
    topic_id INTEGER PRIMARY KEY,
    parent_id INTEGER,
    topic_code TEXT NOT NULL,
    topic_parent_code TEXT,
    title TEXT NOT NULL,
    topic_type TEXT,
    display_order INTEGER,
    topic_level INTEGER NOT NULL,
    topic_path TEXT NOT NULL,
    category TEXT,
    is_leaf INTEGER DEFAULT 0,
    content_text TEXT,
    explanation TEXT,
    content_type TEXT,
    FOREIGN KEY (parent_id) REFERENCES topics(topic_id)
);
"""

CREATE_TOPIC_EDGES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS topic_edges (
    parent_id INTEGER NOT NULL,
    child_id INTEGER NOT NULL,
    relation_type TEXT DEFAULT 'subsumes',
    PRIMARY KEY (parent_id, child_id),
    FOREIGN KEY (parent_id) REFERENCES topics(topic_id),
    FOREIGN KEY (child_id) REFERENCES topics(topic_id)
);
"""

CREATE_TOPIC_CLOSURE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS topic_closure (
    ancestor_id INTEGER NOT NULL,
    descendant_id INTEGER NOT NULL,
    depth INTEGER NOT NULL,
    PRIMARY KEY (ancestor_id, descendant_id, depth),
    FOREIGN KEY (ancestor_id) REFERENCES topics(topic_id),
    FOREIGN KEY (descendant_id) REFERENCES topics(topic_id)
);
"""

CREATE_TOPIC_PATHS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS topic_materialized_paths (
    topic_id INTEGER PRIMARY KEY,
    path_string TEXT NOT NULL,
    level INTEGER NOT NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id)
);
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_topics_parent ON topics(parent_id);",
    "CREATE INDEX IF NOT EXISTS idx_topics_level ON topics(topic_level);",
    "CREATE INDEX IF NOT EXISTS idx_topics_path ON topics(topic_path);",
    "CREATE INDEX IF NOT EXISTS idx_closure_ancestor ON topic_closure(ancestor_id);",
    "CREATE INDEX IF NOT EXISTS idx_closure_descendant ON topic_closure(descendant_id);",
    "CREATE INDEX IF NOT EXISTS idx_closure_depth ON topic_closure(depth);",
    "CREATE INDEX IF NOT EXISTS idx_edges_child ON topic_edges(child_id);"
]

def init_hierarchy_schema(conn: Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(CREATE_TOPICS_TABLE_SQL)
    cursor.execute(CREATE_TOPIC_EDGES_TABLE_SQL)
    cursor.execute(CREATE_TOPIC_CLOSURE_TABLE_SQL)
    cursor.execute(CREATE_TOPIC_PATHS_TABLE_SQL)
    for index_query in CREATE_INDEXES_SQL:
        cursor.execute(index_query)
