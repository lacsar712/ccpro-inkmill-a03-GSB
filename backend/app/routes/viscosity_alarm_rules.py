from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.database import SessionLocal
from app.models.mill import Mill
from app.models.viscosity_alarm_rule import ViscosityAlarmRule
from app.serializers import viscosity_alarm_rule_json
from app.utils import error

bp = Blueprint("viscosity_alarm_rules", __name__, url_prefix="/api/viscosity-alarm-rules")


def _validate(body: dict) -> str | None:
    mill_id = int(body.get("millId") or 0)
    if mill_id <= 0:
        return "请选择研磨机"

    db = SessionLocal()
    try:
        if not db.get(Mill, mill_id):
            return "研磨机不存在"
    finally:
        db.close()

    try:
        min_pa_s = Decimal(str(body.get("minPaS")))
        max_pa_s = Decimal(str(body.get("maxPaS")))
    except (InvalidOperation, ValueError):
        return "粘度上下限必须为数字"
    if not (min_pa_s.is_finite() and max_pa_s.is_finite()):
        return "粘度上下限必须为数字"
    if min_pa_s <= 0 or max_pa_s <= 0:
        return "粘度上下限必须大于 0"
    if min_pa_s >= max_pa_s:
        return "粘度下限必须小于上限"

    return None


@bp.get("")
@jwt_required()
def list_rules():
    mill_id = request.args.get("millId", type=int)
    db = SessionLocal()
    try:
        q = db.query(ViscosityAlarmRule)
        if mill_id:
            q = q.filter(ViscosityAlarmRule.mill_id == mill_id)
        rows = q.order_by(ViscosityAlarmRule.id.desc()).all()
        return jsonify([viscosity_alarm_rule_json(r) for r in rows])
    finally:
        db.close()


@bp.post("")
@jwt_required()
def create_rule():
    body = request.get_json(silent=True) or {}
    err = _validate(body)
    if err:
        return error(err, 400)

    db = SessionLocal()
    try:
        row = ViscosityAlarmRule(
            mill_id=int(body["millId"]),
            min_pa_s=Decimal(str(body["minPaS"])),
            max_pa_s=Decimal(str(body["maxPaS"])),
            active=bool(body.get("active", True)),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return jsonify(viscosity_alarm_rule_json(row)), 201
    finally:
        db.close()


@bp.put("/<int:item_id>")
@jwt_required()
def update_rule(item_id: int):
    body = request.get_json(silent=True) or {}
    err = _validate(body)
    if err:
        return error(err, 400)

    db = SessionLocal()
    try:
        row = db.get(ViscosityAlarmRule, item_id)
        if not row:
            return error("粘度告警规则不存在", 404)

        row.mill_id = int(body["millId"])
        row.min_pa_s = Decimal(str(body["minPaS"]))
        row.max_pa_s = Decimal(str(body["maxPaS"]))
        row.active = bool(body.get("active", True))
        db.commit()
        db.refresh(row)
        return jsonify(viscosity_alarm_rule_json(row))
    finally:
        db.close()


@bp.delete("/<int:item_id>")
@jwt_required()
def delete_rule(item_id: int):
    db = SessionLocal()
    try:
        row = db.get(ViscosityAlarmRule, item_id)
        if not row:
            return error("粘度告警规则不存在", 404)
        db.delete(row)
        db.commit()
        return jsonify({"ok": True})
    finally:
        db.close()
