document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("[data-dual-product]");
  if (!form) return;

  const stock = JSON.parse(form.getAttribute("data-stock") || "{}");
  const colorSelect = document.querySelector("#dual-color-select");
  const sizeSelect = document.querySelector("#dual-size-select");
  const status = document.querySelector("#dual-stock-status");
  const buyButton = document.querySelector("#dual-btn-comprar");

  function refreshStock() {
    const color = colorSelect.value;
    const sizes = stock[color] || {};
    let selectedAvailable = false;

    Array.from(sizeSelect.options).forEach(function (option) {
      const available = Number(sizes[option.value] || 0) > 0;
      option.disabled = !available;
      option.textContent = available ? option.dataset.label : option.dataset.label + " - SIN STOCK";
      if (option.selected && available) selectedAvailable = true;
    });

    if (!selectedAvailable) {
      const firstAvailable = Array.from(sizeSelect.options).find((option) => !option.disabled);
      if (firstAvailable) {
        firstAvailable.selected = true;
        selectedAvailable = true;
      }
    }

    const availableCount = Object.values(sizes).filter((quantity) => Number(quantity) > 0).length;
    status.textContent = selectedAvailable
      ? "Talle seleccionado disponible"
      : "SIN STOCK en todos los talles para este color";
    status.classList.toggle("is-out", !selectedAvailable);
    buyButton.disabled = !selectedAvailable;
    buyButton.textContent = selectedAvailable ? "COMPRAR" : "SIN STOCK";

    if (availableCount === 0) {
      status.textContent = "SIN STOCK en este color";
    }
  }

  colorSelect.addEventListener("change", refreshStock);
  document.querySelectorAll("[data-color]").forEach(function (swatch) {
    swatch.addEventListener("click", function () {
      colorSelect.value = swatch.getAttribute("data-color");
      refreshStock();
    });
  });
  Array.from(sizeSelect.options).forEach(function (option) {
    option.dataset.label = option.value;
  });
  refreshStock();
});