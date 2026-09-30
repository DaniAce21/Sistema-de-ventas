/**
 * Carro de compras persistente y checkout.
 *
 * Endpoints:
 *   GET    /api/carro-tickets/   Carrito guardado en PostgreSQL.
 *   DELETE /api/carro-tickets/   Quitar un sector o vaciar.
 *   POST   /api/compras/pagar/   Checkout transaccional.
 *
 * El carrito se lee siempre desde el backend (no de localStorage),
 * por eso se conserva tras cerrar sesión o cambiar de dispositivo.
 *
 * Al pagar, el backend (dentro de transaction.atomic):
 *   1. Valida el stock de cada sector (bloqueando las filas).
 *   2. Crea la orden y descuenta el stock.
 *   3. Genera una entrada con UUID por ticket.
 *   4. Marca la orden como PAGADO y vacía el carrito.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../../api/client";
import Afiche from "../../components/comun/Afiche";
import Cargando from "../../components/comun/Cargando";
import Modal from "../../components/comun/Modal";
import Vacio from "../../components/comun/Vacio";
import { useCarrito } from "../../context/CarritoContext";
import { formatoFecha, formatoPrecio } from "../../utils/formato";

import "./Carrito.css";

// Pasos del proceso de compra que se muestran arriba.
function Pasos({ actual }) {
  const pasos = ["Carrito", "Pago", "Tickets"];
  return (
    <ol className="pasos" aria-label="Proceso de compra">
      {pasos.map((paso, i) => (
        <li key={paso} className={i < actual ? "hecho" : i === actual ? "actual" : ""} aria-current={i === actual ? "step" : undefined}>
          <span className="pasos__numero">{i < actual ? "✓" : i + 1}</span>
          {paso}
        </li>
      ))}
    </ol>
  );
}

export default function Carrito() {
  const { carrito, refrescar, quitar, vaciar, marcarPagado } = useCarrito();
  const [error, setError] = useState("");
  const [procesando, setProcesando] = useState(false);
  const [confirmarPago, setConfirmarPago] = useState(false);
  const [confirmarVaciar, setConfirmarVaciar] = useState(false);
  const [compra, setCompra] = useState(null);

  // Siempre se relee desde PostgreSQL al entrar al carrito.
  useEffect(() => {
    refrescar().catch((err) => setError(err.message));
  }, [refrescar]);

  // Ejecuta una operación mostrando errores del backend.
  async function operar(accion) {
    setError("");
    setProcesando(true);
    try {
      await accion();
    } catch (err) {
      setError(err.message);
    } finally {
      setProcesando(false);
    }
  }

  async function pagar() {
    await operar(async () => {
      try {
        const respuesta = await api("/compras/pagar/", { method: "POST", body: {} });
        setCompra(respuesta);
        marcarPagado();
      } catch (err) {
        // Ej.: stock insuficiente. La transacción se revierte y el
        // carrito queda intacto; se relee para mostrar el stock real.
        await refrescar().catch(() => {});
        throw err;
      }
    });
    setConfirmarPago(false);
  }

  /* ---------- Compra confirmada ---------- */
  if (compra) {
    return (
      <div className="contenedor carrito">
        <Pasos actual={3} />
        <section className="tarjeta confirmacion">
          <div className="confirmacion__icono" aria-hidden="true">✓</div>
          <h1>¡Compra confirmada!</h1>
          <p className="texto-suave">
            Tu orden <strong>#{compra.compra.id}</strong> quedó en estado <strong>{compra.compra.estado}</strong>.
            Generamos {compra.entradas.length} {compra.entradas.length === 1 ? "ticket" : "tickets"} con código único.
          </p>
          <div className="confirmacion__total">
            <span>Total pagado</span>
            <strong>{formatoPrecio(compra.compra.total)}</strong>
          </div>
          <div className="confirmacion__acciones">
            <Link to="/mis-tickets" className="btn btn-primario btn-grande">Ver mis tickets</Link>
            <Link to="/" className="btn btn-secundario btn-grande">Seguir explorando</Link>
          </div>
        </section>
      </div>
    );
  }

  if (!carrito) {
    return error ? (
      <div className="contenedor carrito"><div className="alerta alerta-error">⚠ {error}</div></div>
    ) : (
      <Cargando texto="Cargando tu carrito…" />
    );
  }

  const items = carrito.items;
  const total = items.reduce((suma, item) => suma + Number(item.sector.precio) * item.cantidad, 0);
  const cantidad = items.reduce((suma, item) => suma + item.cantidad, 0);
  const sinStock = items.some((item) => item.cantidad > item.sector.stock);

  return (
    <div className="contenedor carrito">
      <Pasos actual={0} />
      <h1 className="titulo-pagina">Tu carrito</h1>
      <p className="subtitulo">Tu carrito se guarda en tu cuenta. El stock se reserva recién al pagar.</p>

      {error && <div className="alerta alerta-error" role="alert">⚠ {error}</div>}

      {items.length === 0 ? (
        <Vacio icono="🛒" titulo="Tu carrito está vacío" texto="Explora los eventos programados y elige tus entradas.">
          <Link to="/" className="btn btn-primario">Explorar eventos</Link>
        </Vacio>
      ) : (
        <div className="carrito__layout">
          {/* ---------- Items ---------- */}
          <ul className="carrito__items">
            {items.map((item) => {
              const faltaStock = item.cantidad > item.sector.stock;
              const evento = {
                nombre: item.sector.evento,
                imagen: item.sector.imagen,
                categoria: item.sector.categoria,
              };

              return (
                <li key={item.id} className="tarjeta item">
                  <Link to={`/eventos/${item.sector.evento_id}`} className="item__afiche">
                    <Afiche evento={evento} />
                  </Link>
                  <div className="item__info">
                    <h3>{item.sector.evento}</h3>
                    <p className="texto-suave">{formatoFecha(item.sector.evento_fecha)}</p>
                    <p>
                      <strong>{item.sector.nombre}</strong> · {formatoPrecio(item.sector.precio)} c/u × {item.cantidad}
                    </p>
                    {faltaStock && (
                      <p className="item__aviso">
                        ⚠ Solo quedan {item.sector.stock} disponibles. Quita este sector o el pago será rechazado.
                      </p>
                    )}
                  </div>
                  <div className="item__lado">
                    <strong className="item__subtotal">{formatoPrecio(Number(item.sector.precio) * item.cantidad)}</strong>
                    <button
                      type="button"
                      className="btn btn-peligro btn-chico"
                      onClick={() => operar(() => quitar(item.sector.id))}
                      disabled={procesando}
                    >
                      Quitar
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>

          {/* ---------- Resumen ---------- */}
          <aside className="tarjeta resumen" aria-label="Resumen de compra">
            <h2>Resumen</h2>
            <dl>
              <div>
                <dt>Entradas</dt>
                <dd>{cantidad}</dd>
              </div>
              <div className="resumen__total">
                <dt>Total</dt>
                <dd>{formatoPrecio(total)}</dd>
              </div>
            </dl>
            <p className="resumen__nota">
              El total definitivo se calcula al pagar con los precios vigentes.
            </p>
            <button
              type="button"
              className="btn btn-primario btn-grande btn-bloque"
              onClick={() => setConfirmarPago(true)}
              disabled={procesando}
            >
              Pagar {formatoPrecio(total)}
            </button>
            <button
              type="button"
              className="btn btn-secundario btn-bloque"
              onClick={() => setConfirmarVaciar(true)}
              disabled={procesando}
            >
              Vaciar carrito
            </button>
            {sinStock && <p className="resumen__nota resumen__nota--aviso">Hay sectores sin stock suficiente.</p>}
          </aside>
        </div>
      )}

      <Modal
        abierto={confirmarPago}
        titulo="Confirmar pago"
        textoConfirmar={`Pagar ${formatoPrecio(total)}`}
        procesando={procesando}
        onConfirmar={pagar}
        onCancelar={() => setConfirmarPago(false)}
      >
        <p>
          Vas a comprar <strong>{cantidad}</strong> {cantidad === 1 ? "entrada" : "entradas"} por un total de{" "}
          <strong>{formatoPrecio(total)}</strong>.
        </p>
        <p>Al confirmar se descontará el stock y recibirás tus tickets con código QR.</p>
      </Modal>

      <Modal
        abierto={confirmarVaciar}
        titulo="¿Vaciar el carrito?"
        textoConfirmar="Vaciar"
        peligro
        procesando={procesando}
        onConfirmar={async () => {
          await operar(vaciar);
          setConfirmarVaciar(false);
        }}
        onCancelar={() => setConfirmarVaciar(false)}
      >
        <p>Se quitarán todas las entradas seleccionadas.</p>
      </Modal>
    </div>
  );
}
