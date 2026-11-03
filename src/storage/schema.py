from sqlite3 import Connection

CREATE_TOPICS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS topics (
    topic_id INTEGER PRIMARY KEY,
    parent_id INTEGER,
    topic_code TEXT,
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

CREATE_KNOWLEDGE_ATOMS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS knowledge_atoms (
    atom_id INTEGER PRIMARY KEY,
    topic_id INTEGER NOT NULL,
    parent_element_id INTEGER,
    element_type_en TEXT NOT NULL,
    element_type_ar TEXT NOT NULL,
    macro_category TEXT NOT NULL,
    element_title TEXT NOT NULL,
    element_text TEXT NOT NULL,
    element_order INTEGER NOT NULL,
    depth_level INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    confidence_level TEXT NOT NULL,
    start_char INTEGER NOT NULL,
    end_char INTEGER NOT NULL,
    page_number INTEGER,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id)
);
"""

CREATE_ATOM_PROVENANCE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS atom_provenance (
    atom_id INTEGER PRIMARY KEY,
    document_id TEXT NOT NULL,
    source_start_char INTEGER NOT NULL,
    source_end_char INTEGER NOT NULL,
    is_verified INTEGER DEFAULT 1,
    FOREIGN KEY (atom_id) REFERENCES knowledge_atoms(atom_id)
);
"""

CREATE_STAGE1_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_topics_parent ON topics(parent_id);",
    "CREATE INDEX IF NOT EXISTS idx_topics_level ON topics(topic_level);",
    "CREATE INDEX IF NOT EXISTS idx_topics_path ON topics(topic_path);",
    "CREATE INDEX IF NOT EXISTS idx_closure_ancestor ON topic_closure(ancestor_id);",
    "CREATE INDEX IF NOT EXISTS idx_closure_descendant ON topic_closure(descendant_id);",
    "CREATE INDEX IF NOT EXISTS idx_closure_depth ON topic_closure(depth);",
    "CREATE INDEX IF NOT EXISTS idx_edges_child ON topic_edges(child_id);"
]

CREATE_STAGE2_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_atoms_topic ON knowledge_atoms(topic_id);",
    "CREATE INDEX IF NOT EXISTS idx_atoms_role ON knowledge_atoms(element_type_en);",
    "CREATE INDEX IF NOT EXISTS idx_atoms_macro ON knowledge_atoms(macro_category);",
    "CREATE INDEX IF NOT EXISTS idx_atoms_order ON knowledge_atoms(element_order);"
]

def init_hierarchy_schema(conn: Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(CREATE_TOPICS_TABLE_SQL)
    cursor.execute(CREATE_TOPIC_EDGES_TABLE_SQL)
    cursor.execute(CREATE_TOPIC_CLOSURE_TABLE_SQL)
    cursor.execute(CREATE_TOPIC_PATHS_TABLE_SQL)
    for index_query in CREATE_STAGE1_INDEXES_SQL:
        cursor.execute(index_query)

def init_stage2_schema(conn: Connection) -> None:
    init_hierarchy_schema(conn)
    cursor = conn.cursor()
    cursor.execute(CREATE_KNOWLEDGE_ATOMS_TABLE_SQL)
    cursor.execute(CREATE_ATOM_PROVENANCE_TABLE_SQL)
    for index_query in CREATE_STAGE2_INDEXES_SQL:
        cursor.execute(index_query)
