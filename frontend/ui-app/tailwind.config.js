/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        red: "#dd4734",
        green: "#53bd39",
        "black-gray": "#111111",
        "dark-gray": "#191919",
        gray: "#373737",
        primary: "#361518",
        secondary: "#502126",
        tertiary: "#7d373e",
        background: "#62272d",
      },
    },
  },
  plugins: [],
};
