import { Box } from '@mui/material'

interface PlaceholderImageProps {
  /** 포스터 아트를 결정하는 시드 — 보통 공연 id나 제목. 같은 시드는 항상 같은 그림을 만든다. */
  seed: string
  aspectRatio?: string
  /** true면 aspectRatio 대신 부모를 꽉 채움(부모가 position:relative에 height를 갖고 있어야 함) — 히어로 배경용 */
  fill?: boolean
}

// FNV-1a — 문자 하나짜리 시드(예: id "1"~"9")를 넣어도 곱셈 스텝 덕분에 32비트가 골고루 섞여서
// 짧은 숫자 id끼리 색상이 다닥다닥 붙어 보이는 문제(단순 다항 해시의 약점)를 피할 수 있다.
function hashSeed(seed: string): number {
  let h = 0x811c9dc5
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i)
    h = Math.imul(h, 0x01000193)
  }
  return h >>> 0
}

/**
 * 실제 공연 이미지가 없는 자리표시자 — "이미지 없음" 아이콘 대신, 시드값으로 매번 같은
 * 그러데이션 포스터 아트를 생성해서 카드마다 다르게 보이도록 한다(전부 똑같은 회색 박스로
 * 보이면 데모 티가 확 나서 개선함). 글자를 얹었더니 오히려 어색해 보인다는 피드백을 받아
 * 그러데이션만 남김. 채도/명도는 브랜드 파스텔 톤 범위 안으로 고정.
 */
export function PlaceholderImage({ seed, aspectRatio = '1 / 1', fill = false }: PlaceholderImageProps) {
  const h = hashSeed(seed)
  const hue1 = h % 360
  const hue2 = (hue1 + 34 + ((h >> 8) % 55)) % 360
  const angle = (h >> 4) % 360
  const blobX = 20 + (h % 60)
  const blobY = 20 + ((h >> 3) % 60)

  return (
    <Box
      sx={{
        ...(fill ? { position: 'absolute', inset: 0 } : { aspectRatio, position: 'relative' }),
        overflow: 'hidden',
        borderRadius: fill ? 0 : 2.5,
        background: `linear-gradient(${angle}deg, hsl(${hue1}, 58%, 87%), hsl(${hue2}, 55%, 76%))`,
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(circle at ${blobX}% ${blobY}%, hsla(${hue2}, 70%, 96%, 0.55), transparent 55%)`,
        }}
      />
    </Box>
  )
}
