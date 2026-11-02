from pathlib import Path
from pydantic import BaseModel

class PipelineConfig(BaseModel):
    base_dir: Path = Path(".")
    data_dir: Path = Path("data")
    database_dir: Path = Path("data/database")
    artifacts_dir: Path = Path("artifacts/runs/stage1_hierarchy")
    sqlite_db_name: str = "asl_knowledge_base.db"
    
    topics_csv_url: str = "https://raw.githubusercontent.com/NoorBayan/ASL/main/data/processed/topics.csv"
    topic_source_csv_url: str = "https://raw.githubusercontent.com/NoorBayan/ASL/main/data/processed/topic_source_contents.csv"
    knowledge_graph_csv_url: str = "https://raw.githubusercontent.com/NoorBayan/ASL/main/data/processed/knowledge_graph.csv"

    @property
    def database_path(self) -> Path:
        return self.database_dir / self.sqlite_db_name

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.database_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
