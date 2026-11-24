/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f0f7f4',
          100: '#dceee5',
          200: '#bcdfcb',
          300: '#93caaa',
          400: '#64af84',
          500: '#3e9363',
          600: '#2d774d',
          700: '#245f3f',
          800: '#1e4b33',
          900: '#173a28',
          950: '#0c2217',
        },
        water: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        earth: {
          50: '#faf8f5',
          100: '#f4ede4',
          200: '#e8dbca',
          300: '#d7c0a6',
          400: '#c3a280',
          500: '#b28962',
          600: '#9e7352',
          700: '#7e5a42',
          800: '#674a38',
          900: '#553e31',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
