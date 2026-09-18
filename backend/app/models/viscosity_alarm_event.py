from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

ALARM_LEVELS = ("warn", "critical")


class ViscosityAlarmEvent(Base):
    __tablename__ = "viscosity_alarm_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("viscosity_alarm_rules.id", ondelete="CASCADE"),
        nullable=False,
    )
    sample_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("viscosity_samples.id", ondelete="CASCADE"),
        nullable=False,
    )
    triggered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    level: Mapped[str] = mapped_column(String(16), nullable=False, default="warn")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    acked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    rule: Mapped["ViscosityAlarmRule"] = relationship(
        "ViscosityAlarmRule", back_populates="events"
    )
    sample: Mapped["ViscositySample"] = relationship("ViscositySample")
