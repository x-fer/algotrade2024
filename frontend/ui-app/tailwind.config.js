/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        red: "#dd4734",
        darkred: "#9e2b1b",
        green: "#53bd39",
        darkgreen: "#3b7a2c",
        primary: "rgb(29, 40, 57)",
        secondary: "rgb(2, 7, 19)",
        tertiary: "rgb(2, 7, 19)",
        background: "rgb(2, 7, 19)",
      },
    },
  },
  plugins: [],
};
