import { Button, Card, CardContent, Divider, Stack, Typography } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'

const GENDER_LABEL: Record<string, string> = { M: '남성', F: '여성' }

export default function MyInfoPage() {
  const { user } = useAuth()
  if (!user) return null

  return (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <InfoRow label="이메일" value={user.email} />
          <Divider />
          <InfoRow label="닉네임" value={user.nickname} />
          <Divider />
          <InfoRow label="성별" value={user.gender ? (GENDER_LABEL[user.gender] ?? user.gender) : '미입력'} />
          <Divider />
          <InfoRow label="나이대" value={user.ageRange ?? '미입력'} />
        </Stack>
        <Button component={RouterLink} to="/mypage/edit" variant="contained" sx={{ mt: 3 }}>
          정보 수정
        </Button>
      </CardContent>
    </Card>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <Stack direction="row" sx={{ justifyContent: 'space-between' }}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" sx={{ fontWeight: 600 }}>
        {value}
      </Typography>
    </Stack>
  )
}
