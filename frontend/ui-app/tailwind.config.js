/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        red: "#dd4734",
        "black-gray": "#111111",
        "dark-gray": "#191919",
      },
    },
  },
  plugins: [],
};
