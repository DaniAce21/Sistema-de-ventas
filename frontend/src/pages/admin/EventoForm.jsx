/**
 * Crear o editar un evento, y gestionar su inventario (sectores).
 *
 * Endpoints (ORGANIZADOR propietario):
 *   GET   /api/eventos/recintos/          Recintos para elegir.
 *   POST  /api/eventos/recintos/          Crear un recinto nuevo.
 *   POST  /api/eventos/                   Crear evento (multipart con afiche).
 *   GET   /api/eventos/{id}/              Cargar evento a editar.
 *   PATCH /api/eventos/{id}/              Guardar cambios (multipart).
 *   GET   /api/eventos/{id}/sectores/     Sectores del evento.
 *   POST  /api/eventos/{id}/sectores/     Agregar sector.
 *   PATCH /api/eventos/sectores/{id}/     Ajustar precio y stock.
 *   DELETE /api/eventos/sectores/{id}/    Eliminar sector (si no tiene ventas).
 *
 * El afiche se envía con FormData: el navegador arma una petición
 * multipart/form-data y Django guarda el archivo en MEDIA_ROOT/eventos/.
 */

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../../api/client";
import Afiche from "../../components/comun/Afiche";
import Cargando from "../../components/comun/Cargando";
import Modal from "../../components/comun/Modal";
import { CATEGORIAS, ESTADOS_EVENTO } from "../../utils/categorias";
import { aInputFecha, formatoNumero } from "../../utils/formato";

import "./EventoForm.css";

const EVENTO_VACIO = {
  nombre: "",
  descripcion: "",
  categoria: "CONCIERTO",
  estado: "PROGRAMADO",
  fecha: "",
  recinto_id: "",
};

const TAMANO_MAXIMO = 5 * 1024 * 1024; // 5 MB, igual que el backend.

/* ============================================================
   SECCIÓN: SECTORES E INVENTARIO
   ============================================================ */

