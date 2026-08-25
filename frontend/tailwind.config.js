/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  theme: {
    extend: {
      colors: {
        paper: "#F6F5F0",
        ink: "#0A0A0A",
        ash: "#4A4A4A",
        orange: {
          DEFAULT: "#FF5C00",
          hover: "#E05200",
        },
        highlighter: "#E5FF00",
        electric: "#0038FF",
        sale: "#FF0055",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
      },
      fontFamily: {
        display: ['Anton', 'Impact', 'sans-serif'],
        heading: ['"Archivo"', 'system-ui', 'sans-serif'],
        body: ['"Archivo"', 'system-ui', 'sans-serif'],
        mono: ['"Space Mono"', 'monospace'],
      },
      boxShadow: {
        brutal: "4px 4px 0px 0px #0A0A0A",
        'brutal-lg': "6px 6px 0px 0px #0A0A0A",
        'brutal-xl': "8px 8px 0px 0px #0A0A0A",
        'brutal-orange': "4px 4px 0px 0px #FF5C00",
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        'accordion-down': { from: { height: '0' }, to: { height: 'var(--radix-accordion-content-height)' } },
        'accordion-up': { from: { height: 'var(--radix-accordion-content-height)' }, to: { height: '0' } },
      },
      animation: {
        marquee: 'marquee 22s linear infinite',
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
