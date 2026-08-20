export interface SupportPostSeed {
  id: number
  title: string
  content: string
  category: string
  createdAt: string
}

export const SUPPORT_CATEGORIES = ['공지', '이용안내', '자주묻는질문']

export const supportPosts: SupportPostSeed[] = [
  {
    id: 1,
    title: '새싹티켓 서비스 오픈 안내',
    content: '안녕하세요, 새싹티켓입니다.\n오늘부터 정식 서비스를 시작합니다. 많은 이용 부탁드립니다.',
    category: '공지',
    createdAt: '2026-08-01T09:00:00+09:00',
  },
  {
    id: 2,
    title: '무통장입금 이용 시 유의사항',
    content:
      '좌석 선점 후 24시간 이내에 안내된 계좌로 입금해주셔야 예매가 확정됩니다.\n입금자명이 예매 시 입력한 이름과 다를 경우 확인이 지연될 수 있습니다.',
    category: '이용안내',
    createdAt: '2026-08-02T10:30:00+09:00',
  },
  {
    id: 3,
    title: '예매 취소는 어떻게 하나요?',
    content: '마이페이지 > 내 예매 목록에서 예매 상세로 진입 후 취소 요청을 남겨주시면 순차적으로 처리해드립니다.',
    category: '자주묻는질문',
    createdAt: '2026-08-03T11:00:00+09:00',
  },
  {
    id: 4,
    title: '대기열은 왜 있나요?',
    content: '한정된 좌석에 동시 접속이 몰릴 경우 서버 부하를 줄이고 공정한 선착순 배정을 위해 대기열을 운영합니다.',
    category: '자주묻는질문',
    createdAt: '2026-08-04T09:20:00+09:00',
  },
  {
    id: 5,
    title: '8월 정기 점검 안내',
    content: '보다 안정적인 서비스 제공을 위해 아래 일정으로 정기 점검을 진행합니다.\n일시: 2026-08-15 02:00 ~ 04:00',
    category: '공지',
    createdAt: '2026-08-05T14:00:00+09:00',
  },
  {
    id: 6,
    title: '좌석 등급별 가격 안내',
    content: 'R석/S석/VIP석 등 공연마다 등급 구성과 가격이 다르니 공연 상세 페이지에서 확인해주세요.',
    category: '이용안내',
    createdAt: '2026-08-06T13:10:00+09:00',
  },
  {
    id: 7,
    title: '회원가입 시 이메일 인증이 안 돼요',
    content: '스팸함을 먼저 확인해주세요. 그래도 안 오면 인증번호 재발송 버튼을 눌러 다시 시도해주세요.',
    category: '자주묻는질문',
    createdAt: '2026-08-07T15:45:00+09:00',
  },
  {
    id: 8,
    title: '관심 공연 등록은 어디서 하나요?',
    content: '공연 상세 페이지의 하트 아이콘을 눌러 등록/해제할 수 있고, 마이페이지 > 관심 공연에서 모아볼 수 있습니다.',
    category: '이용안내',
    createdAt: '2026-08-08T09:50:00+09:00',
  },
  {
    id: 9,
    title: '추석 연휴 고객센터 운영시간 안내',
    content: '연휴 기간 중에는 고객센터 응대가 지연될 수 있는 점 양해 부탁드립니다.',
    category: '공지',
    createdAt: '2026-08-09T10:00:00+09:00',
  },
  {
    id: 10,
    title: '비밀번호를 잊어버렸어요',
    content: '로그인 화면의 "비밀번호를 잊으셨나요?" 링크를 눌러 이메일 인증 후 재설정할 수 있습니다.',
    category: '자주묻는질문',
    createdAt: '2026-08-10T16:20:00+09:00',
  },
  {
    id: 11,
    title: '결제 수단 추가 안내',
    content: '현재는 무통장입금만 지원하며, 카드 결제는 순차적으로 지원 예정입니다.',
    category: '공지',
    createdAt: '2026-08-11T11:30:00+09:00',
  },
  {
    id: 12,
    title: '한 번에 몇 좌석까지 예매할 수 있나요?',
    content: '1회 예매 시 최대 4석까지 선택할 수 있습니다.',
    category: '자주묻는질문',
    createdAt: '2026-08-12T12:00:00+09:00',
  },
]
