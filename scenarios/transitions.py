from django.core.exceptions import ValidationError
from catalog.models import ScenarioTransition

def can_transition(user_role: str, scenario, to_status) -> None:
    transition = ScenarioTransition.objects.filter(
        is_active=True,
        from_status=scenario.status,
        to_status=to_status,
    ).first()

    if not transition:
        raise ValidationError("Transición no configurada o inactiva.")

    role_ok = (
        (user_role == "COORDINATOR" and transition.allow_coordinator) or
        (user_role == "ANALYST" and transition.allow_analyst) or
        (user_role == "VIEWER" and transition.allow_viewer)
    )
    if not role_ok:
        raise ValidationError("Rol no autorizado para esta transición.")

    if to_status.requires_all_actions_executed:
        pending = scenario.operational_actions.filter(status__code="PENDING").exists()
        if pending:
            raise ValidationError("No se puede pasar de etapa: existen acciones pendientes.")
