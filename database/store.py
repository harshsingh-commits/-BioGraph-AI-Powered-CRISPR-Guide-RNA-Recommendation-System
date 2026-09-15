import hashlib
import os
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Gene(Base):
    __tablename__ = "genes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    sequence_length: Mapped[int] = mapped_column(Integer)
    gc_content: Mapped[float] = mapped_column(Float)
    sequence_hash: Mapped[str] = mapped_column(String(64), index=True)


class Guide(Base):
    __tablename__ = "guides"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gene_id: Mapped[int] = mapped_column(Integer, index=True)
    sequence: Mapped[str] = mapped_column(String(64))
    efficiency: Mapped[float] = mapped_column(Float)
    final_score: Mapped[float] = mapped_column(Float)
    risk: Mapped[str] = mapped_column(String(32))


class OffTarget(Base):
    __tablename__ = "off_targets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guide_id: Mapped[int] = mapped_column(Integer, index=True)
    reference: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer)
    mismatches: Mapped[int] = mapped_column(Integer)


class Experiment(Base):
    __tablename__ = "experiments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    gene: Mapped[str] = mapped_column(String(255))
    selected_guide: Mapped[str] = mapped_column(String(64))
    model_version: Mapped[str] = mapped_column(String(128))
    efficiency: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    experiment_id: Mapped[str] = mapped_column(String(64), index=True)
    text_path: Mapped[str] = mapped_column(Text)
    pdf_path: Mapped[str] = mapped_column(Text)
    report_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)


def create_store():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required for PostgreSQL persistence.")
    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def persist_result(result):
    session_factory = create_store()
    ranked = result.get("ranked_guides", [])
    top = ranked[0] if ranked else {}
    sequence = result.get("sequence", "")
    with session_factory() as session:
        gene = Gene(
            name=result.get("gene_name", "N/A"),
            sequence_length=result.get("length", 0),
            gc_content=result.get("gc_content", 0),
            sequence_hash=hashlib.sha256(sequence.encode("ascii")).hexdigest(),
        )
        session.add(gene)
        session.flush()
        for item in ranked:
            session.add(
                Guide(
                    gene_id=gene.id,
                    sequence=item["guide"],
                    efficiency=item.get("efficiency", 0),
                    final_score=item.get("final_score", 0),
                    risk=item.get("risk", "UNKNOWN"),
                )
            )
        session.add(
            Experiment(
                external_id=result.get("experiment_id", "unknown"),
                gene=gene.name,
                selected_guide=top.get("guide", "N/A"),
                model_version=result.get("scoring_model", "gc_heuristic"),
                efficiency=top.get("efficiency", 0),
                risk_score=top.get("risk_score", 100),
            )
        )
        session.commit()
