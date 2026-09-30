/**
 * Gestión de estados de las compras.
 *
 * Endpoints (ORGANIZADOR):
 *   GET   /api/compras/?estado=&evento=    Compras de SUS eventos (CompraFilter).
 *   PATCH /api/compras/{id}/estado/        Cambiar estado.
 *
 * Transiciones permitidas (validadas también por el backend):
 *   PENDIENTE -> CANCELADO
 *   PAGADO    -> ENTREGADO | CANCELADO   (CANCELADO repone el stock)
 *   ENTREGADO y CANCELADO son estados finales.
 */

import { useEffect, useState } from "react";

import { api, query } from "../../api/client";
import Cargando from "../../components/comun/Cargando";
import EstadoBadge from "../../components/comun/EstadoBadge";
import Modal from "../../components/comun/Modal";
import Vacio from "../../components/comun/Vacio";
import { ESTADOS_COMPRA } from "../../utils/categorias";
import { formatoFechaCorta, formatoPrecio } from "../../utils/formato";

import "./AdminCompras.css";

// Mismas transiciones que TRANSICIONES_PERMITIDAS en compras/views.py.
const ACCIONES = {
  PENDIENTE: [{ estado: "CANCELADO", texto: "Cancelar", peligro: true }],
  PAGADO: [
    { estado: "ENTREGADO", texto: "Marcar entregada" },
    { estado: "CANCELADO", texto: "Cancelar", peligro: true },
  ],
  ENTREGADO: [],
  CANCELADO: [],
};

