/**
 * 디자인 토큰 원본. 색상 값의 단일 출처(source of truth)이며,
 * docs/design-system.md의 표와 항상 값이 일치해야 한다.
 * theme.ts는 이 파일의 값만 참조해서 MUI 테마를 구성한다.
 */

export const neutral = {
  white: '#FFFFFF',
  ghostWhite: '#F6F5FA', // 페이지 배경
  gray50: '#F1F0F6',
  gray100: '#E5E4EA',
  gray200: '#D5D4DC',
  gray300: '#B8B7C0',
  gray400: '#9A99A6',
  gray500: '#6B6A76',
  gray600: '#4A4952',
  eerieBlack: '#212121', // 기본 텍스트 · primary
  black: '#000000',
} as const

export const accent = {
  blueSoft: '#D8DFE9', // Alice Blue
  blueMain: '#6E85A6',
  blueDark: '#4F657F',
  greenSoft: '#CFDECA', // Honeydew
  greenMain: '#5C8A5A',
  greenDark: '#3F6B3E',
  yellowSoft: '#EFF0A3', // Vanilla — 배경 전용, 텍스트 색으로 사용 금지(대비 부족)
  yellowMain: '#C9A227',
} as const

export const semantic = {
  successMain: accent.greenMain,
  successSoft: accent.greenSoft,
  warningMain: '#B98900',
  warningSoft: '#F5EEC2',
  errorMain: '#C1554A',
  errorSoft: '#F3D9D6',
  infoMain: accent.blueMain,
  infoSoft: accent.blueSoft,
} as const

/** 좌석 배치도 전용 상태 색상. MUI 팔레트가 아니라 컴포넌트에서 직접 참조. */
export const seat = {
  availableBg: neutral.white,
  availableBorder: accent.blueSoft,
  selectedBg: neutral.eerieBlack,
  selectedText: neutral.white,
  heldBg: neutral.gray50,
  heldBorder: neutral.gray200,
  heldText: neutral.gray400,
  reservedBg: neutral.gray100,
  reservedText: neutral.gray300,
} as const

/** 2026-08-20: 그림자에 이어 radius도 "촌스럽다"는 피드백으로 전면 폐지 — 전부 각진 사각형(0)으로 통일. */
export const radius = {
  sm: 0,
  md: 0,
  lg: 0,
  xl: 0,
  pill: 0,
} as const

export const fontFamily =
  "'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, Roboto, 'Helvetica Neue', sans-serif"
