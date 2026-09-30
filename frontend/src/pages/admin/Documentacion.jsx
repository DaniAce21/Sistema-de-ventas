/**
 * Documentación de la API (Swagger / OpenAPI) — EXCLUSIVA del administrador.
 *
 * Flujo:
 *   1. Se descarga el esquema con el JWT del administrador:
 *        GET /api/schema/?format=json
 *      El backend lo protege con el permiso IsGestor: un espectador
 *      recibe 403 aunque conozca la URL.
 *   2. Se dibuja con Swagger UI (paquete swagger-ui-dist).
 *   3. requestInterceptor agrega el token a cada "Try it out",
 *      así se prueban los endpoints protegidos sin copiar el token.
 *
 * Esta página se carga de forma diferida (React.lazy en App.jsx)
 * porque Swagger UI pesa bastante y solo lo usa el administrador.
 */

import { useEffect, useRef, useState } from "react";
import SwaggerUI from "swagger-ui-dist/swagger-ui-es-bundle.js";
import "swagger-ui-dist/swagger-ui.css";

import { api, leerTokens } from "../../api/client";
import Cargando from "../../components/comun/Cargando";

import "./Documentacion.css";

export default function Documentacion() {
  const contenedor = useRef(null);
  const [esquema, setEsquema] = useState(null);
  const [error, setError] = useState("");

  // 1. Descarga del esquema OpenAPI con el JWT.
  useEffect(() => {
    api("/schema/?format=json")
      .then(setEsquema)
      .catch((err) => setError(err.message));
  }, []);

  // 2. Render de Swagger UI una vez que llega el esquema.
  useEffect(() => {
    if (!esquema || !contenedor.current) return;

    SwaggerUI({
      domNode: contenedor.current,
      spec: esquema,
      deepLinking: true,
      docExpansion: "list",
      defaultModelsExpandDepth: 0,
      tryItOutEnabled: false,
      // 3. Cada petición de prueba viaja con el token actual.
      requestInterceptor: (peticion) => {
        const tokens = leerTokens();
        if (tokens?.access && !peticion.headers.Authorization) {
          peticion.headers.Authorization = `Bearer ${tokens.access}`;
        }
        return peticion;
      },
    });
  }, [esquema]);

  if (error) {
    return <div className="alerta alerta-error">⚠ No se pudo cargar la documentación: {error}</div>;
  }

  return (
    <div className="documentacion">
      <section className="documentacion__intro">
        <div>
          <span className="documentacion__etiqueta">OpenAPI 3 · drf-spectacular</span>
          <h2>Referencia de la API</h2>
          <p>
            Esquema generado automáticamente desde los serializers y vistas de Django REST Framework.
            Las pruebas usan tu sesión de administrador: el token JWT se agrega solo a cada petición.
          </p>
        </div>
        <div className="documentacion__acciones">
          <a className="btn btn-claro" href="http://127.0.0.1:8000/api/docs/" target="_blank" rel="noreferrer">
            Abrir en Django ↗
          </a>
        </div>
      </section>

      {!esquema && <Cargando texto="Generando esquema OpenAPI…" />}

      <div className="tarjeta documentacion__swagger" ref={contenedor} />
    </div>
  );
}
