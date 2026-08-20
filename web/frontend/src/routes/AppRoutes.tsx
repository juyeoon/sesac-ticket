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
import QueuePage from '../pages/queue/QueuePage'
import SeatSelectPage from '../pages/reservations/SeatSelectPage'
import BankTransferFormPage from '../pages/reservations/BankTransferFormPage'
import ReservationConfirmPage from '../pages/reservations/ReservationConfirmPage'
import MyPageLayout from '../pages/mypage/MyPageLayout'
import MyInfoPage from '../pages/mypage/MyInfoPage'
import MyInfoEditPage from '../pages/mypage/MyInfoEditPage'
import MyReservationsPage from '../pages/mypage/MyReservationsPage'
import MyFavoritesPage from '../pages/mypage/MyFavoritesPage'

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
        <Route path="/queue/:queueToken" element={<QueuePage />} />
        <Route path="/schedules/:scheduleId/seats" element={<SeatSelectPage />} />
        <Route path="/reservations/bank-transfer/new" element={<BankTransferFormPage />} />
        <Route path="/reservations/bank-transfer/:reservationId" element={<ReservationConfirmPage />} />

        {/* Phase 4 — 마이페이지 */}
        <Route path="/mypage" element={<MyPageLayout />}>
          <Route index element={<MyInfoPage />} />
          <Route path="edit" element={<MyInfoEditPage />} />
          <Route path="reservations" element={<MyReservationsPage />} />
          <Route path="favorites" element={<MyFavoritesPage />} />
        </Route>

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
