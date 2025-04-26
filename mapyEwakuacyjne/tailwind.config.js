/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html',
    './templates/**/*.html',
    './**/forms.py',
  ],
  theme: {
    extend: {
      // Miejsce na ew. rozszerzenia
    }
  },
  plugins: [
    // Miejsce na ew. wtyczki
  ],
}