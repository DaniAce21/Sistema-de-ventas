/**
 * Catálogo de eventos programados (portada del espectador).
 *
 * Endpoint: GET /api/eventos/
 * El backend solo devuelve eventos PROGRAMADOS a visitantes y espectadores.
 *
 * Todos los filtros viven en la URL (?categoria=TEATRO&search=rock...),
 * así la búsqueda se puede compartir y el botón "atrás" funciona.
 * Cada parámetro corresponde a un filtro de django-filter (eventos/filters.py):
 *
 *   search        SearchFilter (nombre, descripción, recinto)
 *   categoria     ChoiceFilter sobre Evento.Categoria
 *   fecha_desde   DateFilter (fecha__date__gte)
 *   fecha_hasta   DateFilter (fecha__date__lte)
 *   precio_max    NumberFilter sobre los sectores
 *   con_stock     BooleanFilter
 *   ordering      OrderingFilter (fecha, nombre)
 */

import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { api, query } from "../../api/client";
import { EsqueletoTarjetas } from "../../components/comun/Cargando";
import Vacio from "../../components/comun/Vacio";
import EventoCard from "../../components/espectador/EventoCard";
import Hero from "../../components/espectador/Hero";
import { CATEGORIAS, categoria as buscarCategoria } from "../../utils/categorias";

import "./Inicio.css";

// Parámetros de filtro que se leen desde la URL.
const FILTROS = ["search", "categoria", "fecha_desde", "fecha_hasta", "precio_max", "con_stock", "ordering"];

