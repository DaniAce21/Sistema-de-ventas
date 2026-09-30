/**
 * Funciones de formato para mostrar datos de la API.
 *
 * La API entrega precios como texto ("50000.00") y fechas en
 * ISO 8601 ("2026-10-15T21:00:00-03:00"). Aquí se convierten
 * al formato chileno usando la API Intl del navegador.
 */

// Pesos chilenos sin decimales: $50.000
const pesos = new Intl.NumberFormat("es-CL", {
  style: "currency",
  currency: "CLP",
  maximumFractionDigits: 0,
});

// Números con separador de miles: 1.250
const numero = new Intl.NumberFormat("es-CL");

// Ej.: "jueves 15 de octubre"
const fechaLarga = new Intl.DateTimeFormat("es-CL", {
  weekday: "long",
  day: "numeric",
  month: "long",
});

// Ej.: "15 oct 2026, 21:00"
const fechaCorta = new Intl.DateTimeFormat("es-CL", {
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

const hora = new Intl.DateTimeFormat("es-CL", { hour: "2-digit", minute: "2-digit" });
const mesCorto = new Intl.DateTimeFormat("es-CL", { month: "short" });

export const formatoPrecio = (valor) => pesos.format(Number(valor));
export const formatoNumero = (valor) => numero.format(Number(valor));
export const formatoFecha = (iso) => fechaLarga.format(new Date(iso));
export const formatoFechaCorta = (iso) => fechaCorta.format(new Date(iso));
export const formatoHora = (iso) => hora.format(new Date(iso));

/**
 * Partes de la fecha para el "calendario" de las tarjetas:
 * { dia: "15", mes: "OCT" }
 */
export function partesFecha(iso) {
  const fecha = new Date(iso);
  return {
    dia: String(fecha.getDate()).padStart(2, "0"),
    mes: mesCorto.format(fecha).replace(".", "").toUpperCase(),
  };
}

/**
 * Convierte un ISO a valor para <input type="datetime-local">
 * en la hora local del navegador: "2026-10-15T21:00".
 */
export function aInputFecha(iso) {
  if (!iso) return "";
  const fecha = new Date(iso);
  const local = new Date(fecha.getTime() - fecha.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}
