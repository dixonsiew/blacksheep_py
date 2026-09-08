from blacksheep.server.controllers import APIController


class BaseController(APIController):
    
    @classmethod
    def route(cls) -> str:
        # Returns /api/v1/{derived_class_prefix}
        return f"/smrp/{cls.path()}"

    @classmethod
    def path(cls) -> str:
        # Default behavior placeholder for subclass paths
        return ""