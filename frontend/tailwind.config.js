/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'finflare': {
          'blue': '#1165C1',  // rgb(17,101,193)
          'green': '#00FF91', // rgb(40, 203, 132)
        }
      },
      fontSize: {
        'label': '20px',
        'input': '18px',
        'button': '1.2em',
        'link': 'large'
      },
      fontFamily: {
        'monaco': ['Monaco', 'monospace']
      }
    },
  },
  plugins: [],
} 