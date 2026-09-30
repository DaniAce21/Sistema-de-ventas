/**
 * Captura errores inesperados de renderizado en cualquier componente.
 *
 * Sin esto, un error de JavaScript deja la página en blanco.
 * Con esto se muestra la página "Algo salió mal" (error 500 del frontend)
 * y el detalle queda en la consola del navegador.
 *
 * Los Error Boundaries deben ser componentes de clase: React no
 * ofrece aún un equivalente con hooks.
 */

import { Component } from "react";

import PaginaError from "../../pages/errores/PaginaError";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("Error no controlado en la interfaz:", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <PaginaError
          pantallaCompleta
          codigo="500"
          icono="🛠"
          titulo="Algo salió mal"
          mensaje="Ocurrió un error inesperado en la página. Recarga para intentarlo de nuevo."
          acciones={
            <button className="btn btn-primario" onClick={() => window.location.assign("/")}>
              Volver al inicio
            </button>
          }
        />
      );
    }

    return this.props.children;
  }
}
