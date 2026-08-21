"""
[모듈] api/app/domains/system/schema.py
[담당] A
[역할] 앱/API 버전 조회 응답 DTO (api 설계서 SYS-003).

[구현할 것]
- AppVersionInfo ({ latestVersion, minRequiredVersion, forceUpdate, updateUrl })
- VersionResponse ({ apiVersion, app, clientIp, webIp, apiIp })
    clientIp/webIp/apiIp는 프론트 화면(footer)에 요청 경로를 노출하기 위해
    .mypc/프론트Q.md "추가로 여쭤볼 것"에서 요청받아 추가함. webIp/apiIp는
    .env로 사람이 정해두는 값(예전 instanceId/az)이 아니라 X-Forwarded-For
    체인/소켓에서 그 요청 시점에 실측한 값이라 오토스케일링으로 인스턴스가
    늘어나거나 바뀌어도 별도 설정 없이 항상 맞다.

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
    client_ip: str | None
    web_ip: str | None
    api_ip: str | None
