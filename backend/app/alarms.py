from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.mill import Mill
from app.models.viscosity_alarm_event import ViscosityAlarmEvent
from app.models.viscosity_alarm_rule import ViscosityAlarmRule
from app.models.viscosity_sample import ViscositySample


def _fmt(value: Decimal) -> str:
    return f"{float(value):g}"


def evaluate_sample_alarms(db: Session, sample: ViscositySample) -> list[ViscosityAlarmEvent]:
    """Evaluate active alarm rules of the sample's mill and create events.

    An event is created when the viscosity falls outside [minPaS, maxPaS].
    The level is ``critical`` when the excess beyond the bound is greater
    than half of the rule's range width, otherwise ``warn``.
    """
    rules = (
        db.query(ViscosityAlarmRule)
        .filter(
            ViscosityAlarmRule.mill_id == sample.mill_id,
            ViscosityAlarmRule.active.is_(True),
        )
        .all()
    )
    events: list[ViscosityAlarmEvent] = []
    if not rules:
        return events

    mill = db.get(Mill, sample.mill_id)
    mill_code = mill.mill_code if mill else f"#{sample.mill_id}"
    viscosity = Decimal(str(sample.viscosity_pa_s))

    for rule in rules:
        low = Decimal(str(rule.min_pa_s))
        high = Decimal(str(rule.max_pa_s))
        width = high - low
        if width <= 0 or low <= viscosity <= high:
            continue

        if viscosity < low:
            excess = low - viscosity
            direction = f"低于下限 {_fmt(low)} Pa·s"
        else:
            excess = viscosity - high
            direction = f"超出上限 {_fmt(high)} Pa·s"

        level = "critical" if excess > width / 2 else "warn"
        event = ViscosityAlarmEvent(
            rule_id=rule.id,
            sample_id=sample.id,
            triggered_at=datetime.now(),
            level=level,
            message=f"研磨机 {mill_code} 粘度 {_fmt(viscosity)} Pa·s {direction}",
            acked=False,
        )
        db.add(event)
        events.append(event)

    return events
