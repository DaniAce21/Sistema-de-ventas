/**
 * Plantilla común de las páginas de error del frontend.
 *
 * La usan:
 *   NoEncontrado     404: la ruta o el evento no existe.
 *   AccesoDenegado   403: el rol no tiene permiso para la sección.
 *   ErrorBoundary    500: error inesperado de la interfaz.
 *
 * Mismo diseño que las plantillas de error de Django
 * (templates/errores/base_error.html).
 *
 * pantallaCompleta: ocupa toda la ventana con fondo oscuro, para
 * cuando la página se muestra fuera de un layout (sin cabecera).
 */

import "./PaginaError.css";

export default function PaginaError({ codigo, icono, titulo, mensaje, acciones, pantallaCompleta = false }) {
  return (
    <section className={`pagina-error ${pantallaCompleta ? "pagina-error--completa" : ""}`}>
      <div className="pagina-error__contenido">
        <div className="pagina-error__icono" aria-hidden="true">{icono}</div>
        <div className="pagina-error__codigo">{codigo}</div>
        <h1>{titulo}</h1>
        <p>{mensaje}</p>
        {acciones && <div className="pagina-error__acciones">{acciones}</div>}
      </div>
    </section>
  );
}
