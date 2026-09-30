/**
 * Error 403: el usuario inició sesión pero su rol no tiene
 * permiso para la sección (por ejemplo, un espectador que intenta
 * abrir el panel de administración o la documentación).
 *
 * Ofrece cerrar sesión para entrar con otra cuenta.
 */

import { Link, useNavigate } from "react-router-dom";

import { NOMBRE_ROL, useAuth } from "../../context/AuthContext";
import PaginaError from "./PaginaError";

export default function AccesoDenegado({ pantallaCompleta = false }) {
  const { usuario, esAdmin, logout } = useAuth();
  const navigate = useNavigate();

  function cambiarCuenta() {
    logout();
    navigate("/login");
  }

  return (
    <PaginaError
      pantallaCompleta={pantallaCompleta}
      codigo="403"
      icono="🔒"
      titulo="Acceso restringido"
      mensaje={
        usuario
          ? `Tu cuenta (${NOMBRE_ROL[usuario.rol] ?? usuario.rol}) no tiene permiso para ver esta sección.`
          : "Necesitas iniciar sesión con una cuenta autorizada."
      }
      acciones={
        <>
          <Link to={esAdmin ? "/panel" : "/"} className="btn btn-primario">
            {esAdmin ? "Ir a mi panel" : "Ver eventos"}
          </Link>
          <button type="button" className={`btn ${pantallaCompleta ? "btn-claro" : "btn-secundario"}`} onClick={cambiarCuenta}>
            Entrar con otra cuenta
          </button>
        </>
      }
    />
  );
}
