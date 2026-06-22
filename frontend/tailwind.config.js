/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#eef3ff',
          100: '#d9e4ff',
          200: '#bcceff',
          300: '#8eaeff',
          400: '#5a83ff',
          500: '#3358f4',
          600: '#2236eb',
          700: '#1b28d0',
          800: '#1d25a8',
          900: '#1e2585',
          950: '#141752',
        },
        surface: '#0f1117',
        panel:   '#161b27',
        border:  '#222840',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
