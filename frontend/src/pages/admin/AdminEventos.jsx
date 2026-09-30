/**
 * Listado de eventos del administrador.
 *
 * Endpoint: GET /api/eventos/  (como ORGANIZADOR devuelve SUS eventos
 * en cualquier estado, no solo los PROGRAMADOS).
 *
 * Filtros enviados al backend (django-filter):
 *   ?search=      SearchFilter
 *   ?estado=      ChoiceFilter sobre Evento.Estado
 *   ?categoria=   ChoiceFilter sobre Evento.Categoria
 *
 * Eliminar: DELETE /api/eventos/{id}/. Si el evento ya tiene entradas
 * vendidas, el backend lo impide (on_delete=PROTECT) y responde 400.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, query } from "../../api/client";
import Afiche from "../../components/comun/Afiche";
import Cargando from "../../components/comun/Cargando";
import EstadoBadge from "../../components/comun/EstadoBadge";
import Modal from "../../components/comun/Modal";
import Vacio from "../../components/comun/Vacio";
import { CATEGORIAS, ESTADOS_EVENTO, categoria } from "../../utils/categorias";
import { formatoFechaCorta, formatoNumero, formatoPrecio } from "../../utils/formato";

import "./AdminEventos.css";

export default function AdminEventos() {
  const [filtros, setFiltros] = useState({ search: "", estado: "", categoria: "" });
  const [eventos, setEventos] = useState(null);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const [eliminar, setEliminar] = useState(null);
  const [procesando, setProcesando] = useState(false);

  // Recarga el listado al cambiar un filtro (con espera para el buscador).
  useEffect(() => {
    const espera = setTimeout(() => {
      api(`/eventos/${query({ ...filtros, ordering: "fecha" })}`)
        .then(setEventos)
        .catch((err) => setError(err.message));
    }, 250);
    return () => clearTimeout(espera);
  }, [filtros]);

  const cambiar = (e) => setFiltros({ ...filtros, [e.target.name]: e.target.value });

  async function confirmarEliminar() {
    setProcesando(true);
    setError("");
    try {
      await api(`/eventos/${eliminar.id}/`, { method: "DELETE" });
      setEventos(eventos.filter((e) => e.id !== eliminar.id));
      setAviso(`"${eliminar.nombre}" fue eliminado.`);
    } catch (err) {
      setError(err.message);
    } finally {
      setProcesando(false);
      setEliminar(null);
    }
  }

  return (
    <div>
      <div className="panel-cabecera">
        <p>Crea eventos, sube afiches y administra el stock de cada sector.</p>
        <Link to="/panel/eventos/nuevo" className="btn btn-primario">+ Nuevo evento</Link>
      </div>

      {/* ---------- Filtros ---------- */}
      <div className="panel-herramientas admin-eventos__filtros">
        <label className="sr-only" htmlFor="buscar-evento">Buscar</label>
        <input
          id="buscar-evento"
          name="search"
          type="search"
          className="input"
          placeholder="🔍 Buscar por nombre o recinto"
          value={filtros.search}
          onChange={cambiar}
        />
        <label className="sr-only" htmlFor="filtro-estado">Estado</label>
        <select id="filtro-estado" name="estado" className="input" value={filtros.estado} onChange={cambiar}>
          <option value="">Todos los estados</option>
          {ESTADOS_EVENTO.map((e) => (
            <option key={e.valor} value={e.valor}>{e.etiqueta}</option>
          ))}
        </select>
        <label className="sr-only" htmlFor="filtro-categoria">Categoría</label>
        <select id="filtro-categoria" name="categoria" className="input" value={filtros.categoria} onChange={cambiar}>
          <option value="">Todas las categorías</option>
          {CATEGORIAS.map((c) => (
            <option key={c.valor} value={c.valor}>{c.etiqueta}</option>
          ))}
        </select>
      </div>

      {error && <div className="alerta alerta-error" role="alert">⚠ {error}</div>}
      {aviso && <div className="alerta alerta-exito">✓ {aviso}</div>}

      {/* ---------- Listado ---------- */}
      {eventos === null ? (
        <Cargando texto="Cargando eventos…" />
      ) : eventos.length === 0 ? (
        <Vacio icono="🎤" titulo="No hay eventos" texto="Crea un evento o ajusta los filtros.">
          <Link to="/panel/eventos/nuevo" className="btn btn-primario">Crear evento</Link>
        </Vacio>
      ) : (
        <div className="tarjeta tabla-contenedor">
          <table className="tabla">
            <thead>
              <tr>
                <th>Evento</th>
                <th>Categoría</th>
                <th>Fecha</th>
                <th>Estado</th>
                <th className="numero">Desde</th>
                <th className="numero">Disponibles</th>
                <th><span className="sr-only">Acciones</span></th>
              </tr>
            </thead>
            <tbody>
              {eventos.map((evento) => (
                <tr key={evento.id}>
                  <td>
                    <div className="admin-eventos__evento">
                      <div className="admin-eventos__miniatura">
                        <Afiche evento={evento} />
                      </div>
                      <div>
                        <Link to={`/panel/eventos/${evento.id}`} className="admin-eventos__nombre">
                          {evento.nombre}
                        </Link>
                        <span className="admin-eventos__recinto">{evento.recinto?.nombre}</span>
                      </div>
                    </div>
                  </td>
                  <td>{categoria(evento.categoria).icono} {evento.categoria_display}</td>
                  <td className="admin-eventos__fecha">{formatoFechaCorta(evento.fecha)}</td>
                  <td><EstadoBadge estado={evento.estado} /></td>
                  <td className="numero">{evento.precio_desde ? formatoPrecio(evento.precio_desde) : "—"}</td>
                  <td className="numero">
                    {evento.precio_desde === null ? (
                      <span className="texto-suave">Sin sectores</span>
                    ) : evento.disponibles === 0 ? (
                      <span className="admin-eventos__agotado">Agotado</span>
                    ) : (
                      formatoNumero(evento.disponibles)
                    )}
                  </td>
                  <td>
                    <div className="admin-eventos__acciones">
                      <Link to={`/panel/eventos/${evento.id}`} className="btn btn-secundario btn-chico">
                        Editar
                      </Link>
                      <button type="button" className="btn btn-peligro btn-chico" onClick={() => setEliminar(evento)}>
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        abierto={Boolean(eliminar)}
        titulo="¿Eliminar este evento?"
        textoConfirmar="Eliminar"
        peligro
        procesando={procesando}
        onConfirmar={confirmarEliminar}
        onCancelar={() => setEliminar(null)}
      >
        <p>
          Se eliminará <strong>{eliminar?.nombre}</strong> junto con sus sectores.
        </p>
        <p>Si ya tiene entradas vendidas no se podrá eliminar: en ese caso cámbialo a estado Cancelado.</p>
      </Modal>
    </div>
  );
}
