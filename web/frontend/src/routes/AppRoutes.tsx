import { Route, Routes } from 'react-router-dom'
import { RootLayout } from '../components/layout/RootLayout'
import NotFoundPage from '../pages/NotFoundPage'
import FailoverPage from '../pages/FailoverPage'
import ComingSoonPage from '../pages/ComingSoonPage'

/**
 * 전체 라우트 표. 아직 만들지 않은 화면은 ComingSoonPage로 채워두고,
 * Phase가 진행될 때마다 해당 라우트의 element만 실제 페이지로 교체한다.
 */
export function AppRoutes() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        {/* Phase 2 — 공연 탐색 */}
        <Route path="/" element={<ComingSoonPage title="공연 목록" />} />
        <Route path="/performances/:performanceId" element={<ComingSoonPage title="공연 상세" />} />
        <Route
          path="/performances/:performanceId/schedules"
          element={<ComingSoonPage title="회차 선택" />}
        />

        {/* Phase 1 — 인증 */}
        <Route path="/login" element={<ComingSoonPage title="로그인" />} />
        <Route path="/signup" element={<ComingSoonPage title="회원가입" />} />
        <Route
          path="/password/reset-request"
          element={<ComingSoonPage title="비밀번호 재설정 요청" />}
        />
        <Route path="/password/reset" element={<ComingSoonPage title="비밀번호 재설정" />} />

        {/* Phase 3 — 예매 / 대기열 */}
        <Route path="/queue/:queueToken" element={<ComingSoonPage title="대기열" />} />
        <Route path="/schedules/:scheduleId/seats" element={<ComingSoonPage title="좌석 선택" />} />
        <Route
          path="/reservations/bank-transfer/new"
          element={<ComingSoonPage title="무통장입금 예매" />}
        />
        <Route
          path="/reservations/bank-transfer/:reservationId"
          element={<ComingSoonPage title="예매 확인" />}
        />

        {/* Phase 4 — 마이페이지 */}
        <Route path="/mypage" element={<ComingSoonPage title="내 정보" />} />
        <Route path="/mypage/edit" element={<ComingSoonPage title="내 정보 수정" />} />
        <Route path="/mypage/reservations" element={<ComingSoonPage title="내 예매 목록" />} />
        <Route path="/mypage/favorites" element={<ComingSoonPage title="관심 공연" />} />

        {/* Phase 5 — 기타 */}
        <Route path="/support" element={<ComingSoonPage title="고객센터" />} />

        <Route path="/failover" element={<FailoverPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>

      {/* 관리자 영역은 일반 사용자 헤더/푸터를 쓰지 않는다 */}
      <Route path="/admin/login" element={<ComingSoonPage title="관리자 로그인" />} />
    </Routes>
  )
}