function Sectores({ eventoId }) {
  const [sectores, setSectores] = useState(null);
  const [cambios, setCambios] = useState({});
  const [nuevo, setNuevo] = useState({ nombre: "", precio: "", stock: "" });
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const [eliminar, setEliminar] = useState(null);
  const [procesando, setProcesando] = useState(false);

  useEffect(() => {
    api(`/eventos/${eventoId}/sectores/`)
      .then(setSectores)
      .catch((err) => setError(err.message));
  }, [eventoId]);

  // Ejecuta una operación mostrando el resultado.
  async function operar(accion, mensaje) {
    setError("");
    setAviso("");
    setProcesando(true);
    try {
      await accion();
      setAviso(mensaje);
    } catch (err) {
      setError(err.message);
    } finally {
      setProcesando(false);
    }
  }

  const editar = (id, campo, valor) =>
    setCambios({ ...cambios, [id]: { ...cambios[id], [campo]: valor } });

  // PATCH solo con los campos modificados de la fila.
  const guardar = (sector) =>
    operar(async () => {
      const actualizado = await api(`/eventos/sectores/${sector.id}/`, {
        method: "PATCH",
        body: cambios[sector.id],
      });
      setSectores(sectores.map((s) => (s.id === sector.id ? actualizado : s)));
      const { [sector.id]: _, ...resto } = cambios;
      setCambios(resto);
    }, `Sector "${sector.nombre}" actualizado.`);

  const agregar = (e) => {
    e.preventDefault();
    operar(async () => {
      const creado = await api(`/eventos/${eventoId}/sectores/`, {
        method: "POST",
        body: { nombre: nuevo.nombre, precio: nuevo.precio, stock: Number(nuevo.stock) },
      });
      setSectores([...sectores, creado]);
      setNuevo({ nombre: "", precio: "", stock: "" });
    }, `Sector "${nuevo.nombre}" agregado.`);
  };

  const confirmarEliminar = () =>
    operar(async () => {
      await api(`/eventos/sectores/${eliminar.id}/`, { method: "DELETE" });
      setSectores(sectores.filter((s) => s.id !== eliminar.id));
    }, `Sector "${eliminar.nombre}" eliminado.`).finally(() => setEliminar(null));

  if (!sectores) return <Cargando texto="Cargando sectores…" />;

  const stockTotal = sectores.reduce((suma, s) => suma + s.stock, 0);

  return (
    <section className="tarjeta evento-form__sectores">
      <div className="evento-form__seccion-cabecera">
        <div>
          <h2>Sectores e inventario</h2>
          <p className="texto-suave">
            El stock se descuenta solo cuando una compra pasa a PAGADO y se repone si se cancela.
          </p>
        </div>
        <span className="evento-form__stock-total">
          Stock total <strong>{formatoNumero(stockTotal)}</strong>
        </span>
      </div>

      {error && <div className="alerta alerta-error" role="alert">⚠ {error}</div>}
      {aviso && <div className="alerta alerta-exito">✓ {aviso}</div>}

      {sectores.length > 0 && (
        <div className="tabla-contenedor evento-form__tabla">
          <table className="tabla">
            <thead>
              <tr>
                <th>Sector</th>
                <th>Precio (CLP)</th>
                <th>Stock disponible</th>
                <th><span className="sr-only">Acciones</span></th>
              </tr>
            </thead>
            <tbody>
              {sectores.map((sector) => {
                const fila = { ...sector, ...cambios[sector.id] };
                const modificado = Boolean(cambios[sector.id]);

                return (
                  <tr key={sector.id}>
                    <td><strong>{sector.nombre}</strong></td>
                    <td>
                      <input
                        type="number"
                        min="0"
                        step="500"
                        className="input evento-form__celda"
                        value={Math.round(fila.precio)}
                        onChange={(e) => editar(sector.id, "precio", e.target.value)}
                        aria-label={`Precio de ${sector.nombre}`}
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        min="0"
                        className="input evento-form__celda"
                        value={fila.stock}
                        onChange={(e) => editar(sector.id, "stock", Number(e.target.value))}
                        aria-label={`Stock de ${sector.nombre}`}
                      />
                    </td>
                    <td>
                      <div className="evento-form__acciones-fila">
                        <button
                          type="button"
                          className="btn btn-primario btn-chico"
                          onClick={() => guardar(sector)}
                          disabled={!modificado || procesando}
                        >
                          Guardar
                        </button>
                        <button
                          type="button"
                          className="btn btn-peligro btn-chico"
                          onClick={() => setEliminar(sector)}
                          disabled={procesando}
                        >
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* ---------- Agregar sector ---------- */}
      <form className="evento-form__nuevo-sector" onSubmit={agregar}>
        <h3>Agregar sector</h3>
        <div className="evento-form__nuevo-campos">
          <div className="campo">
            <label htmlFor="sector-nombre">Nombre</label>
            <input
              id="sector-nombre"
              className="input"
              placeholder="VIP, Cancha, Platea…"
              value={nuevo.nombre}
              onChange={(e) => setNuevo({ ...nuevo, nombre: e.target.value })}
              required
            />
          </div>
          <div className="campo">
            <label htmlFor="sector-precio">Precio</label>
            <input
              id="sector-precio"
              type="number"
              min="0"
              step="500"
              className="input"
              placeholder="25000"
              value={nuevo.precio}
              onChange={(e) => setNuevo({ ...nuevo, precio: e.target.value })}
              required
            />
          </div>
          <div className="campo">
            <label htmlFor="sector-stock">Stock</label>
            <input
              id="sector-stock"
              type="number"
              min="0"
              className="input"
              placeholder="100"
              value={nuevo.stock}
              onChange={(e) => setNuevo({ ...nuevo, stock: e.target.value })}
              required
            />
          </div>
          <button className="btn btn-oscuro" disabled={procesando || !nuevo.nombre || nuevo.precio === "" || nuevo.stock === ""}>
            + Agregar
          </button>
        </div>
      </form>

      <Modal
        abierto={Boolean(eliminar)}
        titulo="¿Eliminar sector?"
        textoConfirmar="Eliminar"
        peligro
        procesando={procesando}
        onConfirmar={confirmarEliminar}
        onCancelar={() => setEliminar(null)}
      >
        <p>
          Se eliminará <strong>{eliminar?.nombre}</strong>. Si ya tiene entradas vendidas, el sistema lo impedirá.
        </p>
      </Modal>
    </section>
  );
}

/* ============================================================
   FORMULARIO PRINCIPAL DEL EVENTO
   ============================================================ */

export default function EventoForm() {
  const { id } = useParams();
  const editando = Boolean(id);
  const navigate = useNavigate();

  const [datos, setDatos] = useState(EVENTO_VACIO);
  const [imagenActual, setImagenActual] = useState(null);
  const [archivo, setArchivo] = useState(null);
  const [vistaPrevia, setVistaPrevia] = useState(null);
  const [recintos, setRecintos] = useState([]);
  const [nuevoRecinto, setNuevoRecinto] = useState(null);
  const [errores, setErrores] = useState({});
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const [cargando, setCargando] = useState(editando);
  const [guardando, setGuardando] = useState(false);

  // Carga recintos y, si se edita, el evento.
  useEffect(() => {
    api("/eventos/recintos/").then(setRecintos).catch(() => setRecintos([]));

    if (!editando) {
      setDatos(EVENTO_VACIO);
      setImagenActual(null);
      return;
    }

    setCargando(true);
    api(`/eventos/${id}/`)
      .then((ev) => {
        setDatos({
          nombre: ev.nombre,
          descripcion: ev.descripcion,
          categoria: ev.categoria,
          estado: ev.estado,
          fecha: aInputFecha(ev.fecha),
          recinto_id: ev.recinto?.id ?? "",
        });
        setImagenActual(ev.imagen);
      })
      .catch((err) => setError(err.status === 404 ? "Este evento no existe o no te pertenece." : err.message))
      .finally(() => setCargando(false));
  }, [id, editando]);

  // Libera la URL temporal de la vista previa al cambiar de archivo.
  useEffect(() => () => vistaPrevia && URL.revokeObjectURL(vistaPrevia), [vistaPrevia]);

  const cambiar = (e) => {
    setDatos({ ...datos, [e.target.name]: e.target.value });
    setErrores({ ...errores, [e.target.name]: undefined });
  };

  function elegirImagen(e) {
    const elegido = e.target.files[0];
    if (!elegido) return;

    if (elegido.size > TAMANO_MAXIMO) {
      setErrores({ ...errores, imagen: ["La imagen no puede superar los 5 MB."] });
      return;
    }

    setErrores({ ...errores, imagen: undefined });
    setArchivo(elegido);
    setVistaPrevia(URL.createObjectURL(elegido));
  }

  async function crearRecinto() {
    try {
      const creado = await api("/eventos/recintos/", { method: "POST", body: nuevoRecinto });
      setRecintos([...recintos, creado].sort((a, b) => a.nombre.localeCompare(b.nombre)));
      setDatos({ ...datos, recinto_id: creado.id });
      setNuevoRecinto(null);
    } catch (err) {
      setError(err.message);
    }
  }

  async function guardar(e) {
    e.preventDefault();
    setError("");
    setAviso("");
    setGuardando(true);

    // FormData permite enviar el archivo junto con los demás campos.
    const formulario = new FormData();
    formulario.append("nombre", datos.nombre);
    formulario.append("descripcion", datos.descripcion);
    formulario.append("categoria", datos.categoria);
    formulario.append("estado", datos.estado);
    formulario.append("recinto_id", datos.recinto_id);
    // datetime-local no trae zona horaria: se convierte a ISO (UTC).
    if (datos.fecha) formulario.append("fecha", new Date(datos.fecha).toISOString());
    if (archivo) formulario.append("imagen", archivo);

    try {
      const evento = await api(editando ? `/eventos/${id}/` : "/eventos/", {
        method: editando ? "PATCH" : "POST",
        body: formulario,
      });

      if (editando) {
        setImagenActual(evento.imagen);
        setArchivo(null);
        setVistaPrevia(null);
        setAviso("Cambios guardados.");
      } else {
        // Los sectores necesitan el ID del evento: se continúa en modo edición.
        navigate(`/panel/eventos/${evento.id}`, { replace: true });
      }
    } catch (err) {
      setError(err.message);
      setErrores(err.campos ?? {});
    } finally {
      setGuardando(false);
    }
  }

  if (cargando) return <Cargando texto="Cargando evento…" />;

  // Evento de ejemplo para la vista previa de la tarjeta.
  const previa = { ...datos, imagen: vistaPrevia ?? imagenActual };

  const errorDe = (campo) =>
    errores[campo] && <span className="error-campo">{errores[campo].join(" ")}</span>;

  return (
    <div className="evento-form">
      <Link to="/panel/eventos" className="evento-form__volver">← Volver a eventos</Link>

      {error && <div className="alerta alerta-error" role="alert">⚠ {error}</div>}
      {aviso && <div className="alerta alerta-exito">✓ {aviso}</div>}
      {editando && !aviso && !error && (
        <div className="alerta alerta-info">💡 Agrega o ajusta los sectores más abajo para definir precios y stock.</div>
      )}

      <form className="evento-form__grid" onSubmit={guardar} noValidate>
        {/* ---------- Datos del evento ---------- */}
        <section className="tarjeta">
          <h2>Información del evento</h2>

          <div className="campo">
            <label htmlFor="nombre">Nombre</label>
            <input id="nombre" name="nombre" className="input" value={datos.nombre} onChange={cambiar} required aria-invalid={Boolean(errores.nombre)} />
            {errorDe("nombre")}
          </div>

          <div className="campo">
            <label htmlFor="descripcion">Descripción</label>
            <textarea id="descripcion" name="descripcion" className="input" value={datos.descripcion} onChange={cambiar} rows={5} />
          </div>

          <div className="fila-campos">
            <div className="campo">
              <label htmlFor="categoria">Categoría</label>
              <select id="categoria" name="categoria" className="input" value={datos.categoria} onChange={cambiar}>
                {CATEGORIAS.map((c) => (
                  <option key={c.valor} value={c.valor}>{c.icono} {c.etiqueta}</option>
                ))}
              </select>
            </div>
            <div className="campo">
              <label htmlFor="estado">Estado</label>
              <select id="estado" name="estado" className="input" value={datos.estado} onChange={cambiar}>
                {ESTADOS_EVENTO.map((e) => (
                  <option key={e.valor} value={e.valor}>{e.etiqueta}</option>
                ))}
              </select>
              <span className="ayuda">Solo los eventos Programados aparecen en el catálogo.</span>
            </div>
          </div>

          <div className="fila-campos">
            <div className="campo">
              <label htmlFor="fecha">Fecha y hora</label>
              <input id="fecha" name="fecha" type="datetime-local" className="input" value={datos.fecha} onChange={cambiar} required aria-invalid={Boolean(errores.fecha)} />
              {errorDe("fecha")}
            </div>

            <div className="campo">
              <label htmlFor="recinto_id">Recinto</label>
              <select id="recinto_id" name="recinto_id" className="input" value={datos.recinto_id} onChange={cambiar} required aria-invalid={Boolean(errores.recinto_id)}>
                <option value="">Selecciona un recinto</option>
                {recintos.map((r) => (
                  <option key={r.id} value={r.id}>{r.nombre}</option>
                ))}
              </select>
              {errorDe("recinto_id")}
              {!nuevoRecinto && (
                <button type="button" className="evento-form__enlace" onClick={() => setNuevoRecinto({ nombre: "", direccion: "" })}>
                  + Crear recinto nuevo
                </button>
              )}
            </div>
          </div>

          {/* Mini formulario para crear un recinto sin salir de la página. */}
          {nuevoRecinto && (
            <div className="evento-form__recinto">
              <div className="fila-campos">
                <div className="campo">
                  <label htmlFor="recinto-nombre">Nombre del recinto</label>
                  <input id="recinto-nombre" className="input" value={nuevoRecinto.nombre} onChange={(e) => setNuevoRecinto({ ...nuevoRecinto, nombre: e.target.value })} />
                </div>
                <div className="campo">
                  <label htmlFor="recinto-direccion">Dirección</label>
                  <input id="recinto-direccion" className="input" value={nuevoRecinto.direccion} onChange={(e) => setNuevoRecinto({ ...nuevoRecinto, direccion: e.target.value })} />
                </div>
              </div>
              <div className="evento-form__recinto-acciones">
                <button type="button" className="btn btn-secundario btn-chico" onClick={() => setNuevoRecinto(null)}>Cancelar</button>
                <button type="button" className="btn btn-oscuro btn-chico" onClick={crearRecinto} disabled={!nuevoRecinto.nombre || !nuevoRecinto.direccion}>
                  Guardar recinto
                </button>
              </div>
            </div>
          )}
        </section>

        {/* ---------- Afiche y vista previa ---------- */}
        <aside className="evento-form__lateral">
          <section className="tarjeta">
            <h2>Afiche</h2>
            <div className="evento-form__previa">
              <Afiche evento={previa} />
            </div>
            <label className="btn btn-secundario btn-bloque evento-form__archivo">
              {previa.imagen ? "Cambiar imagen" : "Subir imagen"}
              <input type="file" accept="image/*" onChange={elegirImagen} className="sr-only" />
            </label>
            <p className="ayuda evento-form__ayuda">JPG o PNG, máximo 5 MB. Formato horizontal recomendado (4:3).</p>
            {errorDe("imagen")}
          </section>

          <button className="btn btn-primario btn-grande btn-bloque" disabled={guardando}>
            {guardando ? "Guardando…" : editando ? "Guardar cambios" : "Crear evento"}
          </button>
        </aside>
      </form>

      {editando && !error && <Sectores eventoId={id} />}
    </div>
  );
}
