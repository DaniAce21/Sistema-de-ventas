/**
 * Selector de cantidad con botones − y +.
 *
 * Limita el valor entre "min" y "max" (el stock disponible),
 * aunque la validación definitiva del stock la hace el backend
 * al momento de pagar.
 */

import "./Cantidad.css";

export default function Cantidad({ valor, onCambio, min = 0, max = 10, etiqueta }) {
  const cambiar = (nuevo) => onCambio(Math.min(max, Math.max(min, nuevo)));

  return (
    <div className="cantidad" role="group" aria-label={etiqueta}>
      <button type="button" onClick={() => cambiar(valor - 1)} disabled={valor <= min} aria-label="Quitar una">
        −
      </button>
      <output aria-live="polite">{valor}</output>
      <button type="button" onClick={() => cambiar(valor + 1)} disabled={valor >= max} aria-label="Agregar una">
        +
      </button>
    </div>
  );
}
