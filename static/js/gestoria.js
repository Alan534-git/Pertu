document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('gestoria-form');
    const feedback = document.getElementById('gestoria-feedback');

    if (!form) {
        return;
    }

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const payload = {
            nombre: document.getElementById('nombre').value.trim(),
            dni: document.getElementById('dni').value.trim(),
            servicio_id: document.getElementById('servicio_id').value,
            detalle: document.getElementById('detalle').value.trim()
        };

        try {
            const response = await fetch('/api/tramite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (response.ok && data.success) {
                if (feedback) {
                    feedback.style.display = 'block';
                    feedback.className = 'notice';
                    feedback.textContent = 'Trámite registrado correctamente.';
                }
                form.reset();
            } else {
                if (feedback) {
                    feedback.style.display = 'block';
                    feedback.className = 'notice error';
                    feedback.textContent = data.message || 'No se pudo registrar el trámite.';
                }
            }
        } catch (error) {
            if (feedback) {
                feedback.style.display = 'block';
                feedback.className = 'notice error';
                feedback.textContent = 'Error de conexión con el servidor.';
            }
        }
    });
});