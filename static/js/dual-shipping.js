document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("#dual-shipping-form");
  const postal = document.querySelector("#dual-shipping-postal");
  const result = document.querySelector("#dual-shipping-result");
  if (!form || !postal || !result) return;

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    result.textContent = "Envío disponible: llega en 2 a 5 días hábiles. Costo: $1.990.";
    result.classList.add("is-visible");
  });
});