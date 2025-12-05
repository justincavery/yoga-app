/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#E3F2FD',
          100: '#BBDEFB',
          200: '#90CAF9',
          300: '#64B5F6',
          400: '#42A5F5',
          500: '#4A90E2',
          600: '#1E88E5',
          700: '#1976D2',
          800: '#1565C0',
          900: '#0D47A1',
        },
        secondary: {
          50: '#F1F8E9',
          100: '#DCEDC8',
          200: '#C5E1A5',
          300: '#AED581',
          400: '#9CCC65',
          500: '#7CB342',
          600: '#689F38',
          700: '#558B2F',
          800: '#33691E',
          900: '#1B5E20',
        },
        accent: {
          50: '#FFF3E0',
          100: '#FFE0B2',
          200: '#FFCC80',
          300: '#FFB74D',
          400: '#FFA726',
          500: '#FF9800',
          600: '#FB8C00',
          700: '#F57C00',
          800: '#EF6C00',
          900: '#E65100',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'sans-serif'],
        mono: ['Fira Code', 'Courier New', 'Courier', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '100': '25rem',
        '112': '28rem',
        '128': '32rem',
      },
      boxShadow: {
        'primary': '0 4px 14px 0 rgba(74, 144, 226, 0.25)',
        'secondary': '0 4px 14px 0 rgba(124, 179, 66, 0.25)',
      },
      transitionTimingFunction: {
        'yoga': 'cubic-bezier(0.4, 0.0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}
