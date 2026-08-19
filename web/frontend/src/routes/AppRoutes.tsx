import { Navigate, Route, Routes } from 'react-router-dom'
import { RootLayout } from '../components/layout/RootLayout'
import NotFoundPage from '../pages/NotFoundPage'
import FailoverPage from '../pages/FailoverPage'
import ComingSoonPage from '../pages/ComingSoonPage'
import LoginPage from '../pages/auth/LoginPage'
import SignupPage from '../pages/auth/SignupPage'
import PasswordResetPage from '../pages/auth/PasswordResetPage'
import PerformanceListPage from '../pages/performances/PerformanceListPage'
import PerformanceDetailPage from '../pages/performances/PerformanceDetailPage'
import ScheduleSelectPage from '../pages/performances/ScheduleSelectPage'

/**
 * 전체 라우트 표. 아직 만들지 않은 화면은 ComingSoonPage로 채워두고,
 * Phase가 진행될 때마다 해당 라우트의 element만 실제 페이지로 교체한다.
 */
export function AppRoutes() {
  return (
    <Routes>
      <Route element={<RootLayout />}>
        {/* Phase 2 — 공연 탐색 */}
        <Route path="/" element={<PerformanceListPage />} />
        <Route path="/performances/:performanceId" element={<PerformanceDetailPage />} />
        <Route path="/performances/:performanceId/schedules" element={<ScheduleSelectPage />} />

        {/* Phase 1 — 인증 */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        {/* figma 와이어프레임이 요청(이메일 인증)과 재설정을 한 화면으로 합쳐놨어서 하나로 통일 */}
        <Route path="/password/reset" element={<PasswordResetPage />} />
        <Route path="/password/reset-request" element={<Navigate to="/password/reset" replace />} />

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
