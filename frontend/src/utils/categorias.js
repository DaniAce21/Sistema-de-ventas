/**
 * Categorías de eventos.
 *
 * Las claves coinciden con Evento.Categoria (CHOICES) del backend.
 * Cada una tiene un ícono y un degradado propio, usado como afiche
 * de respaldo cuando el administrador no subió una imagen.
 */

export const CATEGORIAS = [
  { valor: "CONCIERTO", etiqueta: "Conciertos", icono: "🎸", fondo: "linear-gradient(135deg,#6d28d9,#ec4899)" },
  { valor: "FESTIVAL", etiqueta: "Festivales", icono: "🎪", fondo: "linear-gradient(135deg,#c026d3,#f97316)" },
  { valor: "TEATRO", etiqueta: "Teatro", icono: "🎭", fondo: "linear-gradient(135deg,#1e1b4b,#7c3aed)" },
  { valor: "STANDUP", etiqueta: "Stand-up", icono: "🎤", fondo: "linear-gradient(135deg,#be185d,#f59e0b)" },
  { valor: "DEPORTE", etiqueta: "Deportes", icono: "🏟️", fondo: "linear-gradient(135deg,#0f766e,#22c55e)" },
  { valor: "FAMILIAR", etiqueta: "Familiar", icono: "🎈", fondo: "linear-gradient(135deg,#0369a1,#a855f7)" },
  { valor: "OTRO", etiqueta: "Otros", icono: "✨", fondo: "linear-gradient(135deg,#334155,#6d28d9)" },
];

const POR_VALOR = Object.fromEntries(CATEGORIAS.map((c) => [c.valor, c]));

export function categoria(valor) {
  return POR_VALOR[valor] ?? POR_VALOR.OTRO;
}

// Estados de un evento (Evento.Estado) y de una compra (Compra.Estado).
export const ESTADOS_EVENTO = [
  { valor: "PROGRAMADO", etiqueta: "Programado" },
  { valor: "FINALIZADO", etiqueta: "Finalizado" },
  { valor: "CANCELADO", etiqueta: "Cancelado" },
];

export const ESTADOS_COMPRA = {
  PENDIENTE: { etiqueta: "Pendiente", icono: "⏳" },
  PAGADO: { etiqueta: "Pagado", icono: "✓" },
  ENTREGADO: { etiqueta: "Entregado", icono: "🎫" },
  CANCELADO: { etiqueta: "Cancelado", icono: "✕" },
};
