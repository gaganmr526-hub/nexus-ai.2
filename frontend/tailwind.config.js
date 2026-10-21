/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f0f4ff',
          100: '#dce5ff',
          200: '#bfceff',
          300: '#93a8f4',
          400: '#6b7ff0',
          500: '#4f5de8',
          600: '#3d42d0',
          700: '#3133a8',
          800: '#1e2166',
          900: '#141540',
          950: '#0a0b28',
        },
        risk: {
          low: '#22c55e',
          medium: '#f59e0b',
          high: '#ef4444',
          critical: '#7c3aed',
        }
      },
    },
  },
  plugins: [],
}
