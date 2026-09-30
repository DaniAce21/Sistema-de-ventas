/**
 * Indicador de carga.
 *
 *   <Cargando />                        Spinner con texto.
 *   <Cargando texto="Buscando…" />
 *   <EsqueletoTarjetas cantidad={8} />  Tarjetas grises mientras llega el catálogo.
 */

import "./Cargando.css";

export default function Cargando({ texto = "Cargando…" }) {
  return (
    <div className="cargando" role="status">
      <span className="cargando__spinner" aria-hidden="true" />
      <span>{texto}</span>
    </div>
  );
}

export function EsqueletoTarjetas({ cantidad = 8 }) {
  return (
    <div className="esqueleto-grid" aria-hidden="true">
      {Array.from({ length: cantidad }, (_, i) => (
        <div key={i} className="esqueleto-tarjeta">
          <div className="esqueleto esqueleto--imagen" />
          <div className="esqueleto esqueleto--linea" />
          <div className="esqueleto esqueleto--linea corta" />
        </div>
      ))}
    </div>
  );
}
