/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef7ff',
          100: '#d9edff',
          200: '#bce0ff',
          300: '#8ecdff',
          400: '#59b0ff',
          500: '#3390fc',
          600: '#1d70f0',
          700: '#175bdc',
          800: '#1a4bb3',
          900: '#1c428d',
          950: '#152a56',
        },
      },
    },
  },
  plugins: [],
}
