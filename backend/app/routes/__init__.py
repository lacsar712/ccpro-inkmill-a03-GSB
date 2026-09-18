from app.routes import (
    auth,
    dashboard,
    grind_passes,
    mills,
    viscosity_alarm_events,
    viscosity_alarm_rules,
    viscosity_samples,
    workshops,
)

__all__ = [
    "auth",
    "dashboard",
    "workshops",
    "mills",
    "viscosity_samples",
    "grind_passes",
    "viscosity_alarm_rules",
    "viscosity_alarm_events",
]
