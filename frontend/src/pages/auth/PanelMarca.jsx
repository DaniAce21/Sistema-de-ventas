/**
 * Panel decorativo de la marca para las pantallas de acceso.
 * Se oculta en pantallas angostas (ver Auth.css).
 */

export default function PanelMarca({ titulo, texto }) {
  return (
    <aside className="auth__marca" aria-hidden="true">
      <div className="auth__marca-interior">
        <span className="auth__logo">🎟</span>
        <h2>{titulo}</h2>
        <p>{texto}</p>

        {/* Mini ticket ilustrativo. */}
        <div className="auth__ticket">
          <div>
            <span>Ticket digital</span>
            <strong>Acceso general</strong>
          </div>
          <div className="auth__ticket-qr" />
        </div>
      </div>
    </aside>
  );
}
