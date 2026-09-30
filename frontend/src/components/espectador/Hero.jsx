/**
 * Carrusel de eventos destacados (portada del catálogo).
 *
 * Muestra los próximos eventos a pantalla ancha con su afiche
 * difuminado de fondo. Avanza solo cada 6 segundos; se pausa al
 * pasar el mouse y se puede navegar con los puntos inferiores.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { categoria } from "../../utils/categorias";
import { formatoFecha, formatoHora, formatoPrecio } from "../../utils/formato";
import Afiche from "../comun/Afiche";

import "./Hero.css";

const INTERVALO_MS = 6000;

export default function Hero({ eventos }) {
  const [actual, setActual] = useState(0);
  const [pausado, setPausado] = useState(false);

  // Rotación automática entre los eventos destacados.
  useEffect(() => {
    if (pausado || eventos.length < 2) return;
    const temporizador = setInterval(() => setActual((i) => (i + 1) % eventos.length), INTERVALO_MS);
    return () => clearInterval(temporizador);
  }, [pausado, eventos.length]);

  if (eventos.length === 0) return null;

  const evento = eventos[Math.min(actual, eventos.length - 1)];
  const cat = categoria(evento.categoria);

  return (
    <section
      className="hero"
      aria-roledescription="carrusel"
      aria-label="Eventos destacados"
      onMouseEnter={() => setPausado(true)}
      onMouseLeave={() => setPausado(false)}
    >
      {/* Fondo: el mismo afiche, ampliado y difuminado. */}
      <div className="hero__fondo" aria-hidden="true">
        <Afiche evento={evento} />
      </div>

      <div className="contenedor hero__interior" key={evento.id}>
        <div className="hero__texto">
          <span className="hero__etiqueta">
            {cat.icono} {cat.etiqueta} · Destacado
          </span>
          <h1>{evento.nombre}</h1>
          <p className="hero__datos">
            📅 {formatoFecha(evento.fecha)} · {formatoHora(evento.fecha)} hrs
            <br />📍 {evento.recinto?.nombre}
          </p>
          <div className="hero__acciones">
            <Link to={`/eventos/${evento.id}`} className="btn btn-primario btn-grande">
              Comprar entradas
            </Link>
            {evento.precio_desde !== null && (
              <span className="hero__precio">
                Desde <strong>{formatoPrecio(evento.precio_desde)}</strong>
              </span>
            )}
          </div>
        </div>

        <Link to={`/eventos/${evento.id}`} className="hero__afiche" tabIndex={-1} aria-hidden="true">
          <Afiche evento={evento} />
        </Link>
      </div>

      {eventos.length > 1 && (
        <div className="hero__puntos">
          {eventos.map((e, i) => (
            <button
              key={e.id}
              type="button"
              className={i === actual ? "activo" : ""}
              onClick={() => setActual(i)}
              aria-label={`Ver ${e.nombre}`}
              aria-current={i === actual}
            />
          ))}
        </div>
      )}
    </section>
  );
}
