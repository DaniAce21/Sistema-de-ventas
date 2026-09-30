/**
 * Footer con los datos del alumno (requisito de la pauta).
 *
 * Los datos NO están escritos aquí: se obtienen del backend
 * (GET /api/alumno/), que los lee de settings.ALUMNO.
 * Así existe un solo lugar donde modificarlos.
 *
 * Variantes:
 *   <Footer />           Footer completo de la vista espectador.
 *   <Footer compacto />  Una sola línea, para el panel de administración.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../../api/client";
import { CATEGORIAS } from "../../utils/categorias";

import "./Footer.css";

export default function Footer({ compacto = false }) {
  const [alumno, setAlumno] = useState(null);

  // Se consulta una sola vez al montar el footer.
  useEffect(() => {
    api("/alumno/").then(setAlumno).catch(() => setAlumno(null));
  }, []);

  const datosAlumno = alumno && (
    <p className="footer__alumno">
      <strong>{alumno.nombre}</strong>
      <span aria-hidden="true"> · </span>
      Sección {alumno.seccion}
      <span aria-hidden="true"> · </span>
      {alumno.anio}
    </p>
  );

  if (compacto) {
    return (
      <footer className="footer footer--compacto">
        <span className="footer__marca-chica">🎟 Butaca · Administración</span>
        {datosAlumno}
      </footer>
    );
  }

  return (
    <footer className="footer">
      <div className="contenedor footer__grid">
        <div>
          <div className="footer__marca">
            <span className="footer__logo" aria-hidden="true">🎟</span>
            Butaca
          </div>
          <p className="footer__lema">
            Tu próxima experiencia empieza aquí. Conciertos, teatro, festivales y más,
            con tickets digitales al instante.
          </p>
        </div>

        <nav aria-label="Categorías">
          <h4>Explorar</h4>
          <ul>
            {CATEGORIAS.slice(0, 5).map((c) => (
              <li key={c.valor}>
                <Link to={`/?categoria=${c.valor}`}>{c.etiqueta}</Link>
              </li>
            ))}
          </ul>
        </nav>

        <nav aria-label="Mi cuenta">
          <h4>Mi cuenta</h4>
          <ul>
            <li><Link to="/mis-tickets">Mis tickets</Link></li>
            <li><Link to="/carrito">Carrito</Link></li>
            <li><Link to="/registro">Crear cuenta</Link></li>
          </ul>
        </nav>

        <div>
          <h4>Compra segura</h4>
          <p className="footer__texto">
            El stock se reserva solo al pagar y cada ticket tiene un código único e intransferible.
          </p>
        </div>
      </div>

      <div className="footer__base">
        <div className="contenedor footer__base-interior">
          <span>© {new Date().getFullYear()} Butaca · Sistema de Venta de Entradas</span>
          {datosAlumno}
        </div>
      </div>
    </footer>
  );
}
