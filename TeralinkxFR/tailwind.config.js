/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    "./src/components/**/*.{vue,js,ts}",
    "./src/views/**/*.vue",
    "./src/plugins/**/*.js",
    "./src/App.vue",
  ],
  theme: {
    screens: {
      'xs': '420px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
    },
    extend: {
      fontSize: {
        '2xs': '0.625rem', // 10px
        '3xs': '0.5rem',    // 8px
      },
      width: {
        '96': '96%',// 96% width
        '90': '90%',// 90% width
        '80': '80%',// 80% width
        '70': '70%',// 70% width
      },
      colors: {
        bg: {
          light: '#ffffff',
          dark: '#121212',
        },
        card: {
          light: '#f3f4f6', // Tailwind gray-100
          dark: '#1e1e1e',  // Custom dark surface
        },
        text: {
          light: '#1f2937', // gray-800
          dark: '#f9fafb',  // slate-100
        },
      },
      plugins: [],
    },
  }
}