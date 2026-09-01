// ============================================================
// DUAL — wizard de compra (Envío -> Pago -> Confirmación)
// Se activa únicamente al presionar "Comprar" en un producto.
// ============================================================

(function () {
  const wizard = document.querySelector("[data-dual-wizard]");
  if (!wizard) return;

  const steps = ["envio", "pago", "confirmacion"];
  const panels = {
    envio: document.querySelector("[data-panel='envio']"),
    pago: document.querySelector("[data-panel='pago']"),
    confirmacion: document.querySelector("[data-panel='confirmacion']"),
  };
  const tabs = {
    envio: document.querySelector("[data-step='envio']"),
    pago: document.querySelector("[data-step='pago']"),
    confirmacion: document.querySelector("[data-step='confirmacion']"),
  };

  let currentStep = "envio";
  let selectedPayment = "tarjeta";

  function goTo(step) {
    currentStep = step;
    steps.forEach((s) => {
      panels[s].style.display = s === step ? "block" : "none";
      tabs[s].classList.remove("active", "done");
      if (s === step) tabs[s].classList.add("active");
      else if (steps.indexOf(s) < steps.indexOf(step)) tabs[s].classList.add("done");
    });
    window.scrollTo({ top: wizard.offsetTop - 80, behavior: "smooth" });
  }

  // --- paso 1: envío ---
  const formEnvio = document.querySelector("#dual-form-envio");
  formEnvio.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!formEnvio.checkValidity()) {
      formEnvio.reportValidity();
      return;
    }
    goTo("pago");
  });

  // --- paso 2: pago ---
  document.querySelectorAll("[data-pay-option]").forEach((el) => {
    el.addEventListener("click", () => {
      document.querySelectorAll("[data-pay-option]").forEach((o) => o.classList.remove("selected"));
      el.classList.add("selected");
      selectedPayment = el.getAttribute("data-pay-option");
      const cardFields = document.querySelector("#dual-card-fields");
      if (cardFields) cardFields.style.display = selectedPayment === "tarjeta" ? "block" : "none";
    });
  });

  document.querySelector("#dual-btn-volver-envio").addEventListener("click", () => goTo("envio"));

  const formPago = document.querySelector("#dual-form-pago");
  const btnPagar = document.querySelector("#dual-btn-pagar");

  formPago.addEventListener("submit", async function (e) {
    e.preventDefault();
    if (selectedPayment === "tarjeta" && !formPago.checkValidity()) {
      formPago.reportValidity();
      return;
    }

    btnPagar.disabled = true;
    btnPagar.textContent = "Procesando...";

    const payload = JSON.parse(wizard.getAttribute("data-order-payload"));
    payload.metodo_pago = selectedPayment;
    payload.envio = Object.fromEntries(new FormData(formEnvio).entries());

    try {
      const resp = await fetch("/api/dual/pedido", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();

      if (!data.success) {
        alert(data.message || "No se pudo procesar el pago.");
        btnPagar.disabled = false;
        btnPagar.textContent = "Pagar " + wizard.getAttribute("data-total-label");
        return;
      }

      document.querySelector("#dual-confirm-order-id").textContent = data.order.numero;
      document.querySelector("#dual-confirm-total").textContent = data.order.total_formateado;
      document.querySelector("#dual-confirm-email").textContent = payload.envio.email || "";
      document.querySelector("#dual-link-seguimiento").href = "/dual/pedido/" + data.order.id;
      document.querySelector("#dual-link-pedidos").href = "/dual/pedidos";

      goTo("confirmacion");
    } catch (err) {
      alert("Hubo un problema de conexión. Intentá nuevamente.");
      btnPagar.disabled = false;
      btnPagar.textContent = "Pagar " + wizard.getAttribute("data-total-label");
    }
  });

  goTo("envio");
})();