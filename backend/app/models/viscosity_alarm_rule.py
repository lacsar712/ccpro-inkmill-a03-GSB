from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ViscosityAlarmRule(Base):
    __tablename__ = "viscosity_alarm_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mill_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mills.id", ondelete="CASCADE"), nullable=False
    )
    min_pa_s: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    max_pa_s: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    mill: Mapped["Mill"] = relationship("Mill", back_populates="alarm_rules")
    alarm_events: Mapped[list["ViscosityAlarmEvent"]] = relationship(
        "ViscosityAlarmEvent", back_populates="rule"
    )
