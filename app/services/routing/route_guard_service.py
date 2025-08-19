class RouteGuard:
    PUBLIC_PATHS = ["/auth", "/static", "/"]
    PROTECTED_PATHS = ["/dashboard", "/items", "/payments"]

    @staticmethod
    def is_public(path: str) -> bool:
        return any(path == p or path.startswith(p + "/") for p in RouteGuard.PUBLIC_PATHS)

    @staticmethod
    def is_protected(path: str) -> bool:
        return any(path == p or path.startswith(p + "/") for p in RouteGuard.PROTECTED_PATHS)

    @staticmethod
    def should_block_plan_access(path: str) -> bool:
        return not path.startswith("/payments/checkout") and not path.startswith("/payments/paid")

    @staticmethod
    def is_auth_route(path: str) -> bool:
        return path in ["/auth/login", "/auth/register"]
