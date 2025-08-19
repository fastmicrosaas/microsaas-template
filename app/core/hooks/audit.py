from datetime import datetime
from sqlalchemy import event
from app.models.audit_mixin import AuditMixin
from app.core.context import get_current_user_id

def before_insert(mapper, connection, target):
    now = datetime.utcnow()
    user_id = get_current_user_id()

    if isinstance(target, AuditMixin):
        if hasattr(target, "created_at"):
            target.created_at = now
        if hasattr(target, "created_by"):
            target.created_by = user_id
        # NO seteamos updated_* en un insert

def before_update(mapper, connection, target):
    now = datetime.utcnow()
    user_id = get_current_user_id()

    if isinstance(target, AuditMixin):
        if hasattr(target, "updated_at"):
            target.updated_at = now
        if hasattr(target, "updated_by"):
            target.updated_by = user_id

def register_audit_listeners(models: list):
    for model in models:
        event.listen(model, "before_insert", before_insert)
        event.listen(model, "before_update", before_update)
