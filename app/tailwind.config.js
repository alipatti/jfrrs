/** @type {import('tailwindcss').Config} */

const defaultTheme = require("tailwindcss/defaultTheme");
const colors = require("tailwindcss/colors");

module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [ // force tailwind to include these classes for dynamic sizing of logo
    "text-sm",
    "text-base",
    "text-lg",
    "text-xl",
    "text-2xl",
    "text-3xl",
    "text-4xl",
    "text-5xl",
    "text-6xl",
    "text-7xl",
    "text-8xl",
    "text-9xl",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Karla", ...defaultTheme.fontFamily.sans],
        jeff: "Rock Salt",
      },
      colors: {
        grey: colors.neutral,
        primary: colors.sky,
        secondary: colors.amber,
      },
    },
  },
  plugins: [],
};
