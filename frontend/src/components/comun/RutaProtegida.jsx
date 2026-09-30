/**
 * Protege rutas según el rol del usuario.
 *
 * - Sin sesión:    redirige a /login y luego vuelve a la ruta original.
 * - Con otro rol:  muestra la página 403 "Acceso restringido".
 *
 * Esto es solo para la experiencia de usuario: la seguridad real
 * la aplica el backend con IsEspectador / IsOrganizador.
 */

import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import AccesoDenegado from "../../pages/errores/AccesoDenegado";

export default function RutaProtegida({ rol }) {
  const { usuario } = useAuth();
  const location = useLocation();

  if (!usuario) {
    return <Navigate to="/login" replace state={{ desde: location.pathname }} />;
  }

  if (usuario.rol !== rol) {
    // Las rutas del panel no usan EspectadorLayout: la página 403
    // se muestra completa, con su propio fondo.
    return <AccesoDenegado pantallaCompleta={rol === "ORGANIZADOR"} />;
  }

  return <Outlet />;
}
