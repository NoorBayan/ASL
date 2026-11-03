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

CREATE_RELATION_TYPES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS relation_types (
    relation_type_id TEXT PRIMARY KEY,
    relation_name_en TEXT NOT NULL,
    relation_name_ar TEXT NOT NULL,
    category TEXT NOT NULL,
    is_directed INTEGER DEFAULT 1,
    is_symmetric INTEGER DEFAULT 0,
    inverse_relation TEXT,
    description TEXT
);
"""

CREATE_KNOWLEDGE_RELATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS knowledge_relations (
    relation_id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_id INTEGER NOT NULL,
    object_type TEXT NOT NULL,
    context_topic_id INTEGER,
    weight REAL DEFAULT 1.0,
    confidence_score REAL NOT NULL,
    confidence_level TEXT NOT NULL,
    relation_summary TEXT,
    relation_description TEXT,
    review_status TEXT DEFAULT 'approved',
    FOREIGN KEY (predicate) REFERENCES relation_types(relation_type_id)
);
"""

CREATE_REVIEW_HISTORY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS review_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    reviewer_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    reason TEXT
);
"""

CREATE_DATASET_VERSIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS dataset_versions (
    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_tag TEXT NOT NULL,
    topics_count INTEGER NOT NULL,
    atoms_count INTEGER NOT NULL,
    relations_count INTEGER NOT NULL,
    total_nodes INTEGER NOT NULL,
    total_edges INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

CREATE_STAGE3_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_rel_source ON knowledge_relations(source_id, source_type);",
    "CREATE INDEX IF NOT EXISTS idx_rel_object ON knowledge_relations(object_id, object_type);",
    "CREATE INDEX IF NOT EXISTS idx_rel_predicate ON knowledge_relations(predicate);",
    "CREATE INDEX IF NOT EXISTS idx_rel_confidence ON knowledge_relations(confidence_score);"
]

CREATE_STAGE4_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_review_entity ON review_history(entity_type, entity_id);",
    "CREATE INDEX IF NOT EXISTS idx_review_timestamp ON review_history(timestamp);"
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

def init_stage3_schema(conn: Connection) -> None:
    init_stage2_schema(conn)
    cursor = conn.cursor()
    cursor.execute(CREATE_RELATION_TYPES_TABLE_SQL)
    cursor.execute(CREATE_KNOWLEDGE_RELATIONS_TABLE_SQL)
    for index_query in CREATE_STAGE3_INDEXES_SQL:
        cursor.execute(index_query)

def init_stage4_schema(conn: Connection) -> None:
    init_stage3_schema(conn)
    cursor = conn.cursor()
    cursor.execute(CREATE_REVIEW_HISTORY_TABLE_SQL)
    cursor.execute(CREATE_DATASET_VERSIONS_TABLE_SQL)
    for index_query in CREATE_STAGE4_INDEXES_SQL:
        cursor.execute(index_query)
