/**
 * Estado global de autenticación.
 *
 * Expone:
 *   usuario        { username, rol } leídos del claim del JWT, o null.
 *   esAdmin        true si el rol es ORGANIZADOR (vista de administración).
 *   esEspectador   true si el rol es ESPECTADOR (vista de compra).
 *   login()        POST /api/auth/token/
 *   registrar()    POST /api/auth/registro/ + login automático.
 *   logout()       Borra los tokens (el carrito sigue en PostgreSQL).
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { api, decodificarToken, guardarTokens, leerTokens } from "../api/client";

const AuthContext = createContext(null);

// Nombres de rol que muestra la interfaz.
export const NOMBRE_ROL = {
  ESPECTADOR: "Espectador",
  ORGANIZADOR: "Administrador",
};

function usuarioDesdeTokens(tokens) {
  if (!tokens?.access) return null;
  try {
    const { username, rol } = decodificarToken(tokens.access);
    return { username, rol };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(() => usuarioDesdeTokens(leerTokens()));

  // Inicia sesión y devuelve el usuario (con su rol) para decidir a dónde ir.
  const login = useCallback(async (username, password) => {
    const tokens = await api("/auth/token/", {
      method: "POST",
      body: { username, password },
      reintento: false,
    });

    guardarTokens(tokens);
    const nuevo = usuarioDesdeTokens(tokens);
    setUsuario(nuevo);
    return nuevo;
  }, []);

  // Crea la cuenta (siempre ESPECTADOR en el backend) y entra directo.
  const registrar = useCallback(
    async (datos) => {
      await api("/auth/registro/", { method: "POST", body: datos, reintento: false });
      return login(datos.username, datos.password);
    },
    [login]
  );

  const logout = useCallback(() => {
    guardarTokens(null);
    setUsuario(null);
  }, []);

  // Si el refresh token también expiró, cerramos la sesión.
  useEffect(() => {
    window.addEventListener("sesion-expirada", logout);
    return () => window.removeEventListener("sesion-expirada", logout);
  }, [logout]);

  const valor = useMemo(
    () => ({
      usuario,
      esAdmin: usuario?.rol === "ORGANIZADOR",
      esEspectador: usuario?.rol === "ESPECTADOR",
      login,
      registrar,
      logout,
    }),
    [usuario, login, registrar, logout]
  );

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
