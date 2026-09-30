/**
 * Inicio de sesión (espectadores y administradores).
 *
 * Envía usuario y contraseña a POST /api/auth/token/.
 * El backend responde con los tokens access y refresh; el access
 * incluye el claim "rol" que decide a qué vista se entra:
 *
 *   ESPECTADOR  -> catálogo (o la página que pidió login).
 *   ORGANIZADOR -> panel de administración (/panel).
 */

import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import PanelMarca from "./PanelMarca";

import "./Auth.css";

export default function Login() {
  const { login, usuario } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [datos, setDatos] = useState({ username: "", password: "" });
  const [verClave, setVerClave] = useState(false);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  const cambiar = (e) => setDatos({ ...datos, [e.target.name]: e.target.value });

  // Con la sesión ya iniciada no tiene sentido mostrar el formulario.
  if (usuario && !cargando) return <Navigate to="/" replace />;

  // Envía el formulario sin recargar la página.
  async function enviar(e) {
    e.preventDefault();
    setError("");
    setCargando(true);

    try {
      const usuario = await login(datos.username, datos.password);

      if (usuario.rol === "ORGANIZADOR") {
        navigate("/panel", { replace: true });
      } else {
        navigate(location.state?.desde ?? "/", { replace: true });
      }
    } catch (err) {
      setError(err.status === 401 ? "Usuario o contraseña incorrectos." : err.message);
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="auth">
      <PanelMarca
        titulo="Vuelve a vivirlo en primera fila."
        texto="Tus tickets y tu carrito te esperan: quedan guardados en tu cuenta aunque cierres sesión."
      />

      <section className="auth__formulario">
        <form className="auth__tarjeta" onSubmit={enviar} noValidate>
          <h1>Iniciar sesión</h1>
          <p className="subtitulo">Ingresa con tu cuenta de Butaca.</p>

          {location.state?.desde && !error && (
            <div className="alerta alerta-info">🔒 Inicia sesión para continuar con tu compra.</div>
          )}
          {error && <div className="alerta alerta-error" role="alert">⚠ {error}</div>}

          <div className="campo">
            <label htmlFor="username">Usuario</label>
            <input
              id="username"
              name="username"
              className="input"
              value={datos.username}
              onChange={cambiar}
              autoComplete="username"
              autoFocus
              required
            />
          </div>

          <div className="campo">
            <label htmlFor="password">Contraseña</label>
            <div className="auth__clave">
              <input
                id="password"
                name="password"
                type={verClave ? "text" : "password"}
                className="input"
                value={datos.password}
                onChange={cambiar}
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="auth__ver"
                onClick={() => setVerClave(!verClave)}
                aria-label={verClave ? "Ocultar contraseña" : "Mostrar contraseña"}
              >
                {verClave ? "Ocultar" : "Ver"}
              </button>
            </div>
          </div>

          <button
            className="btn btn-primario btn-grande btn-bloque"
            disabled={cargando || !datos.username || !datos.password}
          >
            {cargando ? "Ingresando…" : "Ingresar"}
          </button>

          <p className="auth__alterno">
            ¿No tienes cuenta? <Link to="/registro" state={location.state}>Créala gratis</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
