/**
 * Etiqueta de estado de un evento o una compra.
 *
 * El color se define en global.css (.badge-PAGADO, .badge-CANCELADO...)
 * y siempre va acompañado del texto (y un ícono en compras), para que
 * el estado no dependa solo del color.
 */

import { ESTADOS_COMPRA, ESTADOS_EVENTO } from "../../utils/categorias";

const ETIQUETAS_EVENTO = Object.fromEntries(ESTADOS_EVENTO.map((e) => [e.valor, e.etiqueta]));

export default function EstadoBadge({ estado }) {
  const compra = ESTADOS_COMPRA[estado];
  const etiqueta = ETIQUETAS_EVENTO[estado] ?? compra?.etiqueta ?? estado;

  return (
    <span className={`badge badge-${estado}`}>
      {compra && <span aria-hidden="true">{compra.icono}</span>}
      {etiqueta}
    </span>
  );
}
