from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.database import SessionLocal
from app.models.viscosity_alarm_event import ViscosityAlarmEvent
from app.models.viscosity_alarm_rule import ViscosityAlarmRule
from app.serializers import viscosity_alarm_event_json
from app.utils import error

bp = Blueprint("viscosity_alarm_events", __name__, url_prefix="/api/viscosity-alarm-events")


def _parse_acked(raw: str | None) -> bool | None:
    if raw in ("true", "1"):
        return True
    if raw in ("false", "0"):
        return False
    return None


@bp.get("")
@jwt_required()
def list_events():
    mill_id = request.args.get("millId", type=int)
    acked = _parse_acked(request.args.get("acked"))

    db = SessionLocal()
    try:
        q = db.query(ViscosityAlarmEvent).join(ViscosityAlarmRule)
        if mill_id:
            q = q.filter(ViscosityAlarmRule.mill_id == mill_id)
        if acked is not None:
            q = q.filter(ViscosityAlarmEvent.acked.is_(acked))
        rows = q.order_by(
            ViscosityAlarmEvent.triggered_at.desc(), ViscosityAlarmEvent.id.desc()
        ).all()
        return jsonify([viscosity_alarm_event_json(r) for r in rows])
    finally:
        db.close()


@bp.post("/<int:item_id>/ack")
@jwt_required()
def ack_event(item_id: int):
    db = SessionLocal()
    try:
        row = db.get(ViscosityAlarmEvent, item_id)
        if not row:
            return error("粘度告警事件不存在", 404)
        row.acked = True
        db.commit()
        db.refresh(row)
        return jsonify(viscosity_alarm_event_json(row))
    finally:
        db.close()
