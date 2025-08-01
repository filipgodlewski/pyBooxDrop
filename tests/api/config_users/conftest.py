from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture

from boox.models.config_users import SyncTokenResponse


@register_fixture
class FakeSyncTokenResponse(ModelFactory[SyncTokenResponse]):
    __check_model__ = True
