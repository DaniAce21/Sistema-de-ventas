/**
 * Estado vacío: se muestra cuando una lista no tiene elementos
 * (carrito vacío, sin tickets, sin resultados de búsqueda...).
 */

import "./Vacio.css";

export default function Vacio({ icono = "🎟", titulo, texto, children }) {
  return (
    <div className="vacio">
      <div className="vacio__icono" aria-hidden="true">
        {icono}
      </div>
      <h3>{titulo}</h3>
      {texto && <p>{texto}</p>}
      {children && <div className="vacio__acciones">{children}</div>}
    </div>
  );
}
