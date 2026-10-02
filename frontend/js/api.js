/**
 * GestPro Analytics - API Client
 * Gestiona las llamadas HTTP asíncronas hacia los 3 microservicios.
 * En producción (con Nginx), las rutas son relativas (/api/*).
 * En desarrollo local independiente, permite fallback directo a los puertos 8001, 8002, 8003.
 */

const API_CONFIG = {
  // Detecta si estamos corriendo bajo Nginx con reverse proxy o en desarrollo local directo
  isDirectPorts: window.location.port !== "80" && window.location.port !== "" && !window.location.pathname.startsWith("/"),
  baseUsers: window.location.port === "80" || window.location.port === "8080" || window.location.hostname === "gestpro-analytics.local" 
    ? "/api/users" 
    : "http://localhost:8001",
  baseInventory: window.location.port === "80" || window.location.port === "8080" || window.location.hostname === "gestpro-analytics.local" 
    ? "/api/inventory" 
    : "http://localhost:8002",
  baseAnalytics: window.location.port === "80" || window.location.port === "8080" || window.location.hostname === "gestpro-analytics.local" 
    ? "/api/analytics" 
    : "http://localhost:8003",
};

const api = {
  // Verificación de estado de los 3 microservicios
  async checkHealth() {
    const results = { users: false, inventory: false, analytics: false };
    try {
      const res = await fetch(`${API_CONFIG.baseUsers}/health`);
      results.users = res.ok;
    } catch (e) { results.users = false; }

    try {
      const res = await fetch(`${API_CONFIG.baseInventory}/health`);
      results.inventory = res.ok;
    } catch (e) { results.inventory = false; }

    try {
      const res = await fetch(`${API_CONFIG.baseAnalytics}/health`);
      results.analytics = res.ok;
    } catch (e) { results.analytics = false; }

    return results;
  },

  // Microservicio Users
  async getUsers() {
    const res = await fetch(`${API_CONFIG.baseUsers}/users/`);
    if (!res.ok) throw new Error("Error al obtener usuarios");
    return await res.json();
  },

  async login(username) {
    const res = await fetch(`${API_CONFIG.baseUsers}/users/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username })
    });
    if (!res.ok) throw new Error("Credenciales inválidas");
    return await res.json();
  },

  // Microservicio Inventory
  async getCategories() {
    const res = await fetch(`${API_CONFIG.baseInventory}/inventory/categories`);
    if (!res.ok) throw new Error("Error al obtener categorías");
    return await res.json();
  },

  async getProducts(search = "", categoryId = null) {
    let url = `${API_CONFIG.baseInventory}/inventory/products?`;
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (categoryId) url += `category_id=${categoryId}&`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Error al obtener catálogo de productos");
    return await res.json();
  },

  async getInventoryStats() {
    const res = await fetch(`${API_CONFIG.baseInventory}/inventory/stats`);
    if (!res.ok) throw new Error("Error al obtener estadísticas de inventario");
    return await res.json();
  },

  // Microservicio Sales & Analytics
  async getKPIs() {
    const res = await fetch(`${API_CONFIG.baseAnalytics}/analytics/kpis`);
    if (!res.ok) throw new Error("Error al calcular KPIs");
    return await res.json();
  },

  async getSalesTrend() {
    const res = await fetch(`${API_CONFIG.baseAnalytics}/analytics/sales-trend`);
    if (!res.ok) throw new Error("Error al consultar tendencia de ventas");
    return await res.json();
  },

  async getTopProducts(limit = 5) {
    const res = await fetch(`${API_CONFIG.baseAnalytics}/analytics/top-products?limit=${limit}`);
    if (!res.ok) throw new Error("Error al obtener top productos");
    return await res.json();
  },

  async getSalesByCategory() {
    const res = await fetch(`${API_CONFIG.baseAnalytics}/analytics/by-category`);
    if (!res.ok) throw new Error("Error al obtener ventas por categoría");
    return await res.json();
  },

  async getSalesByPaymentMethod() {
    const res = await fetch(`${API_CONFIG.baseAnalytics}/analytics/by-payment-method`);
    if (!res.ok) throw new Error("Error al obtener métodos de pago");
    return await res.json();
  },

  async getRecentSales(limit = 10) {
    const res = await fetch(`${API_CONFIG.baseAnalytics}/analytics/recent-sales?limit=${limit}`);
    if (!res.ok) throw new Error("Error al obtener transacciones recientes");
    return await res.json();
  }
};
