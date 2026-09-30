/**
 * Tarjeta de evento del catálogo (estilo ticketing).
 *
 * Muestra el afiche, un "calendario" con día y mes, la categoría,
 * el nombre, el recinto y el precio más bajo ("Desde $20.000").
 * precio_desde y disponibles vienen calculados por el backend
 * con annotate(Min, Sum) en la misma consulta del catálogo.
 */

import { Link } from "react-router-dom";

import { categoria } from "../../utils/categorias";
import { formatoHora, formatoPrecio, partesFecha } from "../../utils/formato";
import Afiche from "../comun/Afiche";

import "./EventoCard.css";

export default function EventoCard({ evento }) {
  const { dia, mes } = partesFecha(evento.fecha);
  const agotado = evento.disponibles === 0 && evento.precio_desde !== null;
  const cat = categoria(evento.categoria);

  return (
    <Link to={`/eventos/${evento.id}`} className="evento-card">
      <div className="evento-card__imagen">
        <Afiche evento={evento} />

        <div className="evento-card__fecha" aria-label={`Fecha: ${dia} ${mes}`}>
          <span className="evento-card__dia">{dia}</span>
          <span className="evento-card__mes">{mes}</span>
        </div>

        {agotado && <span className="evento-card__agotado">Agotado</span>}
      </div>

      <div className="evento-card__cuerpo">
        <span className="evento-card__categoria">
          <span aria-hidden="true">{cat.icono}</span> {cat.etiqueta}
        </span>
        <h3 className="evento-card__nombre">{evento.nombre}</h3>
        <p className="evento-card__lugar">
          📍 {evento.recinto?.nombre} · {formatoHora(evento.fecha)} hrs
        </p>

        <div className="evento-card__pie">
          {evento.precio_desde !== null ? (
            <span className="evento-card__precio">
              <small>Desde</small> {formatoPrecio(evento.precio_desde)}
            </span>
          ) : (
            <span className="evento-card__precio evento-card__precio--pronto">Próximamente</span>
          )}
          <span className="evento-card__cta" aria-hidden="true">
            {agotado ? "Ver" : "Comprar"} →
          </span>
        </div>
      </div>
    </Link>
  );
}
