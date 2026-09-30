/**
 * Estructura de la vista del administrador (ORGANIZADOR).
 *
 * Menú lateral oscuro con las secciones del panel, barra superior
 * con el título de la sección y el usuario, contenido y footer.
 *
 * La documentación de la API (Swagger) solo aparece en este menú:
 * el espectador nunca la ve y el backend además la protege con
 * el permiso IsGestor.
 */

import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import Footer from "../comun/Footer";

import "./AdminLayout.css";

// Secciones del menú lateral.
const SECCIONES = [
  { ruta: "/panel", icono: "📊", texto: "Dashboard", fin: true },
  { ruta: "/panel/eventos", icono: "🎤", texto: "Eventos e inventario" },
  { ruta: "/panel/compras", icono: "🧾", texto: "Compras" },
  { ruta: "/panel/documentacion", icono: "📘", texto: "Documentación API" },
];

// Título de la barra superior según la ruta actual.
function tituloSeccion(pathname) {
  if (pathname.startsWith("/panel/eventos/nuevo")) return "Nuevo evento";
  if (/^\/panel\/eventos\/\d+/.test(pathname)) return "Editar evento";
  const seccion = [...SECCIONES].reverse().find((s) => pathname.startsWith(s.ruta));
  return seccion?.texto ?? "Panel";
}

export default function AdminLayout() {
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [menuMovil, setMenuMovil] = useState(false);

  // Al navegar se cierra el menú en móvil y se vuelve arriba.
  useEffect(() => {
    setMenuMovil(false);
    window.scrollTo(0, 0);
  }, [pathname]);

  function cerrarSesion() {
    logout();
    navigate("/login");
  }

  return (
    <div className={`admin ${menuMovil ? "admin--menu-abierto" : ""}`}>
      {/* ---------- Menú lateral ---------- */}
      <aside className="admin__lateral">
        <div className="admin__marca">
          <span className="admin__logo" aria-hidden="true">🎟</span>
          <div>
            <strong>Butaca</strong>
            <span>Administración</span>
          </div>
        </div>

        <nav className="admin__nav" aria-label="Panel de administración">
          <span className="admin__nav-titulo">Gestión</span>
          {SECCIONES.map((s) => (
            <NavLink key={s.ruta} to={s.ruta} end={s.fin} className="admin__enlace">
              <span aria-hidden="true">{s.icono}</span>
              {s.texto}
            </NavLink>
          ))}

          <span className="admin__nav-titulo">Otros accesos</span>
          <a className="admin__enlace" href="http://127.0.0.1:8000/admin/" target="_blank" rel="noreferrer">
            <span aria-hidden="true">🛠</span>
            Panel Django ↗
          </a>
        </nav>

        <div className="admin__perfil">
          <span className="admin__avatar" aria-hidden="true">
            {usuario.username.slice(0, 2).toUpperCase()}
          </span>
          <div>
            <strong>{usuario.username}</strong>
            <span>Administrador</span>
          </div>
          <button type="button" className="admin__salir" onClick={cerrarSesion} title="Cerrar sesión" aria-label="Cerrar sesión">
            ↩
          </button>
        </div>
      </aside>

      {/* Fondo que cierra el menú al tocar fuera (móvil). */}
      <button type="button" className="admin__velo" aria-label="Cerrar menú" onClick={() => setMenuMovil(false)} />

      {/* ---------- Contenido ---------- */}
      <div className="admin__principal">
        <header className="admin__barra">
          <button
            type="button"
            className="admin__menu-boton"
            onClick={() => setMenuMovil(true)}
            aria-label="Abrir menú"
          >
            ☰
          </button>
          <h1>{tituloSeccion(pathname)}</h1>
        </header>

        <main className="admin__contenido">
          <Outlet />
        </main>

        <Footer compacto />
      </div>
    </div>
  );
}
