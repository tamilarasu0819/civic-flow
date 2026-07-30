/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        obsidian: '#090A0F',
        'card-glass': 'rgba(18, 21, 30, 0.75)',
        'accent-cyan': '#00F0FF',
        'accent-purple': '#7000FF',
        'accent-green': '#00FF66',
        'accent-pink': '#FF0055',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      animation: {
        'scan-laser': 'scanLaser 2s linear infinite',
      },
      keyframes: {
        scanLaser: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' }
        }
      }
    },
  },
  plugins: [
    require('tailwind-scrollbar'),
  ],
}
