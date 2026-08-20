"""
[모듈] api/app/domains/system/schema.py
[담당] A
[역할] 앱/API 버전 조회 응답 DTO (api 설계서 SYS-003).

[구현할 것]
- AppVersionInfo ({ latestVersion, minRequiredVersion, forceUpdate, updateUrl })
- ServerInfo ({ instanceId, az })
- VersionResponse ({ apiVersion, app, server, clientIp })
    server/clientIp는 프론트 화면(footer)에 서버 식별 정보를 노출하기 위해
    .mypc/프론트Q.md "추가로 여쭤볼 것"에서 요청받아 추가함.

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


class ServerInfo(_CamelModel):
    instance_id: str
    az: str


class VersionResponse(_CamelModel):
    api_version: str
    app: AppVersionInfo
    server: ServerInfo
    client_ip: str | None
