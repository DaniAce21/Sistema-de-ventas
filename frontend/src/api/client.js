/**
 * Cliente HTTP para la API de Django.
 *
 * - Agrega automáticamente el header Authorization: Bearer <access>.
 * - Si el access token expiró (401), usa el refresh token para
 *   obtener uno nuevo y reintenta la petición una vez.
 * - Envía JSON o FormData (FormData se usa para subir el afiche).
 * - Lanza errores con el mensaje del backend, que siempre responde
 *   {"error": "...", "codigo": 400, "campos": {...}}
 *   (ver venta_entradas/exceptions.py).
 */

const TOKENS_KEY = "tokens";

/* ------------------------------------------------------------
   TOKENS EN localStorage
   Solo se guardan los tokens JWT. El carrito NO se guarda aquí:
   vive en PostgreSQL para sobrevivir al logout.
   ------------------------------------------------------------ */

export function leerTokens() {
  try {
    return JSON.parse(localStorage.getItem(TOKENS_KEY));
  } catch {
    return null;
  }
}

export function guardarTokens(tokens) {
  try {
    if (tokens) {
      localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens));
    } else {
      localStorage.removeItem(TOKENS_KEY);
    }
  } catch {
    // Almacenamiento bloqueado (modo privado): la sesión dura hasta recargar.
  }
}

/**
 * Decodifica el payload del JWT (sin verificar la firma;
 * la verificación real la hace el backend en cada petición).
 */
export function decodificarToken(access) {
  const base64 = access.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
  const json = decodeURIComponent(
    atob(base64)
      .split("")
      .map((c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"))
      .join("")
  );
  return JSON.parse(json);
}

/* ------------------------------------------------------------
   ERRORES
   ------------------------------------------------------------ */

/**
 * Error de la API con el código HTTP y los errores por campo,
 * para que los formularios puedan marcar cada input.
 */
export class ApiError extends Error {
  constructor(mensaje, status, campos = {}) {
    super(mensaje);
    this.status = status;
    this.campos = campos;
  }
}

function crearError(data, status) {
  if (status === 0) {
    return new ApiError("No se pudo conectar con el servidor. ¿Está corriendo el backend?", 0);
  }

  const mensaje = data?.error ?? data?.detail ?? `Error ${status}`;
  return new ApiError(mensaje, status, data?.campos ?? {});
}

/* ------------------------------------------------------------
   RENOVACIÓN DEL ACCESS TOKEN
   ------------------------------------------------------------ */

async function refrescarAccess() {
  const tokens = leerTokens();
  if (!tokens?.refresh) return false;

  const res = await fetch("/api/auth/token/refresh/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: tokens.refresh }),
  });

  if (!res.ok) {
    guardarTokens(null);
    return false;
  }

  // Con ROTATE_REFRESH_TOKENS el backend también devuelve un refresh nuevo.
  const nuevos = await res.json();
  guardarTokens({ ...tokens, ...nuevos });
  return true;
}

/* ------------------------------------------------------------
   PETICIÓN PRINCIPAL
   ------------------------------------------------------------ */

export async function api(ruta, { method = "GET", body, reintento = true } = {}) {
  const tokens = leerTokens();
  const esFormData = body instanceof FormData;

  const headers = { Accept: "application/json" };
  // Con FormData el navegador define el Content-Type (multipart + boundary).
  if (body !== undefined && !esFormData) headers["Content-Type"] = "application/json";
  if (tokens?.access) headers.Authorization = `Bearer ${tokens.access}`;

  let res;
  try {
    res = await fetch(`/api${ruta}`, {
      method,
      headers,
      body: body === undefined ? undefined : esFormData ? body : JSON.stringify(body),
    });
  } catch {
    throw crearError(null, 0);
  }

  // Access vencido: se renueva una vez y se reintenta.
  if (res.status === 401 && reintento && tokens?.refresh) {
    const renovado = await refrescarAccess();

    if (!renovado) {
      // La sesión expiró por completo: avisamos a la app.
      window.dispatchEvent(new Event("sesion-expirada"));
    }

    // Con el token nuevo, o sin token (los endpoints públicos siguen funcionando).
    return api(ruta, { method, body, reintento: false });
  }

  const data = res.status === 204 ? null : await res.json().catch(() => null);

  if (!res.ok) throw crearError(data, res.status);

  return data;
}

/**
 * Construye un query string omitiendo valores vacíos:
 * query({ search: "rock", estado: "" }) -> "?search=rock"
 */
export function query(params) {
  const qs = new URLSearchParams();

  Object.entries(params).forEach(([clave, valor]) => {
    if (valor === "" || valor === null || valor === undefined || valor === false) return;
    qs.set(clave, valor === true ? "true" : valor);
  });

  const texto = qs.toString();
  return texto ? `?${texto}` : "";
}
