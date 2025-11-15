/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,ts,tsx,jsx,js}'],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#141414',
        'dark-card': '#1a1a1a',
        'dark-border': '#2a2a2a',
      },
      backdrop: {
        blur: {
          xs: '2px',
          sm: '4px',
          md: '12px',
          lg: '24px',
          xl: '40px',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      boxShadow: {
        'neon-blue': '0 0 20px rgba(0, 212, 255, 0.3)',
        'neon-purple': '0 0 20px rgba(139, 92, 246, 0.3)',
        glass: '0 8px 32px rgba(0, 0, 0, 0.1)',
      },
      backdropFilter: {
        glass: 'blur(12px)',
      },
    },
  },
  plugins: [],
  corePlugins: {
    preflight: true,
  },
};
