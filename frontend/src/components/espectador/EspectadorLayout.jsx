/**
 * Estructura de la vista del espectador: cabecera, página y footer.
 *
 * Un administrador (ORGANIZADOR) no usa esta vista: si entra a una
 * ruta pública se le envía a su panel, porque las vistas de cada
 * rol están separadas.
 */

import { useEffect } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import Footer from "../comun/Footer";
import Header from "./Header";

export default function EspectadorLayout() {
  const { esAdmin } = useAuth();
  const { pathname } = useLocation();

  // Cada cambio de página vuelve al inicio del scroll.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  if (esAdmin) {
    return <Navigate to="/panel" replace />;
  }

  return (
    <>
      <Header />
      <main className="vista-espectador">
        <Outlet />
      </main>
      <Footer />
    </>
  );
}
