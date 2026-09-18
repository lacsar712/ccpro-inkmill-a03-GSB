from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models.viscosity_alarm_event import ViscosityAlarmEvent
from app.models.viscosity_alarm_rule import ViscosityAlarmRule
from app.serializers import viscosity_alarm_event_json
from app.utils import error

bp = Blueprint("viscosity_alarm_events", __name__, url_prefix="/api/viscosity-alarm-events")


@bp.get("")
@jwt_required()
def list_events():
    db = SessionLocal()
    try:
        query = db.query(ViscosityAlarmEvent).join(
            ViscosityAlarmRule, ViscosityAlarmEvent.rule_id == ViscosityAlarmRule.id
        )

        mill_id = request.args.get("millId", type=int)
        if mill_id:
            query = query.filter(ViscosityAlarmRule.mill_id == mill_id)

        acked_arg = request.args.get("acked")
        if acked_arg is not None and acked_arg != "":
            query = query.filter(
                ViscosityAlarmEvent.acked.is_(acked_arg in ("1", "true", "True"))
            )

        level = request.args.get("level")
        if level in ("warn", "critical"):
            query = query.filter(ViscosityAlarmEvent.level == level)

        rows = (
            query.options(
                joinedload(ViscosityAlarmEvent.rule),
                joinedload(ViscosityAlarmEvent.sample),
            )
            .order_by(ViscosityAlarmEvent.triggered_at.desc(), ViscosityAlarmEvent.id.desc())
            .all()
        )
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
            return error("告警事件不存在", 404)
        if not row.acked:
            row.acked = True
            db.commit()
            db.refresh(row)
        return jsonify(viscosity_alarm_event_json(row))
    finally:
        db.close()
