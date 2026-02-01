/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: "#3B82F6",
        primary: "#3B82F6",
        "background-light": "#F9FAFB",
        "background-dark": "#0F172A",
      },
      fontFamily: {
        display: ["Inter", "PingFang SC", "Microsoft YaHei", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "12px",
      },
    },
  },
  plugins: [],
};