export default function AdminCompras() {
  const [filtros, setFiltros] = useState({ estado: "", evento: "" });
  const [eventos, setEventos] = useState([]);
  const [compras, setCompras] = useState(null);
  const [abierta, setAbierta] = useState(null);
  const [confirmar, setConfirmar] = useState(null);
  const [procesando, setProcesando] = useState(false);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");

  // Eventos del organizador para el filtro "evento".
  useEffect(() => {
    api("/eventos/?ordering=fecha").then(setEventos).catch(() => setEventos([]));
  }, []);

  // Recarga las compras al cambiar un filtro.
  useEffect(() => {
    setCompras(null);
    api(`/compras/${query({ ...filtros, ordering: "-creado_en" })}`)
      .then(setCompras)
      .catch((err) => {
        setError(err.message);
        setCompras([]);
      });
  }, [filtros]);

  async function cambiarEstado() {
    const { compra, accion } = confirmar;
    setError("");
    setAviso("");
    setProcesando(true);

    try {
      const respuesta = await api(`/compras/${compra.id}/estado/`, {
        method: "PATCH",
        body: { estado: accion.estado },
      });
      setCompras(compras.map((c) => (c.id === compra.id ? respuesta.compra : c)));
      setAviso(
        accion.estado === "CANCELADO" && compra.estado === "PAGADO"
          ? `Compra #${compra.id} cancelada. El stock de sus sectores fue repuesto.`
          : `Compra #${compra.id} marcada como ${ESTADOS_COMPRA[accion.estado].etiqueta.toLowerCase()}.`
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setProcesando(false);
      setConfirmar(null);
    }
  }

  return (
    <div>
      <div className="panel-cabecera">
        <p>Compras que incluyen entradas de tus eventos.</p>
        <div className="panel-herramientas">
          <label className="sr-only" htmlFor="filtro-estado-compra">Estado</label>
          <select
            id="filtro-estado-compra"
            className="input"
            value={filtros.estado}
            onChange={(e) => setFiltros({ ...filtros, estado: e.target.value })}
          >
            <option value="">Todos los estados</option>
            {Object.entries(ESTADOS_COMPRA).map(([valor, { etiqueta }]) => (
              <option key={valor} value={valor}>{etiqueta}</option>
            ))}
          </select>
          <label className="sr-only" htmlFor="filtro-evento">Evento</label>
          <select
            id="filtro-evento"
            className="input"
            value={filtros.evento}
            onChange={(e) => setFiltros({ ...filtros, evento: e.target.value })}
          >
            <option value="">Todos los eventos</option>
            {eventos.map((ev) => (
              <option key={ev.id} value={ev.id}>{ev.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="alerta alerta-error" role="alert">⚠ {error}</div>}
      {aviso && <div className="alerta alerta-exito">✓ {aviso}</div>}

      {compras === null ? (
        <Cargando texto="Cargando compras…" />
      ) : compras.length === 0 ? (
        <Vacio icono="🧾" titulo="No hay compras para mostrar" texto="Cuando los espectadores compren entradas, aparecerán aquí." />
      ) : (
        <div className="tarjeta tabla-contenedor">
          <table className="tabla compras-tabla">
            <thead>
              <tr>
                <th>Compra</th>
                <th>Comprador</th>
                <th>Fecha</th>
                <th>Estado</th>
                <th className="numero">Total</th>
                <th><span className="sr-only">Acciones</span></th>
              </tr>
            </thead>
            <tbody>
              {compras.map((compra) => (
                <FilaCompra
                  key={compra.id}
                  compra={compra}
                  abierta={abierta === compra.id}
                  onAlternar={() => setAbierta(abierta === compra.id ? null : compra.id)}
                  onAccion={(accion) => setConfirmar({ compra, accion })}
                  procesando={procesando}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        abierto={Boolean(confirmar)}
        titulo={confirmar ? `${confirmar.accion.texto} compra #${confirmar.compra.id}` : ""}
        textoConfirmar={confirmar?.accion.texto}
        peligro={confirmar?.accion.peligro}
        procesando={procesando}
        onConfirmar={cambiarEstado}
        onCancelar={() => setConfirmar(null)}
      >
        {confirmar?.accion.estado === "CANCELADO" ? (
          <>
            <p>La compra pasará a <strong>Cancelado</strong>. Es un estado final.</p>
            {confirmar.compra.estado === "PAGADO" && (
              <p>Las entradas dejarán de ser válidas y el stock de cada sector se repondrá automáticamente.</p>
            )}
          </>
        ) : (
          <p>La compra pasará a <strong>Entregado</strong>. Es un estado final.</p>
        )}
      </Modal>
    </div>
  );
}

/**
 * Fila de una compra con su detalle desplegable (líneas compradas).
 */
function FilaCompra({ compra, abierta, onAlternar, onAccion, procesando }) {
  const acciones = ACCIONES[compra.estado];

  return (
    <>
      <tr className={abierta ? "compras-tabla__abierta" : ""}>
        <td>
          <button type="button" className="compras-tabla__alternar" onClick={onAlternar} aria-expanded={abierta}>
            <span aria-hidden="true">{abierta ? "▾" : "▸"}</span> #{compra.id}
          </button>
        </td>
        <td>{compra.usuario}</td>
        <td className="compras-tabla__fecha">{formatoFechaCorta(compra.creado_en)}</td>
        <td><EstadoBadge estado={compra.estado} /></td>
        <td className="numero"><strong>{formatoPrecio(compra.total)}</strong></td>
        <td>
          <div className="compras-tabla__acciones">
            {acciones.length === 0 ? (
              <span className="texto-suave">Estado final</span>
            ) : (
              acciones.map((accion) => (
                <button
                  key={accion.estado}
                  type="button"
                  className={`btn btn-chico ${accion.peligro ? "btn-peligro" : "btn-secundario"}`}
                  onClick={() => onAccion(accion)}
                  disabled={procesando}
                >
                  {accion.texto}
                </button>
              ))
            )}
          </div>
        </td>
      </tr>

      {abierta && (
        <tr className="compras-tabla__detalle">
          <td colSpan={6}>
            <ul>
              {compra.items.map((item) => (
                <li key={item.id}>
                  <span>{item.sector}</span>
                  <span className="texto-suave">
                    {item.cantidad} × {formatoPrecio(item.precio_unitario)}
                  </span>
                  <strong>{formatoPrecio(item.subtotal)}</strong>
                </li>
              ))}
            </ul>
          </td>
        </tr>
      )}
    </>
  );
}
