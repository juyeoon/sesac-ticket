"""
[모듈] api/app/domains/system/schema.py
[담당] A
[역할] 앱/API 버전 조회 응답 DTO (api 설계서 SYS-003).

[구현할 것]
- AppVersionInfo ({ latestVersion, minRequiredVersion, forceUpdate, updateUrl })
- VersionResponse ({ apiVersion, app })

[의존]
- pydantic

[호출자]
- app.domains.system.router
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class AppVersionInfo(_CamelModel):
    latest_version: str
    min_required_version: str
    force_update: bool
    update_url: str


class VersionResponse(_CamelModel):
    api_version: str
    app: AppVersionInfo
