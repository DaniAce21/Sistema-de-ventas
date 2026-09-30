/**
 * Creación de cuenta de espectador.
 *
 * Endpoint: POST /api/auth/registro/
 *
 * El backend siempre crea el usuario con rol ESPECTADOR (aunque se
 * intente enviar otro rol) y valida la contraseña con los validadores
 * de Django. Los errores por campo llegan en "campos" y se muestran
 * bajo cada input. Tras registrarse se inicia sesión automáticamente.
 */

import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import PanelMarca from "./PanelMarca";

import "./Auth.css";

const INICIAL = { first_name: "", last_name: "", username: "", email: "", password: "", confirmar: "" };

export default function Registro() {
  const { registrar, usuario } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [datos, setDatos] = useState(INICIAL);
  const [errores, setErrores] = useState({});
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  const cambiar = (e) => {
    setDatos({ ...datos, [e.target.name]: e.target.value });
    setErrores({ ...errores, [e.target.name]: undefined });
  };

  // Con la sesión ya iniciada no tiene sentido mostrar el formulario.
  if (usuario && !cargando) return <Navigate to="/" replace />;

  async function enviar(e) {
    e.preventDefault();
    setError("");

    // Validación rápida en el navegador; la definitiva la hace el backend.
    if (datos.password !== datos.confirmar) {
      setErrores({ confirmar: ["Las contraseñas no coinciden."] });
      return;
    }

    setCargando(true);
    try {
      const { confirmar, ...envio } = datos;
      await registrar(envio);
      navigate(location.state?.desde ?? "/", { replace: true });
    } catch (err) {
      setError(err.message);
      setErrores(err.campos ?? {});
    } finally {
      setCargando(false);
    }
  }

  // Input con su mensaje de error del backend debajo.
  const campo = (nombre, etiqueta, props = {}) => (
    <div className="campo">
      <label htmlFor={nombre}>{etiqueta}</label>
      <input
        id={nombre}
        name={nombre}
        className="input"
        value={datos[nombre]}
        onChange={cambiar}
        aria-invalid={Boolean(errores[nombre])}
        aria-describedby={errores[nombre] ? `${nombre}-error` : undefined}
        {...props}
      />
      {errores[nombre] && (
        <span id={`${nombre}-error`} className="error-campo">
          {errores[nombre].join(" ")}
        </span>
      )}
    </div>
  );

  return (
    <div className="auth">
      <PanelMarca
        titulo="Tu próxima butaca te está esperando."
        texto="Crea tu cuenta para comprar entradas, guardar tu carrito y llevar tus tickets con código QR."
      />

      <section className="auth__formulario">
        <form className="auth__tarjeta" onSubmit={enviar} noValidate>
          <h1>Crear cuenta</h1>
          <p className="subtitulo">Es gratis y toma menos de un minuto.</p>

          {error && <div className="alerta alerta-error" role="alert">⚠ {error}</div>}

          <div className="fila-campos">
            {campo("first_name", "Nombre", { autoComplete: "given-name" })}
            {campo("last_name", "Apellido", { autoComplete: "family-name" })}
          </div>
          {campo("username", "Usuario", { autoComplete: "username", required: true })}
          {campo("email", "Correo electrónico", { type: "email", autoComplete: "email", required: true })}
          {campo("password", "Contraseña", { type: "password", autoComplete: "new-password", required: true })}
          {campo("confirmar", "Repite la contraseña", { type: "password", autoComplete: "new-password", required: true })}

          <p className="auth__ayuda">Mínimo 8 caracteres, no solo números ni una contraseña común.</p>

          <button
            className="btn btn-primario btn-grande btn-bloque"
            disabled={cargando || !datos.username || !datos.email || !datos.password}
          >
            {cargando ? "Creando cuenta…" : "Crear cuenta"}
          </button>

          <p className="auth__alterno">
            ¿Ya tienes cuenta? <Link to="/login" state={location.state}>Inicia sesión</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
