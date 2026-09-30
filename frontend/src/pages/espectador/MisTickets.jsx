/**
 * Tickets del espectador.
 *
 * Endpoint: GET /api/mis-entradas/  (ESPECTADOR)
 *
 * El backend devuelve solo las entradas del usuario del JWT,
 * de compras PAGADAS o ENTREGADAS (las canceladas no se muestran).
 * Cada ticket muestra un QR con su UUID v4 generado al pagar.
 *
 * Pestañas:
 *   Próximos  -> eventos cuya fecha aún no pasa.
 *   Pasados   -> eventos ya realizados.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../../api/client";
import Cargando from "../../components/comun/Cargando";
import Vacio from "../../components/comun/Vacio";
import Ticket from "../../components/espectador/Ticket";

import "./MisTickets.css";

export default function MisTickets() {
  const [entradas, setEntradas] = useState(null);
  const [error, setError] = useState("");
  const [pestana, setPestana] = useState("proximos");

  useEffect(() => {
    api("/mis-entradas/")
      .then(setEntradas)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="contenedor tickets">
        <div className="alerta alerta-error">⚠ {error}</div>
      </div>
    );
  }

  if (!entradas) return <Cargando texto="Cargando tus tickets…" />;

  // Separa los tickets según la fecha del evento.
  const ahora = new Date();
  const proximos = entradas
    .filter((e) => new Date(e.evento_fecha) >= ahora)
    .sort((a, b) => new Date(a.evento_fecha) - new Date(b.evento_fecha));
  const pasados = entradas.filter((e) => new Date(e.evento_fecha) < ahora);
  const lista = pestana === "proximos" ? proximos : pasados;

  return (
    <div className="contenedor tickets">
      <h1 className="titulo-pagina">Mis tickets</h1>
      <p className="subtitulo">Presenta el código QR en el acceso. Cada código es único y válido una sola vez.</p>

      <div className="pestanas" role="tablist" aria-label="Filtrar tickets">
        <button
          type="button"
          role="tab"
          aria-selected={pestana === "proximos"}
          className={pestana === "proximos" ? "activa" : ""}
          onClick={() => setPestana("proximos")}
        >
          Próximos <span className="pestanas__conteo">{proximos.length}</span>
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={pestana === "pasados"}
          className={pestana === "pasados" ? "activa" : ""}
          onClick={() => setPestana("pasados")}
        >
          Pasados <span className="pestanas__conteo">{pasados.length}</span>
        </button>
      </div>

      {lista.length === 0 ? (
        <Vacio
          icono="🎫"
          titulo={pestana === "proximos" ? "No tienes tickets para próximos eventos" : "Aún no tienes eventos pasados"}
          texto={pestana === "proximos" ? "Cuando compres entradas, tus tickets aparecerán aquí al instante." : undefined}
        >
          {pestana === "proximos" && (
            <Link to="/" className="btn btn-primario">Explorar eventos</Link>
          )}
        </Vacio>
      ) : (
        <div className="tickets__lista">
          {lista.map((entrada) => (
            <Ticket key={entrada.id} entrada={entrada} />
          ))}
        </div>
      )}
    </div>
  );
}
