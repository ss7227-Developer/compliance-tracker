import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0", // Required inside Docker to be reachable from host
    port: 5173,
    proxy: {
      // In Docker: /api/* → http://api:8000/api/* (Docker internal DNS)
      // Locally:   /api/* → http://localhost:8000/api/* if you set VITE_API_BASE_URL
      "/api": {
        target: "http://api:8000",
        changeOrigin: true,
      },
    },
  },
});
