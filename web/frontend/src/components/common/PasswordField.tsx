import { forwardRef, useState } from 'react'
import { IconButton, InputAdornment, TextField, type TextFieldProps } from '@mui/material'
import Visibility from '@mui/icons-material/Visibility'
import VisibilityOff from '@mui/icons-material/VisibilityOff'

/** 눈 모양 아이콘으로 표시/숨김을 토글하는 비밀번호 입력 필드. */
export const PasswordField = forwardRef<HTMLInputElement, TextFieldProps>((props, ref) => {
  const [visible, setVisible] = useState(false)

  return (
    <TextField
      {...props}
      ref={ref}
      type={visible ? 'text' : 'password'}
      slotProps={{
        ...props.slotProps,
        input: {
          ...props.slotProps?.input,
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={() => setVisible((v) => !v)}
                edge="end"
                size="small"
                tabIndex={-1}
                aria-label={visible ? '비밀번호 숨기기' : '비밀번호 표시'}
              >
                {visible ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
              </IconButton>
            </InputAdornment>
          ),
        },
      }}
    />
  )
})

PasswordField.displayName = 'PasswordField'
