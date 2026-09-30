/**
 * Estado global del carrito del espectador.
 *
 * El carrito vive en PostgreSQL (GET /api/carro-tickets/).
 * Este contexto solo mantiene una copia en memoria para mostrar
 * el contador de la cabecera y evitar recargas innecesarias.
 *
 * Al iniciar sesión se vuelve a leer desde el backend: por eso
 * los items agregados antes del logout reaparecen intactos.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import { useAuth } from "./AuthContext";

const CarritoContext = createContext(null);

export function CarritoProvider({ children }) {
  const { esEspectador } = useAuth();
  const [carrito, setCarrito] = useState(null);

  // Vuelve a leer el carrito desde PostgreSQL.
  const refrescar = useCallback(async () => {
    if (!esEspectador) {
      setCarrito(null);
      return null;
    }
    const data = await api("/carro-tickets/");
    setCarrito(data);
    return data;
  }, [esEspectador]);

  // Cada operación del backend devuelve el carrito actualizado.
  const agregar = useCallback(async (sectorId, cantidad) => {
    const data = await api("/carro-tickets/", {
      method: "POST",
      body: { sector_id: sectorId, cantidad },
    });
    setCarrito(data);
    return data;
  }, []);

  const quitar = useCallback(async (sectorId) => {
    const data = await api("/carro-tickets/", { method: "DELETE", body: { sector_id: sectorId } });
    setCarrito(data);
    return data;
  }, []);

  const vaciar = useCallback(async () => {
    const data = await api("/carro-tickets/", { method: "DELETE", body: {} });
    setCarrito(data);
    return data;
  }, []);

  // Tras pagar, el backend vacía el carrito dentro de la transacción.
  const marcarPagado = useCallback(() => {
    setCarrito((actual) => (actual ? { ...actual, items: [] } : actual));
  }, []);

  // Al cambiar de sesión (login/logout) se recarga o se limpia.
  useEffect(() => {
    refrescar().catch(() => setCarrito(null));
  }, [refrescar]);

  const cantidadTotal = carrito?.items.reduce((suma, item) => suma + item.cantidad, 0) ?? 0;

  const valor = useMemo(
    () => ({ carrito, cantidadTotal, refrescar, agregar, quitar, vaciar, marcarPagado }),
    [carrito, cantidadTotal, refrescar, agregar, quitar, vaciar, marcarPagado]
  );

  return <CarritoContext.Provider value={valor}>{children}</CarritoContext.Provider>;
}

export function useCarrito() {
  return useContext(CarritoContext);
}
