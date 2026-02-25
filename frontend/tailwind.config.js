/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Classification severity colours — used in badges and charts
        oai: "#ef4444", // red   — Official Action Indicated (most severe)
        vai: "#f59e0b", // amber — Voluntary Action Indicated
        nai: "#22c55e", // green — No Action Indicated (compliant)
      },
    },
  },
  plugins: [],
};
