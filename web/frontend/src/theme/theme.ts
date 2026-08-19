import { createTheme } from '@mui/material/styles'
import { koKR } from '@mui/material/locale'
import { accent, fontFamily, neutral, radius, semantic } from './tokens'
import './augment.d.ts'

export const theme = createTheme(
  {
    palette: {
      mode: 'light',
      primary: {
        main: neutral.eerieBlack,
        light: neutral.gray600,
        dark: neutral.black,
        contrastText: neutral.white,
      },
      secondary: {
        main: accent.blueMain,
        light: accent.blueSoft,
        dark: accent.blueDark,
        contrastText: neutral.white,
      },
      success: { main: semantic.successMain, contrastText: neutral.white },
      warning: { main: semantic.warningMain, contrastText: neutral.white },
      error: { main: semantic.errorMain, contrastText: neutral.white },
      info: { main: semantic.infoMain, contrastText: neutral.white },
      background: {
        default: neutral.ghostWhite,
        paper: neutral.white,
      },
      text: {
        primary: neutral.eerieBlack,
        secondary: neutral.gray500,
        disabled: neutral.gray300,
      },
      divider: neutral.gray100,
      accent: {
        blueSoft: accent.blueSoft,
        blueMain: accent.blueMain,
        greenSoft: accent.greenSoft,
        greenMain: accent.greenMain,
        yellowSoft: accent.yellowSoft,
        yellowMain: accent.yellowMain,
      },
    },
    shape: {
      borderRadius: radius.md,
    },
    typography: {
      fontFamily,
      h1: { fontWeight: 700, fontSize: '2.5rem', lineHeight: 1.25, letterSpacing: '-0.01em' },
      h2: { fontWeight: 700, fontSize: '2rem', lineHeight: 1.3, letterSpacing: '-0.01em' },
      h3: { fontWeight: 700, fontSize: '1.75rem', lineHeight: 1.3 },
      h4: { fontWeight: 600, fontSize: '1.5rem', lineHeight: 1.35 },
      h5: { fontWeight: 600, fontSize: '1.25rem', lineHeight: 1.4 },
      h6: { fontWeight: 600, fontSize: '1.125rem', lineHeight: 1.4 },
      subtitle1: { fontWeight: 500, fontSize: '1rem', lineHeight: 1.5 },
      subtitle2: { fontWeight: 500, fontSize: '0.875rem', lineHeight: 1.5 },
      body1: { fontWeight: 400, fontSize: '0.9375rem', lineHeight: 1.6 },
      body2: { fontWeight: 400, fontSize: '0.875rem', lineHeight: 1.6 },
      caption: { fontWeight: 400, fontSize: '0.75rem', lineHeight: 1.5 },
      button: { fontWeight: 600, fontSize: '0.9375rem', textTransform: 'none' },
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: neutral.ghostWhite,
          },
        },
      },
      MuiButton: {
        defaultProps: { disableElevation: true },
        styleOverrides: {
          root: {
            borderRadius: radius.pill,
            paddingInline: 20,
            paddingBlock: 10,
          },
          sizeLarge: {
            paddingInline: 28,
            paddingBlock: 12,
            fontSize: '1rem',
          },
          outlined: {
            borderColor: neutral.gray200,
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: radius.pill,
            fontWeight: 500,
          },
        },
      },
      MuiPaper: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
          rounded: {
            borderRadius: radius.xl,
          },
        },
      },
      MuiCard: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: {
            borderRadius: radius.xl,
            border: `1px solid ${neutral.gray100}`,
          },
        },
      },
      MuiTextField: {
        defaultProps: { size: 'medium' },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: radius.md,
          },
        },
      },
      MuiAppBar: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: {
            backgroundColor: neutral.white,
            color: neutral.eerieBlack,
            borderBottom: `1px solid ${neutral.gray100}`,
          },
        },
      },
    },
  },
  koKR,
)
