import { CenteredMessagePage } from '../components/common/CenteredMessagePage'

interface ComingSoonPageProps {
  title: string
}

/** 다음 Phase에서 구현될 라우트의 임시 자리표시자. */
export default function ComingSoonPage({ title }: ComingSoonPageProps) {
  return (
    <CenteredMessagePage
      eyebrow="다음 단계에서 구현 예정"
      title={title}
      description="이 화면은 다음 Phase에서 채워질 예정입니다."
    />
  )
}
