/**
 * Afiche de un evento.
 *
 * Muestra la imagen subida por el administrador. Si el evento no
 * tiene imagen (o no carga), dibuja un afiche de respaldo con el
 * degradado y el ícono de su categoría, para que el catálogo
 * nunca muestre espacios vacíos.
 */

import { useState } from "react";

import { categoria } from "../../utils/categorias";

import "./Afiche.css";

export default function Afiche({ evento, className = "" }) {
  const [fallo, setFallo] = useState(false);
  const cat = categoria(evento.categoria);

  if (evento.imagen && !fallo) {
    return (
      <img
        className={`afiche ${className}`}
        src={evento.imagen}
        alt={`Afiche de ${evento.nombre}`}
        loading="lazy"
        onError={() => setFallo(true)}
      />
    );
  }

  return (
    <div className={`afiche afiche--respaldo ${className}`} style={{ background: cat.fondo }} role="img" aria-label={evento.nombre}>
      <span className="afiche__icono" aria-hidden="true">
        {cat.icono}
      </span>
      <span className="afiche__nombre">{evento.nombre}</span>
    </div>
  );
}
