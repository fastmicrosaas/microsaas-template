import contextvars

_user_id_ctx_var = contextvars.ContextVar("user_id", default=None)

def set_current_user_id(user_id: int):
    _user_id_ctx_var.set(user_id)

def get_current_user_id() -> int | None:
    return _user_id_ctx_var.get()
