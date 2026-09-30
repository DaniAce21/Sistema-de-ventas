/**
 * Dashboard del administrador.
 *
 * Endpoints (ORGANIZADOR):
 *   GET /api/compras/resumen/                 Métricas agregadas en PostgreSQL
 *                                             (Sum, Count) de SUS eventos.
 *   GET /api/compras/?ordering=-creado_en     Últimas compras.
 *
 * Presentación:
 *   - Tarjetas con cifras clave (recaudación, entradas, eventos, compras).
 *   - Tabla de ventas por evento con barra de ocupación
 *     (vendidas / capacidad), siempre con el número visible.
 *   - Compras por estado, con etiqueta e ícono (no solo color).
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../../api/client";
import Cargando from "../../components/comun/Cargando";
import EstadoBadge from "../../components/comun/EstadoBadge";
import Vacio from "../../components/comun/Vacio";
import { useAuth } from "../../context/AuthContext";
import { ESTADOS_COMPRA } from "../../utils/categorias";
import { formatoFechaCorta, formatoNumero, formatoPrecio } from "../../utils/formato";

import "./Dashboard.css";

function Metrica({ titulo, valor, detalle, destacada = false }) {
  return (
    <div className={`tarjeta metrica ${destacada ? "metrica--destacada" : ""}`}>
      <span className="metrica__titulo">{titulo}</span>
      <strong className="metrica__valor">{valor}</strong>
      {detalle && <span className="metrica__detalle">{detalle}</span>}
    </div>
  );
}

export default function Dashboard() {
  const { usuario } = useAuth();
  const [resumen, setResumen] = useState(null);
  const [ultimas, setUltimas] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api("/compras/resumen/"), api("/compras/?ordering=-creado_en")])
      .then(([res, compras]) => {
        setResumen(res);
        setUltimas(compras.slice(0, 5));
      })
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <div className="alerta alerta-error">⚠ {error}</div>;
  if (!resumen) return <Cargando texto="Calculando métricas…" />;

  const porEstado = resumen.compras_por_estado;
  const comprasVendidas = porEstado.PAGADO + porEstado.ENTREGADO;
  const totalCompras = Object.values(porEstado).reduce((a, b) => a + b, 0);

  return (
    <div className="dashboard">
      <div className="dashboard__saludo">
        <div>
          <h2>Hola, {usuario.username} 👋</h2>
          <p className="texto-suave">Así van las ventas de tus eventos.</p>
        </div>
        <Link to="/panel/eventos/nuevo" className="btn btn-primario">+ Nuevo evento</Link>
      </div>

      {/* ---------- Cifras clave ---------- */}
      <div className="metricas">
        <Metrica
          destacada
          titulo="Recaudación"
          valor={formatoPrecio(resumen.recaudado)}
          detalle="Compras pagadas y entregadas"
        />
        <Metrica titulo="Entradas vendidas" valor={formatoNumero(resumen.entradas_vendidas)} />
        <Metrica titulo="Eventos programados" valor={resumen.eventos_programados} detalle={`de ${resumen.eventos.length} en total`} />
        <Metrica titulo="Compras concretadas" valor={comprasVendidas} detalle={`${porEstado.CANCELADO} canceladas`} />
      </div>

      <div className="dashboard__grid">
        {/* ---------- Ventas por evento ---------- */}
        <section className="tarjeta tabla-contenedor dashboard__eventos">
          <div className="dashboard__seccion-cabecera">
            <h3>Ventas por evento</h3>
            <Link to="/panel/eventos">Gestionar →</Link>
          </div>

          {resumen.eventos.length === 0 ? (
            <div className="dashboard__vacio">
              <Vacio icono="🎤" titulo="Aún no tienes eventos" texto="Crea tu primer evento para empezar a vender.">
                <Link to="/panel/eventos/nuevo" className="btn btn-primario">Crear evento</Link>
              </Vacio>
            </div>
          ) : (
            <table className="tabla">
              <thead>
                <tr>
                  <th>Evento</th>
                  <th>Estado</th>
                  <th>Ocupación</th>
                  <th className="numero">Recaudado</th>
                </tr>
              </thead>
              <tbody>
                {resumen.eventos.map((evento) => {
                  const capacidad = evento.vendidas + evento.disponibles;
                  const porcentaje = capacidad ? Math.round((evento.vendidas / capacidad) * 100) : 0;

                  return (
                    <tr key={evento.id}>
                      <td>
                        <Link to={`/panel/eventos/${evento.id}`} className="dashboard__evento">
                          {evento.nombre}
                        </Link>
                        <span className="dashboard__fecha">{formatoFechaCorta(evento.fecha)}</span>
                      </td>
                      <td><EstadoBadge estado={evento.estado} /></td>
                      <td>
                        <div
                          className="ocupacion"
                          title={`${evento.vendidas} vendidas de ${capacidad} (${porcentaje}%)`}
                        >
                          <div className="ocupacion__barra" aria-hidden="true">
                            <span style={{ width: `${porcentaje}%` }} />
                          </div>
                          <span className="ocupacion__texto">
                            {formatoNumero(evento.vendidas)}/{formatoNumero(capacidad)}
                          </span>
                        </div>
                      </td>
                      <td className="numero">{formatoPrecio(evento.recaudado)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </section>

        <div className="dashboard__lateral">
          {/* ---------- Compras por estado ---------- */}
          <section className="tarjeta">
            <h3>Compras por estado</h3>
            <ul className="estados">
              {Object.keys(ESTADOS_COMPRA).map((estado) => (
                <li key={estado}>
                  <EstadoBadge estado={estado} />
                  <div className="estados__barra" aria-hidden="true">
                    <span style={{ width: `${totalCompras ? (porEstado[estado] / totalCompras) * 100 : 0}%` }} />
                  </div>
                  <strong>{porEstado[estado]}</strong>
                </li>
              ))}
            </ul>
          </section>

          {/* ---------- Últimas compras ---------- */}
          <section className="tarjeta">
            <div className="dashboard__seccion-cabecera">
              <h3>Últimas compras</h3>
              <Link to="/panel/compras">Ver todas →</Link>
            </div>
            {ultimas.length === 0 ? (
              <p className="texto-suave">Todavía no hay compras.</p>
            ) : (
              <ul className="ultimas">
                {ultimas.map((compra) => (
                  <li key={compra.id}>
                    <div>
                      <strong>#{compra.id} · {compra.usuario}</strong>
                      <span>{formatoFechaCorta(compra.creado_en)}</span>
                    </div>
                    <div className="ultimas__lado">
                      <strong>{formatoPrecio(compra.total)}</strong>
                      <EstadoBadge estado={compra.estado} />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
