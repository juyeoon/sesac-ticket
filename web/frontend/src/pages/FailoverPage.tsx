import { CenteredMessagePage } from '../components/common/CenteredMessagePage'

/** 요구사항 정의서 TRF-006: 비정상 접근/트래픽 초과 시 이동. API가 아닌 클라이언트 전용 페이지. */
export default function FailoverPage() {
  return (
    <CenteredMessagePage
      eyebrow="일시적인 접속 지연"
      title="지금 접속자가 많아요"
      description="잠시 후 다시 시도해주세요. 예매 정보는 안전하게 보관되고 있어요."
    />
  )
}
