from blacksheep.server.controllers import APIController, abstract


@abstract()
class BaseController(APIController):
    
    @classmethod
    def route(cls) -> str:
        # Returns /api/v1/{derived_class_prefix}
        return f"/smrp/{cls.path()}"

    @classmethod
    def path(cls) -> str:
        # Default behavior placeholder for subclass paths
        return ""

@abstract()
class BaseSetupController(BaseController):
    
    @classmethod
    def path(cls) -> str:
        # Returns /setup/{derived_class_prefix}
        return "api"