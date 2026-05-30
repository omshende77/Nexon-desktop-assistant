/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
      colors: {
        nexon: {
          bg:      '#080810',
          darker:  '#050508',
          card:    'rgba(255,255,255,0.04)',
          border:  'rgba(255,255,255,0.08)',
          purple:  '#7c3aed',
          indigo:  '#4f46e5',
          blue:    '#3b82f6',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'nexon-gradient':  'linear-gradient(135deg, #7c3aed, #4f46e5)',
        'user-bubble':     'linear-gradient(135deg, #4f46e5, #7c3aed)',
      },
      animation: {
        'pulse-slow':    'pulse 3s ease-in-out infinite',
        'glow':          'glow 2s ease-in-out infinite alternate',
        'bounce-subtle': 'bounceSubtle 1.4s ease-in-out infinite',
        'ripple':        'ripple 1.5s linear infinite',
        'slide-up':      'slideUp 0.3s ease-out',
        'fade-in':       'fadeIn 0.4s ease-out',
        'float':         'float 6s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%':   { boxShadow: '0 0 15px rgba(124, 58, 237, 0.3)' },
          '100%': { boxShadow: '0 0 40px rgba(124, 58, 237, 0.7), 0 0 80px rgba(124, 58, 237, 0.2)' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%':      { transform: 'translateY(-4px)' },
        },
        ripple: {
          '0%':   { transform: 'scale(1)',   opacity: '0.6' },
          '100%': { transform: 'scale(2.5)', opacity: '0' },
        },
        slideUp: {
          '0%':   { transform: 'translateY(12px)', opacity: '0' },
          '100%': { transform: 'translateY(0)',    opacity: '1' },
        },
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-10px)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
