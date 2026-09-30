/**
 * Ticket digital de una entrada.
 *
 * El código QR contiene el UUID de la entrada (uuid4 generado por
 * el backend al pagar). En el acceso al evento se escanea el QR y
 * se busca la entrada por ese UUID (por ejemplo desde /admin/).
 */

import { QRCodeSVG } from "qrcode.react";

import { formatoFecha, formatoHora } from "../../utils/formato";
import Afiche from "../comun/Afiche";

import "./Ticket.css";

export default function Ticket({ entrada }) {
  // Datos mínimos para el afiche de respaldo cuando no hay imagen.
  const evento = { nombre: entrada.evento, imagen: entrada.imagen, categoria: entrada.categoria };

  return (
    <article className={`ticket ${entrada.utilizada ? "ticket--usado" : ""}`}>
      <div className="ticket__afiche">
        <Afiche evento={evento} />
      </div>

      <div className="ticket__cuerpo">
        <span className="ticket__etiqueta">Evento</span>
        <h3 className="ticket__evento">{entrada.evento}</h3>

        <dl className="ticket__datos">
          <div>
            <dt>Fecha</dt>
            <dd>{formatoFecha(entrada.evento_fecha)}</dd>
          </div>
          <div>
            <dt>Hora</dt>
            <dd>{formatoHora(entrada.evento_fecha)} hrs</dd>
          </div>
          <div>
            <dt>Recinto</dt>
            <dd>{entrada.recinto}</dd>
          </div>
          <div>
            <dt>Sector</dt>
            <dd>{entrada.sector_nombre}</dd>
          </div>
        </dl>
      </div>

      {/* Talón: separado por una línea punteada con muescas laterales. */}
      <div className="ticket__talon">
        <div className="ticket__qr">
          <QRCodeSVG value={entrada.id} size={116} level="M" bgColor="#ffffff" fgColor="#120f24" />
        </div>
        <code className="ticket__uuid" title="Código único de la entrada (UUID)">
          {entrada.id}
        </code>
        <span className="ticket__compra">
          Compra #{entrada.compra}
          {entrada.utilizada && <span className="badge badge-FINALIZADO">Utilizada</span>}
        </span>
      </div>
    </article>
  );
}
