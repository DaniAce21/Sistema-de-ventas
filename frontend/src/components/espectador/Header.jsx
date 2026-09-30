/**
 * Cabecera de la vista del espectador.
 *
 * - Logo y buscador de eventos (usa ?search= del catálogo, SearchFilter de DRF).
 * - Enlaces según la sesión:
 *     Visitante:   Ingresar / Crear cuenta.
 *     Espectador:  Eventos, Mis tickets, carrito con contador y menú de usuario.
 */

import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useNavigate, useSearchParams } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { useCarrito } from "../../context/CarritoContext";

import "./Header.css";

export default function Header() {
  const { usuario, logout } = useAuth();
  const { cantidadTotal } = useCarrito();
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const [busqueda, setBusqueda] = useState(params.get("search") ?? "");
  const [menuAbierto, setMenuAbierto] = useState(false);
  const menu = useRef(null);

  // Mantiene el buscador sincronizado con la URL (?search=...).
  useEffect(() => {
    setBusqueda(params.get("search") ?? "");
  }, [params]);

  // Cierra el menú de usuario al hacer clic fuera de él.
  useEffect(() => {
    function cerrar(e) {
      if (menu.current && !menu.current.contains(e.target)) setMenuAbierto(false);
    }
    document.addEventListener("click", cerrar);
    return () => document.removeEventListener("click", cerrar);
  }, []);

  function buscar(e) {
    e.preventDefault();
    const texto = busqueda.trim();
    navigate(texto ? `/?search=${encodeURIComponent(texto)}` : "/");
  }

  // Cerrar sesión no borra el carrito: sigue guardado en PostgreSQL.
  function cerrarSesion() {
    setMenuAbierto(false);
    logout();
    navigate("/");
  }

  const iniciales = usuario?.username.slice(0, 2).toUpperCase();

  return (
    <header className="header">
      <div className="contenedor header__interior">
        <Link to="/" className="header__marca" aria-label="Butaca, inicio">
          <span className="header__logo" aria-hidden="true">🎟</span>
          <span>Butaca</span>
        </Link>

        <form className="header__buscador" role="search" onSubmit={buscar}>
          <span aria-hidden="true">🔍</span>
          <label htmlFor="buscador" className="sr-only">Buscar eventos</label>
          <input
            id="buscador"
            type="search"
            placeholder="Buscar artistas, eventos o recintos"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </form>

        <nav className="header__nav" aria-label="Principal">
          <NavLink to="/" end className="header__link">
            Eventos
          </NavLink>

          {usuario ? (
            <>
              <NavLink to="/mis-tickets" className="header__link">
                Mis tickets
              </NavLink>

              <NavLink to="/carrito" className="header__carrito" aria-label={`Carrito, ${cantidadTotal} entradas`}>
                <span aria-hidden="true">🛒</span>
                {cantidadTotal > 0 && <span className="header__contador">{cantidadTotal}</span>}
              </NavLink>

              <div className="header__usuario" ref={menu}>
                <button
                  type="button"
                  className="header__avatar"
                  onClick={() => setMenuAbierto(!menuAbierto)}
                  aria-expanded={menuAbierto}
                  aria-haspopup="menu"
                >
                  <span className="header__iniciales" aria-hidden="true">{iniciales}</span>
                  <span className="header__nombre">{usuario.username}</span>
                </button>

                {menuAbierto && (
                  <div className="header__menu" role="menu">
                    <div className="header__menu-cabecera">
                      <strong>{usuario.username}</strong>
                      <span>Espectador</span>
                    </div>
                    <Link role="menuitem" to="/mis-tickets" onClick={() => setMenuAbierto(false)}>
                      🎫 Mis tickets
                    </Link>
                    <Link role="menuitem" to="/carrito" onClick={() => setMenuAbierto(false)}>
                      🛒 Mi carrito
                    </Link>
                    <button role="menuitem" type="button" onClick={cerrarSesion}>
                      ↩ Cerrar sesión
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="header__link">
                Ingresar
              </Link>
              <Link to="/registro" className="btn btn-primario btn-chico">
                Crear cuenta
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
