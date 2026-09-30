/**
 * Detalle de un evento y selección de entradas.
 *
 * Endpoints:
 *   GET  /api/eventos/{id}/            Datos del evento (solo PROGRAMADOS).
 *   GET  /api/eventos/{id}/sectores/   Precio y stock de cada sector.
 *   POST /api/carro-tickets/           Agrega cada sector elegido (ESPECTADOR).
 *
 * Agregar al carrito NO descuenta stock: el backend solo guarda
 * el item en PostgreSQL. El stock se valida y descuenta al pagar.
 */

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../../api/client";
import Afiche from "../../components/comun/Afiche";
import Cantidad from "../../components/comun/Cantidad";
import Cargando from "../../components/comun/Cargando";
import { useAuth } from "../../context/AuthContext";
import { useCarrito } from "../../context/CarritoContext";
import { categoria } from "../../utils/categorias";
import { formatoFecha, formatoHora, formatoPrecio } from "../../utils/formato";
import NoEncontrado from "../errores/NoEncontrado";

import "./EventoDetalle.css";

// Máximo de entradas por sector en una misma selección.
const MAXIMO_POR_SECTOR = 10;

export default function EventoDetalle() {
  const { id } = useParams();
  const { usuario } = useAuth();
  const { agregar } = useCarrito();
  const navigate = useNavigate();

  const [evento, setEvento] = useState(null);
  const [sectores, setSectores] = useState([]);
  const [seleccion, setSeleccion] = useState({});
  const [estado, setEstado] = useState("cargando"); // cargando | listo | no-encontrado | error
  const [error, setError] = useState("");
  const [agregando, setAgregando] = useState(false);
  const [agregado, setAgregado] = useState(false);

  // Carga el evento y sus sectores en paralelo.
  useEffect(() => {
    setEstado("cargando");
    Promise.all([api(`/eventos/${id}/`), api(`/eventos/${id}/sectores/`)])
      .then(([ev, secs]) => {
        setEvento(ev);
        setSectores(secs);
        setEstado("listo");
      })
      .catch((err) => {
        setError(err.message);
        setEstado(err.status === 404 ? "no-encontrado" : "error");
      });
  }, [id]);

  if (estado === "cargando") return <Cargando texto="Cargando evento…" />;
  if (estado === "no-encontrado") return <NoEncontrado titulo="Este evento no está disponible" />;
  if (estado === "error") {
    return (
      <div className="contenedor detalle-error">
        <div className="alerta alerta-error">⚠ {error}</div>
      </div>
    );
  }

  const cat = categoria(evento.categoria);
  const totalEntradas = Object.values(seleccion).reduce((a, b) => a + b, 0);
  const totalPrecio = sectores.reduce((suma, s) => suma + Number(s.precio) * (seleccion[s.id] ?? 0), 0);

  // Agrega cada sector con cantidad > 0 al carrito persistente.
  async function agregarAlCarrito() {
    if (!usuario) {
      navigate("/login", { state: { desde: `/eventos/${id}` } });
      return;
    }

    setError("");
    setAgregando(true);
    try {
      for (const [sectorId, cantidad] of Object.entries(seleccion)) {
        if (cantidad > 0) await agregar(Number(sectorId), cantidad);
      }
      setSeleccion({});
      setAgregado(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setAgregando(false);
    }
  }

  return (
    <article className="detalle">
      {/* ---------- Banner ---------- */}
      <header className="detalle__banner">
        <div className="detalle__banner-fondo" aria-hidden="true">
          <Afiche evento={evento} />
        </div>
        <div className="contenedor detalle__banner-interior">
          <div className="detalle__afiche">
            <Afiche evento={evento} />
          </div>
          <div className="detalle__titulo">
            <Link to="/" className="detalle__volver">← Todos los eventos</Link>
            <span className="detalle__categoria">
              {cat.icono} {cat.etiqueta}
            </span>
            <h1>{evento.nombre}</h1>
            <ul className="detalle__datos">
              <li>📅 <span>{formatoFecha(evento.fecha)}</span></li>
              <li>🕘 <span>{formatoHora(evento.fecha)} hrs</span></li>
              <li>📍 <span>{evento.recinto?.nombre} · {evento.recinto?.direccion}</span></li>
            </ul>
          </div>
        </div>
      </header>

      <div className="contenedor detalle__cuerpo">
        {/* ---------- Información ---------- */}
        <section className="detalle__info">
          <h2>Sobre el evento</h2>
          <p className="detalle__descripcion">
            {evento.descripcion || "El organizador aún no agrega una descripción para este evento."}
          </p>

          <h2>Información importante</h2>
          <ul className="detalle__avisos">
            <li>🎫 Recibirás tus tickets digitales con código QR al instante tras el pago.</li>
            <li>🔒 Cada ticket tiene un código único (UUID) e intransferible.</li>
            <li>🛒 Tu carrito se guarda en tu cuenta: puedes cerrar sesión y continuar después.</li>
            <li>⏱ El stock se reserva solo al pagar; agregar al carrito no garantiza disponibilidad.</li>
          </ul>
        </section>

        {/* ---------- Selección de entradas ---------- */}
        <aside className="tarjeta detalle__compra" aria-labelledby="titulo-entradas">
          <h2 id="titulo-entradas">Selecciona tus entradas</h2>

          {error && <div className="alerta alerta-error">⚠ {error}</div>}

          {agregado && (
            <div className="alerta alerta-exito detalle__agregado">
              <span>✓ Entradas agregadas a tu carrito.</span>
              <Link to="/carrito" className="btn btn-oscuro btn-chico">Ir a pagar</Link>
            </div>
          )}

          {sectores.length === 0 ? (
            <p className="texto-suave">Las entradas de este evento estarán disponibles pronto.</p>
          ) : (
            <ul className="sectores">
              {sectores.map((sector) => {
                const agotado = sector.stock === 0;
                const pocas = !agotado && sector.stock <= 10;

                return (
                  <li key={sector.id} className={`sector ${agotado ? "sector--agotado" : ""}`}>
                    <div className="sector__info">
                      <strong>{sector.nombre}</strong>
                      <span className="sector__precio">{formatoPrecio(sector.precio)}</span>
                      {agotado && <span className="sector__stock sector__stock--agotado">Agotado</span>}
                      {pocas && <span className="sector__stock">¡Últimas {sector.stock}!</span>}
                    </div>
                    {!agotado && (
                      <Cantidad
                        etiqueta={`Cantidad para ${sector.nombre}`}
                        valor={seleccion[sector.id] ?? 0}
                        max={Math.min(sector.stock, MAXIMO_POR_SECTOR)}
                        onCambio={(v) => {
                          setAgregado(false);
                          setSeleccion({ ...seleccion, [sector.id]: v });
                        }}
                      />
                    )}
                  </li>
                );
              })}
            </ul>
          )}

          <div className="detalle__total">
            <span>
              Total <small>({totalEntradas} {totalEntradas === 1 ? "entrada" : "entradas"})</small>
            </span>
            <strong>{formatoPrecio(totalPrecio)}</strong>
          </div>

          <button
            type="button"
            className="btn btn-primario btn-grande btn-bloque"
            onClick={agregarAlCarrito}
            disabled={totalEntradas === 0 || agregando}
          >
            {agregando ? "Agregando…" : usuario ? "Agregar al carrito" : "Inicia sesión para comprar"}
          </button>
        </aside>
      </div>
    </article>
  );
}
