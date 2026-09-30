import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El frontend corre en http://localhost:5173 y el backend Django
// en http://127.0.0.1:8000.
//
// El proxy reenvía al backend:
//   /api    -> endpoints de la API REST.
//   /media  -> afiches de los eventos subidos por el administrador.
//
// Así el navegador ve todo como del mismo origen y no hace falta CORS.
export default defineConfig({
  plugins: [react()],
  build: {
    // Swagger UI (~1,5 MB) se carga aparte y solo en /panel/documentacion
    // (React.lazy), así que no afecta la carga del sitio del espectador.
    chunkSizeWarningLimit: 1600,
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/media": "http://127.0.0.1:8000",
    },
  },
});
