import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
    "./services/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        border: "hsl(var(--border))",
        muted: {
          DEFAULT: "hsl(var(--muted) / <alpha-value>)",
          foreground: "hsl(var(--muted-foreground) / <alpha-value>)"
        },
        accent: "hsl(var(--accent))",
        success: "hsl(var(--success))",
        danger: "hsl(var(--danger))",
        surface: "hsl(var(--surface) / <alpha-value>)",
        surface2: "hsl(var(--surface-2) / <alpha-value>)",
        rule: "hsl(var(--rule) / <alpha-value>)",
        bull: "hsl(var(--bull) / <alpha-value>)",
        bear: "hsl(var(--bear) / <alpha-value>)",
        accentWarm: "hsl(var(--accent-warm) / <alpha-value>)"
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        mono: ["var(--font-mono)"]
      },
      backgroundImage: {
        grid: "linear-gradient(to right, rgba(83, 167, 191, 0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(83, 167, 191, 0.08) 1px, transparent 1px)"
      },
      boxShadow: {
        panel: "0 0 0 1px rgba(83,167,191,0.08), 0 20px 60px rgba(0,0,0,0.45)"
      }
    }
  },
  plugins: []
};

export default config;
