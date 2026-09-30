/**
 * Error 404: la ruta no existe, o el evento no está disponible
 * (el backend responde 404 para eventos no PROGRAMADOS).
 *
 * enPanel: versión dentro del panel de administración.
 */

import { Link } from "react-router-dom";

import PaginaError from "./PaginaError";

export default function NoEncontrado({ enPanel = false, titulo = "Página no encontrada" }) {
  return (
    <PaginaError
      codigo="404"
      icono="🔍"
      titulo={titulo}
      mensaje="Esta butaca está vacía: lo que buscas no existe, fue movido o ya no está disponible."
      acciones={
        enPanel ? (
          <Link to="/panel" className="btn btn-primario">Volver al dashboard</Link>
        ) : (
          <>
            <Link to="/" className="btn btn-primario">Ver eventos</Link>
            <Link to="/mis-tickets" className="btn btn-secundario">Mis tickets</Link>
          </>
        )
      }
    />
  );
}
