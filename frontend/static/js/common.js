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

// Asegúrate de que las funciones estén disponibles globalmente si es necesario
window.getAuthHeaders = getAuthHeaders;
window.fetchProductos = fetchProductos;