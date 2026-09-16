// ============================================================
// INMOCONTROL — tasación (wizard), tabs de propiedad, favoritos
// y formularios de contacto / agenda de visita.
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

  // ---------- Favoritos (corazón en las tarjetas) ----------
  document.querySelectorAll("[data-inmo-fav]").forEach((btn) => {
    btn.addEventListener("click", async function (e) {
      e.preventDefault();
      e.stopPropagation();
      const propertyId = btn.getAttribute("data-inmo-fav");
      try {
        const resp = await fetch("/api/inmo/favorito", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ property_id: propertyId }),
        });
        const data = await resp.json();
        if (data.success) {
          btn.classList.toggle("active", data.guardado);
          const icon = btn.querySelector("i");
          if (icon) icon.className = data.guardado ? "fas fa-heart" : "far fa-heart";
        }
      } catch (err) {
        console.error("No se pudo actualizar favoritos", err);
      }
    });
  });

  // ---------- Tabs de detalle de propiedad ----------
  const tabs = document.querySelectorAll("[data-inmo-tab]");
  if (tabs.length) {
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const target = tab.getAttribute("data-inmo-tab");
        document.querySelectorAll("[data-inmo-tab]").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        document.querySelectorAll("[data-inmo-panel]").forEach((panel) => {
          panel.style.display = panel.getAttribute("data-inmo-panel") === target ? "block" : "none";
        });
      });
    });
  }

  // ---------- Galería de fotos de propiedad ----------
  const galleryMain = document.querySelector("#inmo-gallery-main-image");
  const galleryCount = document.querySelector("#inmo-gallery-count");
  const galleryThumbs = document.querySelectorAll(".inmo-gallery-thumb");
  const galleryModal = document.querySelector("#inmo-gallery-modal");
  const galleryModalImage = document.querySelector("#inmo-gallery-modal-image");
  const galleryExpand = document.querySelector(".inmo-gallery-expand");
  const galleryClose = document.querySelector(".inmo-gallery-modal-close");
  const galleryPrev = document.querySelector(".inmo-gallery-modal-prev");
  const galleryNext = document.querySelector(".inmo-gallery-modal-next");

  let galleryImages = [];
  let galleryIndex = 0;

  function updateGallery(index) {
    if (!galleryMain || !galleryThumbs.length) return;
    galleryImages = Array.from(galleryThumbs).map((thumb) => thumb.getAttribute("data-image"));
    galleryIndex = ((index % galleryImages.length) + galleryImages.length) % galleryImages.length;
    const selected = galleryImages[galleryIndex];
    galleryMain.src = selected;
    galleryMain.alt = "Foto de la propiedad";
    galleryThumbs.forEach((thumb, thumbIndex) => {
      thumb.classList.toggle("active", thumbIndex === galleryIndex);
    });
    if (galleryCount) galleryCount.textContent = `${galleryIndex + 1} / ${galleryImages.length}`;
    if (galleryModalImage) galleryModalImage.src = selected;
  }

  galleryThumbs.forEach((thumb) => {
    thumb.addEventListener("click", () => {
      galleryIndex = Number(thumb.getAttribute("data-index")) || 0;
      updateGallery(galleryIndex);
    });
  });

  if (galleryExpand && galleryModal && galleryModalImage) {
    galleryExpand.addEventListener("click", () => {
      galleryModal.classList.add("is-open");
      galleryModal.setAttribute("aria-hidden", "false");
      galleryModalImage.src = galleryMain.src;
    });
  }

  function closeGalleryModal() {
    if (!galleryModal) return;
    galleryModal.classList.remove("is-open");
    galleryModal.setAttribute("aria-hidden", "true");
  }

  if (galleryClose) galleryClose.addEventListener("click", closeGalleryModal);
  if (galleryPrev) {
    galleryPrev.addEventListener("click", () => {
      updateGallery(galleryIndex - 1);
      if (galleryModalImage) galleryModalImage.src = galleryImages[galleryIndex];
    });
  }
  if (galleryNext) {
    galleryNext.addEventListener("click", () => {
      updateGallery(galleryIndex + 1);
      if (galleryModalImage) galleryModalImage.src = galleryImages[galleryIndex];
    });
  }
  if (galleryModal) {
    galleryModal.addEventListener("click", (event) => {
      if (event.target.matches("[data-close-gallery='true']") || event.target === galleryModal) {
        closeGalleryModal();
      }
    });
  }
  document.addEventListener("keydown", (event) => {
    if (!galleryModal || !galleryModal.classList.contains("is-open")) return;
    if (event.key === "Escape") closeGalleryModal();
    if (event.key === "ArrowRight") {
      updateGallery(galleryIndex + 1);
      if (galleryModalImage) galleryModalImage.src = galleryImages[galleryIndex];
    }
    if (event.key === "ArrowLeft") {
      updateGallery(galleryIndex - 1);
      if (galleryModalImage) galleryModalImage.src = galleryImages[galleryIndex];
    }
  });

  if (galleryMain && galleryThumbs.length) {
    updateGallery(0);
  }

  // ---------- Formulario de contacto en el detalle de propiedad ----------
  const formContactoPropiedad = document.querySelector("#inmo-form-contacto-propiedad");
  if (formContactoPropiedad) {
    formContactoPropiedad.addEventListener("submit", async function (e) {
      e.preventDefault();
      const feedback = document.querySelector("#inmo-contacto-feedback");
      const payload = Object.fromEntries(new FormData(formContactoPropiedad).entries());
      payload.property_id = formContactoPropiedad.getAttribute("data-property-id");

      try {
        const resp = await fetch("/api/inmo/contacto", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await resp.json();
        feedback.style.display = "block";
        feedback.textContent = data.success ? "¡Gracias! Te vamos a contactar a la brevedad." : (data.message || "No pudimos enviar tu consulta.");
        feedback.classList.toggle("inmo-notice-error", !data.success);
        if (data.success) formContactoPropiedad.reset();
      } catch (err) {
        feedback.style.display = "block";
        feedback.textContent = "Hubo un problema de conexión. Intentá nuevamente.";
        feedback.classList.add("inmo-notice-error");
      }
    });
  }

  // ---------- Botón "Agendar visita" ----------
  const btnVisita = document.querySelector("#inmo-btn-agendar-visita");
  if (btnVisita) {
    btnVisita.addEventListener("click", async function () {
      const propertyId = btnVisita.getAttribute("data-property-id");
      const feedback = document.querySelector("#inmo-contacto-feedback");
      btnVisita.disabled = true;
      try {
        const resp = await fetch("/api/inmo/visita", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ property_id: propertyId }),
        });
        const data = await resp.json();
        feedback.style.display = "block";
        feedback.textContent = data.success ? "¡Visita agendada! Te contactaremos para coordinar el horario." : (data.message || "No pudimos agendar la visita.");
        feedback.classList.toggle("inmo-notice-error", !data.success);
      } catch (err) {
        feedback.style.display = "block";
        feedback.textContent = "Hubo un problema de conexión. Intentá nuevamente.";
        feedback.classList.add("inmo-notice-error");
      } finally {
        btnVisita.disabled = false;
      }
    });
  }

  // ---------- Formulario de contacto general ----------
  const formContactoGeneral = document.querySelector("#inmo-form-contacto");
  if (formContactoGeneral) {
    formContactoGeneral.addEventListener("submit", async function (e) {
      e.preventDefault();
      const feedback = document.querySelector("#inmo-contacto-general-feedback");
      const payload = Object.fromEntries(new FormData(formContactoGeneral).entries());

      try {
        const resp = await fetch("/api/inmo/contacto", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await resp.json();
        feedback.style.display = "block";
        feedback.textContent = data.success ? "¡Mensaje enviado! Te responderemos a la brevedad." : (data.message || "No pudimos enviar tu mensaje.");
        feedback.classList.toggle("inmo-notice-error", !data.success);
        if (data.success) formContactoGeneral.reset();
      } catch (err) {
        feedback.style.display = "block";
        feedback.textContent = "Hubo un problema de conexión. Intentá nuevamente.";
        feedback.classList.add("inmo-notice-error");
      }
    });
  }

  // ---------- Wizard de tasación: Dirección -> Detalles -> Resultado ----------
  const wizard = document.querySelector("[data-inmo-tasacion-wizard]");
  if (!wizard) return;

  const steps = ["direccion", "detalles", "resultado"];
  const panels = {
    direccion: wizard.querySelector("[data-panel='direccion']"),
    detalles: wizard.querySelector("[data-panel='detalles']"),
    resultado: wizard.querySelector("[data-panel='resultado']"),
  };
  const stepEls = {
    direccion: wizard.querySelector("[data-step='direccion']"),
    detalles: wizard.querySelector("[data-step='detalles']"),
    resultado: wizard.querySelector("[data-step='resultado']"),
  };

  let direccionValor = "";

  function goTo(step) {
    steps.forEach((s) => {
      panels[s].style.display = s === step ? "block" : "none";
      stepEls[s].classList.remove("active", "done");
      if (s === step) stepEls[s].classList.add("active");
      else if (steps.indexOf(s) < steps.indexOf(step)) stepEls[s].classList.add("done");
    });
    window.scrollTo({ top: wizard.offsetTop - 40, behavior: "smooth" });
  }

  const formDireccion = wizard.querySelector("#inmo-form-direccion");
  formDireccion.addEventListener("submit", function (e) {
    e.preventDefault();
    direccionValor = new FormData(formDireccion).get("direccion");
    goTo("detalles");
  });

  wizard.querySelectorAll("[data-inmo-volver]").forEach((btn) => {
    btn.addEventListener("click", () => goTo(btn.getAttribute("data-inmo-volver")));
  });

  const formDetalles = wizard.querySelector("#inmo-form-detalles");
  formDetalles.addEventListener("submit", async function (e) {
    e.preventDefault();
    const errorBox = document.querySelector("#inmo-tasacion-error");
    errorBox.style.display = "none";

    const payload = Object.fromEntries(new FormData(formDetalles).entries());
    payload.direccion = direccionValor;

    try {
      const resp = await fetch("/api/inmo/tasacion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (!data.success) {
        errorBox.style.display = "block";
        errorBox.classList.add("inmo-notice-error");
        errorBox.textContent = data.message || "No pudimos calcular la tasación.";
        return;
      }
      document.querySelector("#inmo-resultado-valor").textContent = data.valor_formateado;
      goTo("resultado");
    } catch (err) {
      errorBox.style.display = "block";
      errorBox.classList.add("inmo-notice-error");
      errorBox.textContent = "Hubo un problema de conexión. Intentá nuevamente.";
    }
  });

  goTo("direccion");
});