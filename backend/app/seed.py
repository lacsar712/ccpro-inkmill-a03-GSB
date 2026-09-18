from datetime import datetime, timedelta
from decimal import Decimal

from app.alarm_service import evaluate_sample
from app.auth import hash_password
from app.database import SessionLocal
from app.models.grind_pass import GrindPass
from app.models.mill import Mill
from app.models.user import User
from app.models.viscosity_alarm_rule import ViscosityAlarmRule
from app.models.viscosity_sample import ViscositySample
from app.models.workshop import Workshop


def seed() -> None:
    db = SessionLocal()
    try:
        for username, display_name, role in [
            ("admin", "系统管理员", "admin"),
            ("grinder", "研磨工", "grinder"),
        ]:
            if not db.query(User).filter(User.username == username).first():
                db.add(
                    User(
                        username=username,
                        password_hash=hash_password("123456"),
                        display_name=display_name,
                        role=role,
                    )
                )
        db.commit()

        if db.query(Workshop).count() == 0:
            w1 = Workshop(name="一号油墨车间", site="厂区 A 栋", notes="高固含色浆线")
            w2 = Workshop(name="调墨中心", site="厂区 B 栋", notes="小批量专色")
            db.add_all([w1, w2])
            db.flush()

            m1 = Mill(
                workshop_id=w1.id,
                mill_code="M-01",
                pigment_base="酞菁蓝载体",
                bowl_liters=Decimal("25.00"),
                status="grinding",
            )
            m2 = Mill(
                workshop_id=w1.id,
                mill_code="M-02",
                pigment_base="炭黑载体",
                bowl_liters=Decimal("18.50"),
                status="idle",
            )
            m3 = Mill(
                workshop_id=w2.id,
                mill_code="M-A1",
                pigment_base="专色红载体",
                bowl_liters=Decimal("12.00"),
                status="wash",
            )
            db.add_all([m1, m2, m3])
            db.flush()

            # M-01 粘度告警规则：合格区间 10 ~ 14 Pa·s（宽度 4，半宽 2）
            rule_m1 = ViscosityAlarmRule(
                mill_id=m1.id,
                min_pa_s=Decimal("10.0000"),
                max_pa_s=Decimal("14.0000"),
                active=True,
            )
            db.add(rule_m1)
            db.flush()

            now = datetime.now()
            samples = [
                ViscositySample(
                    mill_id=m1.id,
                    sampled_at=now - timedelta(hours=5),
                    viscosity_pa_s=Decimal("16.5000"),
                    temp_c=Decimal("31.20"),
                    notes="早班超粘，已处理确认",
                ),
                ViscositySample(
                    mill_id=m1.id,
                    sampled_at=now - timedelta(hours=2),
                    viscosity_pa_s=Decimal("12.5000"),
                    temp_c=Decimal("28.50"),
                    notes="首检合格",
                ),
                ViscositySample(
                    mill_id=m1.id,
                    sampled_at=now - timedelta(minutes=30),
                    viscosity_pa_s=Decimal("9.8000"),
                    temp_c=Decimal("29.00"),
                    notes="二检微调，略低于下限",
                ),
                ViscositySample(
                    mill_id=m1.id,
                    sampled_at=now - timedelta(minutes=10),
                    viscosity_pa_s=Decimal("4.5000"),
                    temp_c=Decimal("29.40"),
                    notes="稀释过度，严重偏低",
                ),
                ViscositySample(
                    mill_id=m2.id,
                    sampled_at=now - timedelta(days=1),
                    viscosity_pa_s=Decimal("15.2000"),
                    temp_c=Decimal("27.00"),
                    notes=None,
                ),
            ]
            db.add_all(samples)
            db.flush()

            # 按规则自动判定告警：
            # 16.5 → critical（超限 2.5 > 半宽 2，已确认）
            # 9.8  → warn（超限 0.2，未确认）
            # 4.5  → critical（超限 5.5 > 半宽 2，未确认）
            events = []
            for sample in samples:
                events.extend(evaluate_sample(db, sample))
            db.add_all(events)
            db.flush()
            for event in events:
                if event.triggered_at <= now - timedelta(hours=4):
                    event.acked = True

            db.add_all(
                [
                    GrindPass(
                        mill_id=m1.id,
                        started_at=now - timedelta(hours=3),
                        pass_no=1,
                        duration_min=Decimal("45.00"),
                        media_type="0.8mm 锆珠",
                        operator_name="张研磨",
                    ),
                    GrindPass(
                        mill_id=m1.id,
                        started_at=now - timedelta(hours=2),
                        pass_no=2,
                        duration_min=Decimal("38.00"),
                        media_type="0.8mm 锆珠",
                        operator_name="张研磨",
                    ),
                    GrindPass(
                        mill_id=m2.id,
                        started_at=now - timedelta(days=5),
                        pass_no=1,
                        duration_min=Decimal("60.00"),
                        media_type="1.0mm 玻璃珠",
                        operator_name="李工",
                    ),
                ]
            )
            db.commit()
            print("Seed data inserted.")
        else:
            print("Seed skipped (workshops exist).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
