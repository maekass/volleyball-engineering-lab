"""SQLAlchemy models for signals, targets, benchmarks, and diligence scores."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    Text,
    TypeDecorator,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class DecimalText(TypeDecorator):
    """Decimal stored as text so SQLite round-trips the exact score."""

    impl = String(32)
    cache_ok = True

    def process_bind_param(self, value: Decimal | None, dialect: object) -> str | None:
        if value is None:
            return None
        return format(Decimal(value), "f")

    def process_result_value(self, value: str | None, dialect: object) -> Decimal | None:
        if value is None:
            return None
        return Decimal(value)


class AwareDateTime(TypeDecorator):
    """Store UTC and always return a timezone-aware datetime."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: object) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamps must be timezone-aware")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect: object) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


class Base(DeclarativeBase):
    pass


_HTTP_SOURCE_URL = "source_url LIKE 'https://%' OR source_url LIKE 'http://%'"


def _http_source_constraint(table: str) -> CheckConstraint:
    return CheckConstraint(_HTTP_SOURCE_URL, name=f"ck_{table}_source_url_http")


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (_http_source_constraint("signals"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    signal_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(AwareDateTime, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)


class Target(Base):
    __tablename__ = "targets"
    __table_args__ = (_http_source_constraint("targets"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)
    pillar: Mapped[str] = mapped_column(String(128), nullable=False)
    record_status: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(AwareDateTime, nullable=False)


class ClinicalBenchmarkRow(Base):
    __tablename__ = "clinical_benchmarks"
    __table_args__ = (_http_source_constraint("clinical_benchmarks"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    benchmark_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    cohort_id: Mapped[str] = mapped_column(String(128), nullable=False)
    position: Mapped[str] = mapped_column(String(32), nullable=False)
    metric: Mapped[str] = mapped_column(String(64), nullable=False)
    mean_value: Mapped[str] = mapped_column(String(32), nullable=False)
    sd_value: Mapped[str | None] = mapped_column(String(32), nullable=True)
    unit: Mapped[str] = mapped_column(String(64), nullable=False)
    citation: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(AwareDateTime, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)


class DiligenceScoreRow(Base):
    __tablename__ = "diligence_scores"
    __table_args__ = (_http_source_constraint("diligence_scores"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False)
    technical_ingestion: Mapped[Decimal] = mapped_column(DecimalText, nullable=False)
    workflow_lock_in: Mapped[Decimal] = mapped_column(DecimalText, nullable=False)
    catalyst: Mapped[Decimal] = mapped_column(DecimalText, nullable=False)
    exit_path: Mapped[Decimal] = mapped_column(DecimalText, nullable=False)
    composite: Mapped[Decimal] = mapped_column(DecimalText, nullable=False)
    gate_pass: Mapped[bool] = mapped_column(Boolean, nullable=False)
    input_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(AwareDateTime, nullable=False)

    @classmethod
    def from_result(cls, result: object, computed_at: datetime) -> DiligenceScoreRow:
        return cls(
            target_id=result.target_id,  # type: ignore[attr-defined]
            technical_ingestion=result.technical_ingestion,  # type: ignore[attr-defined]
            workflow_lock_in=result.workflow_lock_in,  # type: ignore[attr-defined]
            catalyst=result.catalyst,  # type: ignore[attr-defined]
            exit_path=result.exit_path,  # type: ignore[attr-defined]
            composite=result.composite,  # type: ignore[attr-defined]
            gate_pass=result.gate_pass,  # type: ignore[attr-defined]
            input_sha256=result.input_sha256,  # type: ignore[attr-defined]
            source_url=result.source_url,  # type: ignore[attr-defined]
            computed_at=computed_at,
        )


def create_engine_for(path: Path):
    from sqlalchemy import create_engine

    return create_engine(f"sqlite:///{path}")


def session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
