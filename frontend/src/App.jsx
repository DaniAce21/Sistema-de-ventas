/**
 * Rutas de la aplicación, separadas en dos vistas según el rol (RBAC).
 *
 * VISTA ESPECTADOR (EspectadorLayout: cabecera + footer)
 *   /                  Eventos programados              Público
 *   /eventos/:id       Detalle, sectores y compra       Público
 *   /login, /registro  Acceso y creación de cuenta      Público
 *   /carrito           Carro persistente y pago         ESPECTADOR
 *   /mis-tickets       Tickets con UUID y código QR     ESPECTADOR
 *
 * VISTA ADMINISTRADOR (AdminLayout: menú lateral)
 *   /panel                   Dashboard de ventas          ORGANIZADOR
 *   /panel/eventos           Eventos, sectores y stock    ORGANIZADOR
 *   /panel/eventos/nuevo     Crear evento                 ORGANIZADOR
 *   /panel/eventos/:id       Editar evento                ORGANIZADOR
 *   /panel/compras           Estados de las compras       ORGANIZADOR
 *   /panel/documentacion     Swagger / OpenAPI            ORGANIZADOR (exclusivo)
 *
 * Errores: /403 y cualquier otra ruta (404).
 *
 * La seguridad real la aplica el backend; estas rutas solo
 * adaptan la interfaz a lo que cada rol puede hacer.
 */

import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import AdminLayout from "./components/admin/AdminLayout";
import Cargando from "./components/comun/Cargando";
import RutaProtegida from "./components/comun/RutaProtegida";
import EspectadorLayout from "./components/espectador/EspectadorLayout";
import AdminCompras from "./pages/admin/AdminCompras";
import AdminEventos from "./pages/admin/AdminEventos";
import Dashboard from "./pages/admin/Dashboard";
import EventoForm from "./pages/admin/EventoForm";
import Login from "./pages/auth/Login";
import Registro from "./pages/auth/Registro";
import AccesoDenegado from "./pages/errores/AccesoDenegado";
import NoEncontrado from "./pages/errores/NoEncontrado";
import Carrito from "./pages/espectador/Carrito";
import EventoDetalle from "./pages/espectador/EventoDetalle";
import Inicio from "./pages/espectador/Inicio";
import MisTickets from "./pages/espectador/MisTickets";

// Swagger UI es pesado: se descarga solo cuando el admin abre la documentación.
const Documentacion = lazy(() => import("./pages/admin/Documentacion"));

export default function App() {
  return (
    <Routes>
      {/* ---------------- Vista espectador ---------------- */}
      <Route element={<EspectadorLayout />}>
        <Route index element={<Inicio />} />
        <Route path="eventos/:id" element={<EventoDetalle />} />
        <Route path="login" element={<Login />} />
        <Route path="registro" element={<Registro />} />

        <Route element={<RutaProtegida rol="ESPECTADOR" />}>
          <Route path="carrito" element={<Carrito />} />
          <Route path="mis-tickets" element={<MisTickets />} />
        </Route>

        <Route path="403" element={<AccesoDenegado />} />
        <Route path="*" element={<NoEncontrado />} />
      </Route>

      {/* ---------------- Vista administrador ---------------- */}
      <Route element={<RutaProtegida rol="ORGANIZADOR" />}>
        <Route path="panel" element={<AdminLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="eventos" element={<AdminEventos />} />
          <Route path="eventos/nuevo" element={<EventoForm />} />
          <Route path="eventos/:id" element={<EventoForm />} />
          <Route path="compras" element={<AdminCompras />} />
          <Route
            path="documentacion"
            element={
              <Suspense fallback={<Cargando texto="Cargando documentación…" />}>
                <Documentacion />
              </Suspense>
            }
          />
          <Route path="*" element={<NoEncontrado enPanel />} />
        </Route>
      </Route>
    </Routes>
  );
}
