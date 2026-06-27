/** @type {import('tailwindcss').Config} */

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,vue}'],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        sport: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        energy: {
          50: '#FFF7ED',
          100: '#FFEDD5',
          200: '#FED7AA',
          300: '#FDBA74',
          400: '#FB923C',
          500: '#F97316',
          600: '#EA580C',
          700: '#C2410C',
        },
        ink: {
          900: '#0F172A',
          700: '#334155',
          500: '#64748B',
          300: '#CBD5E1',
          100: '#F1F5F9',
          50: '#F8FAFC',
        },
        gold: '#FBBF24',
        silver: '#9CA3AF',
        bronze: '#B45309',
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans SC', 'system-ui', 'sans-serif'],
        display: ['Inter', 'Noto Sans SC', 'sans-serif'],
        num: ['Inter', 'monospace'],
      },
      borderRadius: {
        sm: '6px',
        md: '8px',
        lg: '12px',
        xl: '20px',
      },
      boxShadow: {
        card: '0 4px 20px rgba(37, 99, 235, 0.08)',
        hover: '0 12px 32px rgba(37, 99, 235, 0.16)',
        energy: '0 8px 24px rgba(249, 115, 22, 0.24)',
      },
      backgroundImage: {
        'gradient-sport': 'linear-gradient(135deg, #2563EB 0%, #3B82F6 50%, #60A5FA 100%)',
        'gradient-energy': 'linear-gradient(135deg, #F97316 0%, #FB923C 50%, #FBBF24 100%)',
        'gradient-track': 'linear-gradient(135deg, #2563EB 0%, #F97316 100%)',
        'gradient-hero': 'linear-gradient(120deg, #1E3A8A 0%, #2563EB 40%, #F97316 100%)',
      },
      animation: {
        'slide-fade': 'slide-fade-in 0.5s cubic-bezier(0.22, 1, 0.36, 1) both',
        'pop': 'pop-in 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) both',
        'medal': 'medal-bounce 1.8s ease-in-out infinite',
        'record': 'record-flash 1.6s ease-out infinite',
      },
      keyframes: {
        'slide-fade-in': {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'pop-in': {
          '0%': { opacity: '0', transform: 'scale(0.85)' },
          '60%': { transform: 'scale(1.05)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'medal-bounce': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        'record-flash': {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(251, 191, 36, 0.6)' },
          '50%': { boxShadow: '0 0 0 8px rgba(251, 191, 36, 0)' },
        },
      },
    },
  },
  plugins: [],
}
