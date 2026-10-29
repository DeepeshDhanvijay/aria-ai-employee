import os
import sqlite3
from pathlib import Path
from uuid import uuid4

from .models import Approval, Business, KnowledgeDocument


def _database_path(database_url: str) -> str:
    if database_url.startswith("sqlite:///"):
        return database_url.removeprefix("sqlite:///")
    if database_url.startswith("sqlite://"):
        return database_url.removeprefix("sqlite://")
    raise ValueError("Only SQLite DATABASE_URL values are supported by the local MVP")


class _BusinessCollection:
    def __init__(self, store: "Store") -> None:
        self.store = store

    def __contains__(self, business_id: str) -> bool:
        return self.store.get_business_optional(business_id) is not None

    def __getitem__(self, business_id: str) -> Business:
        business = self.store.get_business_optional(business_id)
        if business is None:
            raise KeyError(business_id)
        return business

    def __setitem__(self, business_id: str, business: Business) -> None:
        self.store.save_business(business)

    def clear(self) -> None:
        with self.store.connection:
            self.store.connection.execute("DELETE FROM businesses")


class _ApprovalCollection:
    def __init__(self, store: "Store") -> None:
        self.store = store

    def get(self, approval_id: str) -> Approval | None:
        return self.store.get_approval(approval_id)

    def values(self) -> list[Approval]:
        return self.store.list_all_approvals()

    def clear(self) -> None:
        with self.store.connection:
            self.store.connection.execute("DELETE FROM approvals")


class _DocumentCollection:
    def __init__(self, store: "Store") -> None:
        self.store = store

    def append(self, document: KnowledgeDocument) -> None:
        self.store.save_document(document)

    def clear(self) -> None:
        with self.store.connection:
            self.store.connection.execute("DELETE FROM documents")


class Store:
    def __init__(self, database_url: str | None = None) -> None:
        path = _database_path(database_url or os.getenv("DATABASE_URL", "sqlite:///./aria.db"))
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._create_tables()
        self.businesses = _BusinessCollection(self)
        self.approvals = _ApprovalCollection(self)
        self.documents = _DocumentCollection(self)

    def _create_tables(self) -> None:
        with self.connection:
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS businesses (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    timezone TEXT NOT NULL,
                    auto_approve_categories TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    page INTEGER
                );
                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY,
                    business_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def get_business_optional(self, business_id: str) -> Business | None:
        row = self.connection.execute("SELECT * FROM businesses WHERE id = ?", (business_id,)).fetchone()
        if row is None:
            return None
        return Business.model_validate(
            {
                "id": row["id"],
                "name": row["name"],
                "timezone": row["timezone"],
                "auto_approve_categories": row["auto_approve_categories"].split(",")
                if row["auto_approve_categories"]
                else [],
            }
        )

    def save_business(self, business: Business) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT OR REPLACE INTO businesses (id, name, timezone, auto_approve_categories) VALUES (?, ?, ?, ?)",
                (business.id, business.name, business.timezone, ",".join(business.auto_approve_categories)),
            )

    def get_business(self, business_id: str) -> Business:
        business = self.get_business_optional(business_id)
        if business is None:
            raise KeyError(business_id)
        return business

    def save_document(self, document: KnowledgeDocument) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO documents (business_id, title, content, page) VALUES (?, ?, ?, ?)",
                (document.business_id, document.title, document.content, document.page),
            )

    def list_documents(self, business_id: str | None = None) -> list[KnowledgeDocument]:
        if business_id is None:
            rows = self.connection.execute("SELECT * FROM documents").fetchall()
        else:
            rows = self.connection.execute("SELECT * FROM documents WHERE business_id = ?", (business_id,)).fetchall()
        return [KnowledgeDocument.model_validate(dict(row)) for row in rows]

    def create_approval(self, business_id: str, action_type: str, payload: dict) -> Approval:
        approval = Approval(id=str(uuid4()), business_id=business_id, action_type=action_type, payload=payload)
        import json

        with self.connection:
            self.connection.execute(
                "INSERT INTO approvals (id, business_id, action_type, payload, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    approval.id,
                    approval.business_id,
                    approval.action_type,
                    json.dumps(approval.payload),
                    approval.status,
                    approval.created_at.isoformat(),
                ),
            )
        return approval

    def get_approval(self, approval_id: str) -> Approval | None:
        import json

        row = self.connection.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,)).fetchone()
        if row is None:
            return None
        return Approval.model_validate({**dict(row), "payload": json.loads(row["payload"])})

    def list_all_approvals(self) -> list[Approval]:
        rows = self.connection.execute("SELECT id FROM approvals ORDER BY created_at DESC").fetchall()
        return [approval for row in rows if (approval := self.get_approval(row["id"])) is not None]

    def update_approval(self, approval: Approval) -> None:
        import json

        with self.connection:
            self.connection.execute(
                "UPDATE approvals SET status = ? WHERE id = ?",
                (approval.status, approval.id),
            )
