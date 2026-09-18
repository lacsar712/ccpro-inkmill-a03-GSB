"""粘度告警判定服务。

新建粘度取样后调用 evaluate_sample：若该机台存在 active 规则且粘度越界，
则为每条越界规则生成一条 ViscosityAlarmEvent。

级别判定：越界量超过规则区间宽度的一半（strictly greater）记为 critical，
否则记为 warn。
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.mill import Mill
from app.models.viscosity_alarm_event import ViscosityAlarmEvent
from app.models.viscosity_alarm_rule import ViscosityAlarmRule
from app.models.viscosity_sample import ViscositySample

HALF = Decimal("0.5")


def _fmt(value: Decimal) -> str:
    return format(value, "f")


def evaluate_sample(db: Session, sample: ViscositySample) -> list[ViscosityAlarmEvent]:
    rules = (
        db.query(ViscosityAlarmRule)
        .filter(
            ViscosityAlarmRule.mill_id == sample.mill_id,
            ViscosityAlarmRule.active.is_(True),
        )
        .all()
    )
    if not rules:
        return []

    mill = db.get(Mill, sample.mill_id)
    mill_label = mill.mill_code if mill else f"#{sample.mill_id}"
    value = sample.viscosity_pa_s

    events: list[ViscosityAlarmEvent] = []
    for rule in rules:
        lo = rule.min_pa_s
        hi = rule.max_pa_s
        if lo <= value <= hi:
            continue

        width = hi - lo
        if value < lo:
            over = lo - value
            message = (
                f"研磨机 {mill_label} 粘度 {_fmt(value)} Pa·s 低于告警下限 {_fmt(lo)}"
                f"（超限 {_fmt(over)} Pa·s）"
            )
        else:
            over = value - hi
            message = (
                f"研磨机 {mill_label} 粘度 {_fmt(value)} Pa·s 高于告警上限 {_fmt(hi)}"
                f"（超限 {_fmt(over)} Pa·s）"
            )

        level = "critical" if over > width * HALF else "warn"
        events.append(
            ViscosityAlarmEvent(
                rule_id=rule.id,
                sample_id=sample.id,
                triggered_at=sample.sampled_at,
                level=level,
                message=message,
                acked=False,
            )
        )

    return events
