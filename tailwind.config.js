/** @type {import('tailwindcss').Config} */

const defaultTheme = require("tailwindcss/defaultTheme");
const colors = require("tailwindcss/colors");

module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
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
};