export default function Inicio() {
  const [params, setParams] = useSearchParams();
  const [destacados, setDestacados] = useState([]);
  const [eventos, setEventos] = useState(null);
  const [error, setError] = useState("");
  const [mostrarFiltros, setMostrarFiltros] = useState(false);

  // Filtros actuales tomados de la URL.
  const filtros = Object.fromEntries(FILTROS.map((f) => [f, params.get(f) ?? ""]));
  const hayFiltros = FILTROS.some((f) => f !== "ordering" && filtros[f]);

  // Destacados del carrusel: los 5 próximos eventos (sin filtros).
  useEffect(() => {
    api("/eventos/?ordering=fecha")
      .then((data) => setDestacados(data.slice(0, 5)))
      .catch(() => setDestacados([]));
  }, []);

  // Listado filtrado: se vuelve a pedir cuando cambia la URL.
  // La espera de 250 ms evita una petición por cada tecla.
  const clave = params.toString();
  useEffect(() => {
    setEventos(null);
    setError("");

    const espera = setTimeout(() => {
      api(`/eventos/${query({ ordering: "fecha", ...Object.fromEntries(new URLSearchParams(clave)) })}`)
        .then(setEventos)
        .catch((err) => {
          setError(err.message);
          setEventos([]);
        });
    }, 250);

    return () => clearTimeout(espera);
  }, [clave]);

  // Cambia un filtro en la URL (valor vacío = quitarlo).
  function cambiarFiltro(nombre, valor) {
    const nuevos = new URLSearchParams(params);
    if (valor === "" || valor === false) nuevos.delete(nombre);
    else nuevos.set(nombre, valor === true ? "true" : valor);
    setParams(nuevos, { replace: true });
  }

  const limpiar = () => setParams({}, { replace: true });

  const categoriaActual = filtros.categoria ? buscarCategoria(filtros.categoria) : null;

  return (
    <>
      {!hayFiltros && <Hero eventos={destacados} />}

      <div className="contenedor catalogo">
        {/* ---------- Chips de categorías ---------- */}
        <nav className="categorias" aria-label="Categorías">
          <button
            type="button"
            className={`categoria-chip ${!filtros.categoria ? "activa" : ""}`}
            onClick={() => cambiarFiltro("categoria", "")}
          >
            <span aria-hidden="true">🎟</span> Todos
          </button>
          {CATEGORIAS.map((c) => (
            <button
              key={c.valor}
              type="button"
              className={`categoria-chip ${filtros.categoria === c.valor ? "activa" : ""}`}
              onClick={() => cambiarFiltro("categoria", c.valor)}
              aria-pressed={filtros.categoria === c.valor}
            >
              <span aria-hidden="true">{c.icono}</span> {c.etiqueta}
            </button>
          ))}
        </nav>

        {/* ---------- Encabezado del listado ---------- */}
        <div className="catalogo__cabecera">
          <div>
            <h2 className="catalogo__titulo">
              {filtros.search
                ? `Resultados para "${filtros.search}"`
                : categoriaActual
                  ? categoriaActual.etiqueta
                  : "Próximos eventos"}
            </h2>
            {eventos && (
              <p className="texto-suave catalogo__conteo">
                {eventos.length} {eventos.length === 1 ? "evento disponible" : "eventos disponibles"}
              </p>
            )}
          </div>

          <div className="catalogo__herramientas">
            <label className="sr-only" htmlFor="orden">Ordenar</label>
            <select
              id="orden"
              className="input catalogo__orden"
              value={filtros.ordering || "fecha"}
              onChange={(e) => cambiarFiltro("ordering", e.target.value === "fecha" ? "" : e.target.value)}
            >
              <option value="fecha">Más próximos</option>
              <option value="-fecha">Más lejanos</option>
              <option value="nombre">Nombre A–Z</option>
            </select>
            <button
              type="button"
              className={`btn btn-secundario ${mostrarFiltros ? "activo" : ""}`}
              onClick={() => setMostrarFiltros(!mostrarFiltros)}
              aria-expanded={mostrarFiltros}
            >
              ⚙ Filtros
            </button>
          </div>
        </div>

        {/* ---------- Panel de filtros ---------- */}
        {mostrarFiltros && (
          <div className="tarjeta filtros">
            <div className="campo">
              <label htmlFor="fecha_desde">Desde</label>
              <input
                id="fecha_desde"
                type="date"
                className="input"
                value={filtros.fecha_desde}
                onChange={(e) => cambiarFiltro("fecha_desde", e.target.value)}
              />
            </div>
            <div className="campo">
              <label htmlFor="fecha_hasta">Hasta</label>
              <input
                id="fecha_hasta"
                type="date"
                className="input"
                value={filtros.fecha_hasta}
                onChange={(e) => cambiarFiltro("fecha_hasta", e.target.value)}
              />
            </div>
            <div className="campo">
              <label htmlFor="precio_max">Precio máximo</label>
              <input
                id="precio_max"
                type="number"
                min="0"
                step="1000"
                placeholder="$ sin límite"
                className="input"
                value={filtros.precio_max}
                onChange={(e) => cambiarFiltro("precio_max", e.target.value)}
              />
            </div>
            <label className="filtros__check">
              <input
                type="checkbox"
                checked={filtros.con_stock === "true"}
                onChange={(e) => cambiarFiltro("con_stock", e.target.checked)}
              />
              Solo con entradas disponibles
            </label>
            <button type="button" className="btn btn-secundario btn-chico" onClick={limpiar} disabled={!hayFiltros}>
              Limpiar filtros
            </button>
          </div>
        )}

        {/* ---------- Resultados ---------- */}
        {error && <div className="alerta alerta-error">⚠ {error}</div>}

        {eventos === null ? (
          <EsqueletoTarjetas />
        ) : eventos.length === 0 ? (
          <Vacio
            icono="🔍"
            titulo="No encontramos eventos"
            texto="Prueba con otra búsqueda, otra categoría o quita algunos filtros."
          >
            {hayFiltros && (
              <button type="button" className="btn btn-primario" onClick={limpiar}>
                Ver todos los eventos
              </button>
            )}
          </Vacio>
        ) : (
          <div className="catalogo__grid">
            {eventos.map((evento) => (
              <EventoCard key={evento.id} evento={evento} />
            ))}
          </div>
        )}
      </div>
    </>
  );
}
