import json
from pathlib import Path
from datetime import datetime
from schemas.task import Task, TaskMetadata
from context_engine.retriever import Document


def load_scenario(scenario_id: int) -> tuple[Task, list[Document], list[str], list[str]]:
    scenario_dir = Path(__file__).parent.parent / "fixtures" / f"scenario{scenario_id}"
    
    with open(scenario_dir / "task.json") as f:
        task_data = json.load(f)
    
    task = Task(
        metadata=TaskMetadata(**task_data["metadata"])
    )
    
    with open(scenario_dir / "permissions.json") as f:
        permissions_data = json.load(f)
    
    allowed_documents = permissions_data["access_control"]["allowed_documents"]
    restricted_documents = permissions_data["access_control"]["restricted_documents"]
    
    documents = []
    
    repo_dir = scenario_dir / "repo"
    if repo_dir.exists():
        for file_path in repo_dir.iterdir():
            if file_path.is_file() and file_path.suffix == ".py":
                content = file_path.read_text()
                stat = file_path.stat()
                timestamp = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
                doc_id = file_path.name
                documents.append(Document(
                    doc_id=doc_id,
                    content=content,
                    source_type="code",
                    timestamp=timestamp
                ))
                if doc_id not in allowed_documents:
                    allowed_documents.append(doc_id)
    
    docs_dir = scenario_dir / "docs"
    if docs_dir.exists():
        for file_path in docs_dir.iterdir():
            if file_path.is_file() and file_path.suffix == ".md":
                content = file_path.read_text()
                
                source_type = _infer_source_type(file_path.name)
                timestamp = _extract_timestamp(content, file_path)
                
                doc_id = file_path.name
                documents.append(Document(
                    doc_id=doc_id,
                    content=content,
                    source_type=source_type,
                    timestamp=timestamp
                ))
    
    return task, documents, allowed_documents, restricted_documents


def _infer_source_type(filename: str) -> str:
    filename_lower = filename.lower()
    if "readme" in filename_lower:
        return "readme"
    elif "architecture" in filename_lower:
        return "architecture_docs"
    elif "api" in filename_lower:
        return "architecture_docs"
    elif "security" in filename_lower:
        return "security_policy"
    elif "meeting" in filename_lower:
        return "meeting_notes"
    else:
        return "readme"


def _extract_timestamp(content: str, file_path: Path) -> str:
    for line in content.split('\n'):
        if "last updated:" in line.lower():
            date_str = line.split(":")[-1].strip()
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                return dt.isoformat()
            except ValueError:
                pass
    
    stat = file_path.stat()
    return datetime.fromtimestamp(stat.st_mtime).isoformat()


def get_raw_doc_size(documents: list[Document]) -> int:
    return sum(len(doc.content) for doc in documents)
