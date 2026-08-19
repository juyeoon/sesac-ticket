import { Box } from '@mui/material'
import ImageNotSupportedOutlinedIcon from '@mui/icons-material/ImageNotSupportedOutlined'

interface PlaceholderImageProps {
  aspectRatio?: string
  iconSize?: number
}

/** 실제 이미지가 없는 mock 단계용 자리표시자. figma 와이어프레임의 회색 X 박스와 같은 역할. */
export function PlaceholderImage({ aspectRatio = '1 / 1', iconSize = 40 }: PlaceholderImageProps) {
  return (
    <Box
      sx={{
        aspectRatio,
        bgcolor: 'grey.100',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 2.5,
      }}
    >
      <ImageNotSupportedOutlinedIcon sx={{ fontSize: iconSize, color: 'grey.300' }} />
    </Box>
  )
}
