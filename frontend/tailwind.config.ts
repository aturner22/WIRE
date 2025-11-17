import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: "1.5rem",
        sm: "2rem",
        lg: "3rem",
      },
      screens: {
        "2xl": "1200px", // Max width for content
      },
    },
    extend: {
      colors: {
        // WIRE Design System Colors
        navy: {
          DEFAULT: "#0A1628",  // Primary navy (almost black)
          secondary: "#1E3A5F", // Medium navy
          light: "#2D5F8D",     // Lighter navy accent
        },
        gray: {
          50: "#F8F9FA",
          100: "#E9ECEF",
          200: "#DEE2E6",
          300: "#CED4DA",
          400: "#ADB5BD",
          500: "#6C757D",
          600: "#6C757D",
          700: "#495057",
          800: "#343A40",
          900: "#212529",
        },
        accent: {
          DEFAULT: "#0066CC",   // Professional blue
          hover: "#0052A3",     // Darker on hover
        },
        // Risk level colors (subtle, data-focused)
        risk: {
          1: "#10B981",  // Low - muted green
          2: "#F59E0B",  // Moderate - amber
          3: "#EF4444",  // High - red
          4: "#DC2626",  // Very High - dark red
          5: "#991B1B",  // Extreme - very dark red
        },
        // Semantic mappings for compatibility
        border: "#E9ECEF",
        input: "#DEE2E6",
        ring: "#0066CC",
        background: "#FFFFFF",
        foreground: "#212529",
        primary: {
          DEFAULT: "#0A1628",
          foreground: "#FFFFFF",
        },
        secondary: {
          DEFAULT: "#F8F9FA",
          foreground: "#212529",
        },
        muted: {
          DEFAULT: "#F8F9FA",
          foreground: "#6C757D",
        },
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#212529",
        },
      },
      borderRadius: {
        none: "0",
        sm: "2px",
        DEFAULT: "4px",    // Corporate standard
        md: "4px",
        lg: "4px",         // No large radius
      },
      fontSize: {
        xs: ["11px", { lineHeight: "14px", fontWeight: "500" }],
        sm: ["12px", { lineHeight: "16px", fontWeight: "400" }],
        base: ["14px", { lineHeight: "20px", fontWeight: "400" }],
        lg: ["16px", { lineHeight: "24px", fontWeight: "600" }],
        xl: ["20px", { lineHeight: "28px", fontWeight: "600" }],
        "2xl": ["24px", { lineHeight: "32px", fontWeight: "600" }],
        "3xl": ["32px", { lineHeight: "40px", fontWeight: "600" }],
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        none: "none",
        sm: "0 1px 2px 0 rgba(0, 0, 0, 0.04)",  // Very subtle
        DEFAULT: "0 1px 2px 0 rgba(0, 0, 0, 0.04)",
        md: "0 1px 3px 0 rgba(0, 0, 0, 0.06)",
        lg: "none",  // Disable large shadows
        xl: "none",
        "2xl": "none",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.15s ease-out",
        "accordion-up": "accordion-up 0.15s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
      },
      spacing: {
        18: "4.5rem",  // 72px
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

export default config
