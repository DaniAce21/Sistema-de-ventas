/**
 * Punto de entrada de React.
 *
 * Monta la aplicación en <div id="root"> de index.html y la envuelve en:
 * - ErrorBoundary:   muestra una página de error si un componente falla.
 * - BrowserRouter:   navegación entre páginas sin recargar.
 * - AuthProvider:    sesión JWT disponible en todos los componentes.
 * - CarritoProvider: carrito del espectador (contador de la cabecera).
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import ErrorBoundary from "./components/comun/ErrorBoundary";
import { AuthProvider } from "./context/AuthContext";
import { CarritoProvider } from "./context/CarritoContext";

import "./styles/global.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <CarritoProvider>
            <App />
          </CarritoProvider>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>
);
