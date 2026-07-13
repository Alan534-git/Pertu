document.addEventListener('DOMContentLoaded', function () {
    const feedback = document.getElementById('admin-feedback');
    const buttons = document.querySelectorAll('.admin-status-btn');

    buttons.forEach(button => {
        button.addEventListener('click', async function () {
            const collection = button.dataset.collection;
            const requestId = button.dataset.requestId;
            const status = button.dataset.status;

            try {
                const response = await fetch('/api/admin/request-status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ collection, request_id: requestId, status })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    if (feedback) {
                        feedback.style.display = 'block';
                        feedback.className = 'notice';
                        feedback.textContent = 'Estado actualizado correctamente.';
                    }
                    button.textContent = 'Aprobado';
                    button.disabled = true;
                } else if (feedback) {
                    feedback.style.display = 'block';
                    feedback.className = 'notice error';
                    feedback.textContent = data.message || 'No se pudo actualizar el estado.';
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
});