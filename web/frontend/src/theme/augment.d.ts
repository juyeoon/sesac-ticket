import '@mui/material/styles'

declare module '@mui/material/styles' {
  interface Palette {
    accent: {
      blueSoft: string
      blueMain: string
      greenSoft: string
      greenMain: string
      yellowSoft: string
      yellowMain: string
    }
  }
  interface PaletteOptions {
    accent?: Palette['accent']
  }
}
