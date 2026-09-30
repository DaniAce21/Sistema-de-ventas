/**
 * Diálogo de confirmación.
 *
 * Se usa antes de acciones importantes (pagar, cancelar una compra,
 * eliminar un sector) para que el usuario confirme explícitamente.
 *
 * Usa el elemento nativo <dialog> con showModal(): el navegador
 * se encarga del foco, del fondo oscurecido y de cerrar con Escape.
 */

import { useEffect, useRef } from "react";

import "./Modal.css";

export default function Modal({
  abierto,
  titulo,
  children,
  textoConfirmar = "Confirmar",
  textoCancelar = "Cancelar",
  peligro = false,
  procesando = false,
  onConfirmar,
  onCancelar,
}) {
  const dialogo = useRef(null);

  // Sincroniza la prop "abierto" con el estado del <dialog>.
  useEffect(() => {
    const el = dialogo.current;
    if (!el) return;
    if (abierto && !el.open) el.showModal();
    if (!abierto && el.open) el.close();
  }, [abierto]);

  return (
    <dialog
      ref={dialogo}
      className="modal"
      onCancel={(e) => {
        // Escape: se cierra por la prop, no por el navegador.
        e.preventDefault();
        if (!procesando) onCancelar();
      }}
    >
      <h2 className="modal__titulo">{titulo}</h2>
      <div className="modal__cuerpo">{children}</div>
      <div className="modal__acciones">
        <button type="button" className="btn btn-secundario" onClick={onCancelar} disabled={procesando}>
          {textoCancelar}
        </button>
        <button
          type="button"
          className={`btn ${peligro ? "btn-peligro" : "btn-primario"}`}
          onClick={onConfirmar}
          disabled={procesando}
        >
          {procesando ? "Procesando…" : textoConfirmar}
        </button>
      </div>
    </dialog>
  );
}
