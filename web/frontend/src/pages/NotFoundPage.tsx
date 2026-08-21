import { CenteredMessagePage } from '../components/common/CenteredMessagePage'

export default function NotFoundPage() {
  return (
    <CenteredMessagePage
      eyebrow="404"
      title="페이지를 찾을 수 없어요"
      description="주소를 다시 확인하시거나 홈에서 다시 시작해주세요."
    />
  )
}
