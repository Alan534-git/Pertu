document.addEventListener("DOMContentLoaded", function () {
  const imageButton = document.querySelector("#dual-product-image");
  const image = document.querySelector("#dual-product-image-source");
  const modal = document.querySelector("#dual-image-modal");
  const modalImage = document.querySelector("#dual-image-modal-source");
  const closeButton = document.querySelector(".dual-image-modal-close");
  const colorSelect = document.querySelector("#dual-color-select");

  function closeModal() {
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
  }

  if (imageButton && modal && image && modalImage) {
    imageButton.addEventListener("click", function () {
      modalImage.src = image.src;
      modal.classList.add("is-open");
      modal.setAttribute("aria-hidden", "false");
    });
    modal.addEventListener("click", function (event) {
      if (event.target === modal) closeModal();
    });
  }

  if (closeButton) closeButton.addEventListener("click", closeModal);
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeModal();
  });

  document.querySelectorAll(".dual-product-swatch").forEach(function (swatch) {
    swatch.addEventListener("click", function () {
      const color = swatch.getAttribute("data-color");
      document.querySelectorAll(".dual-product-swatch").forEach(function (item) {
        item.classList.toggle("active", item === swatch);
      });
      if (colorSelect) colorSelect.value = color;
      if (imageButton) imageButton.style.background = swatch.getAttribute("data-color-media");
    });
  });
});
