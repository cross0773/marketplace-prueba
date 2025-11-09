/**
 * Obtiene los encabezados de autenticación, incluyendo el token JWT si está disponible.
 * @returns {Object} Un objeto con los encabezados para las peticiones fetch.
 */
function getAuthHeaders() {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Obtiene la lista de productos desde la API.
 * @returns {Promise<Array>} Lista de productos.
 * @throws {Error} Si hay un error al cargar los productos.
 */
async function fetchProductos() {
  try {
    const response = await fetch(`${window.GATEWAY_URL}/api/v1/productos/`, {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'include'
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Error al cargar los productos');
    }

    return await response.json();
  } catch (error) {
    console.error('Error en fetchProductos:', error);
    throw error;
  }
}

/**
 * Muestra una notificación (toast) en la pantalla.
 * @param {string} message - El mensaje a mostrar.
 * @param {string} type - El tipo de notificación ('success', 'danger', 'info', 'warning').
 */
function showToast(message, type = 'info') {
  const toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) return;

  const toastId = `toast-${Date.now()}`;
  const toastHTML = `
    <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  toastContainer.insertAdjacentHTML('beforeend', toastHTML);
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, { delay: 5000 }); // Se oculta a los 5 segundos
  toast.show();
}

// Asegúrate de que las funciones estén disponibles globalmente si es necesario
window.getAuthHeaders = getAuthHeaders;
window.fetchProductos = fetchProductos;
window.showToast = showToast;

/**
 * Formatea un número como moneda colombiana (COP), usando '.' como separador de miles.
 * @param {number} value - El número a formatear.
 * @returns {string} - El valor formateado como moneda.
 */
function formatCurrency(value) {
  if (typeof value !== 'number') {
    return 'N/A';
  }
  // Usamos el locale 'es-CO' para el formato colombiano y quitamos los decimales.
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
}