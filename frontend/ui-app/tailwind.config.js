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
        primary: "#361518",
        secondary: "#502126",
        tertiary: "#7d373e",
        background: "#62272d",
      },
    },
  },
  plugins: [],
};
