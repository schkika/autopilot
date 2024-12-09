/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,js}",
    "./node_modules/tw-elements/dist/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        sbcolor: "#1c2434",
        sbcolordark: "#24303f",
        maincolor: "#1a222c",
        focuscolor: "#3a4452",
        about: "#06050A",
      },
      width: {
        logoWidth: "50px",
        imgWidth: "800px",
      },
      fontSize: {
        mainHeading: "50px",
        mainHeadingSm: "30px",
        errorPage: "25px",
      },
    },
  },
  darkMode: "class",
  plugins: [require("tw-elements/dist/plugin.cjs")],
};
