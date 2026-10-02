/**
 * GestPro Analytics - Main Application Controller
 * Controla la lógica de interfaz, cambio de roles y actualización de datos.
 */

let currentRole = 'admin'; // 'admin' | 'vendedor'
let allProducts = [];
let selectedCategoryId = null;

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  setupEventListeners();
  await updateHealthBadges();
  await loadRoleView(currentRole);

  // Verificación periódica del estado de los microservicios cada 30 segundos
  setInterval(updateHealthBadges, 30000);
}

function setupEventListeners() {
  // Cambio de rol mediante los botones del navbar
  const btnRoleAdmin = document.getElementById('btnRoleAdmin');
  const btnRoleVendedor = document.getElementById('btnRoleVendedor');

  if (btnRoleAdmin && btnRoleVendedor) {
    btnRoleAdmin.addEventListener('click', () => switchRole('admin'));
    btnRoleVendedor.addEventListener('click', () => switchRole('vendedor'));
  }

  // Buscador de productos en tiempo real para el vendedor
  const searchInput = document.getElementById('productSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      filterProductsList(e.target.value);
    });
  }

  // Botón de refrescar datos
  const btnRefresh = document.getElementById('btnRefresh');
  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      loadRoleView(currentRole);
      updateHealthBadges();
    });
  }
}

async function updateHealthBadges() {
  const health = await api.checkHealth();

  setServiceBadge('badgeUsers', health.users, 'Users :8001');
  setServiceBadge('badgeInventory', health.inventory, 'Inventory :8002');
  setServiceBadge('badgeAnalytics', health.analytics, 'Analytics :8003');
}

function setServiceBadge(elementId, isOnline, name) {
  const el = document.getElementById(elementId);
  if (!el) return;

  if (isOnline) {
    el.className = 'status-pill bg-success-subtle text-success border border-success-subtle';
    el.innerHTML = `<span class="status-dot"></span> ${name} Online`;
  } else {
    el.className = 'status-pill bg-danger-subtle text-danger border border-danger-subtle';
    el.innerHTML = `<span class="status-dot" style="background-color: #ef4444"></span> ${name} Offline`;
  }
}

function switchRole(role) {
  currentRole = role;
  const btnRoleAdmin = document.getElementById('btnRoleAdmin');
  const btnRoleVendedor = document.getElementById('btnRoleVendedor');

  if (role === 'admin') {
    btnRoleAdmin.classList.add('btn-primary');
    btnRoleAdmin.classList.remove('btn-outline-primary');
    btnRoleVendedor.classList.remove('btn-primary');
    btnRoleVendedor.classList.add('btn-outline-primary');
  } else {
    btnRoleVendedor.classList.add('btn-primary');
    btnRoleVendedor.classList.remove('btn-outline-primary');
    btnRoleAdmin.classList.remove('btn-primary');
    btnRoleAdmin.classList.add('btn-outline-primary');
  }

  loadRoleView(role);
}

async function loadRoleView(role) {
  const adminSection = document.getElementById('adminSection');
  const vendedorSection = document.getElementById('vendedorSection');

  if (role === 'admin') {
    adminSection.classList.remove('d-none');
    vendedorSection.classList.add('d-none');
    await loadAdminDashboard();
  } else {
    adminSection.classList.add('d-none');
    vendedorSection.classList.remove('d-none');
    await loadVendedorView();
  }
}

// -------------------------------------------------------------
// VISTA: GERENTE COMERCIAL (ADMIN)
// -------------------------------------------------------------
async function loadAdminDashboard() {
  try {
    // 1. Cargar KPIs
    const kpis = await api.getKPIs();
    document.getElementById('kpiRevenue').innerText = charts.formatCurrency(kpis.total_revenue);
    document.getElementById('kpiSalesCount').innerText = `${kpis.total_sales} ventas registradas`;

    document.getElementById('kpiProfit').innerText = charts.formatCurrency(kpis.net_profit);
    document.getElementById('kpiCost').innerText = `Costos: ${charts.formatCurrency(kpis.total_cost)}`;

    document.getElementById('kpiMargin').innerText = `${kpis.profit_margin_pct}%`;
    document.getElementById('kpiAvgTicket').innerText = charts.formatCurrency(kpis.avg_ticket);

    // 2. Cargar Gráficos
    const trend = await api.getSalesTrend();
    charts.renderSalesTrend(trend);

    const topProducts = await api.getTopProducts(5);
    charts.renderTopProducts(topProducts);

    const categories = await api.getSalesByCategory();
    charts.renderCategoryDistribution(categories);

    const paymentMethods = await api.getSalesByPaymentMethod();
    charts.renderPaymentMethodDistribution(paymentMethods);

    // 3. Cargar Transacciones Recientes
    const recent = await api.getRecentSales(8);
    renderRecentSalesTable(recent);

  } catch (error) {
    console.error("Error al cargar dashboard de administrador:", error);
  }
}

function renderRecentSalesTable(sales) {
  const tbody = document.getElementById('recentSalesTableBody');
  if (!tbody) return;

  if (sales.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-3 text-muted">No hay transacciones registradas</td></tr>';
    return;
  }

  tbody.innerHTML = sales.map(s => `
    <tr>
      <td class="fw-semibold text-primary">${s.invoice_code}</td>
      <td>${s.date} <small class="text-muted">${s.time}</small></td>
      <td>${s.user_name}</td>
      <td><span class="badge bg-light text-dark border">${s.payment_method}</span></td>
      <td><small class="text-muted">${s.items.map(i => `${i.quantity}x ${i.product_name}`).join(', ')}</small></td>
      <td class="text-end fw-bold">${charts.formatCurrency(s.total)}</td>
    </tr>
  `).join('');
}

// -------------------------------------------------------------
// VISTA: VENDEDOR / CAJERO (OPERATIVO)
// -------------------------------------------------------------
async function loadVendedorView() {
  try {
    // 1. Cargar estadísticas de inventario
    const stats = await api.getInventoryStats();
    document.getElementById('vendedorTotalProducts').innerText = stats.total_products || 0;
    document.getElementById('vendedorTotalUnits').innerText = stats.total_units || 0;
    document.getElementById('vendedorLowStock').innerText = stats.low_stock_count || 0;
    document.getElementById('vendedorOutOfStock').innerText = stats.out_of_stock_count || 0;

    // 2. Cargar botones de categorías
    const categories = await api.getCategories();
    renderCategoryFilterButtons(categories);

    // 3. Cargar catálogo de productos
    allProducts = await api.getProducts();
    renderProductsTable(allProducts);

  } catch (error) {
    console.error("Error al cargar vista de vendedor:", error);
  }
}

function renderCategoryFilterButtons(categories) {
  const container = document.getElementById('categoryFiltersContainer');
  if (!container) return;

  let html = `<button class="btn btn-sm ${selectedCategoryId === null ? 'btn-dark' : 'btn-outline-secondary'}" onclick="filterByCategory(null)">Todas</button>`;
  categories.forEach(cat => {
    const isSelected = selectedCategoryId === cat.id;
    html += `<button class="btn btn-sm ${isSelected ? 'btn-dark' : 'btn-outline-secondary'}" onclick="filterByCategory(${cat.id})">${cat.name}</button>`;
  });
  container.innerHTML = html;
}

window.filterByCategory = function(catId) {
  selectedCategoryId = catId;
  const searchInput = document.getElementById('productSearchInput');
  const searchTerm = searchInput ? searchInput.value : '';
  
  // Re-render botones para actualizar estado activo
  api.getCategories().then(renderCategoryFilterButtons);

  filterProductsList(searchTerm);
};

function filterProductsList(searchTerm) {
  let filtered = allProducts;

  if (selectedCategoryId) {
    filtered = filtered.filter(p => p.category_id === selectedCategoryId);
  }

  if (searchTerm && searchTerm.trim() !== '') {
    const term = searchTerm.toLowerCase().trim();
    filtered = filtered.filter(p => 
      p.name.toLowerCase().includes(term) || 
      p.sku.toLowerCase().includes(term) || 
      (p.barcode && p.barcode.includes(term))
    );
  }

  renderProductsTable(filtered);
}

function renderProductsTable(products) {
  const tbody = document.getElementById('productsTableBody');
  if (!tbody) return;

  if (products.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No se encontraron productos coincidentes</td></tr>';
    return;
  }

  tbody.innerHTML = products.map(p => {
    let stockBadge = '';
    if (p.stock === 0) {
      stockBadge = '<span class="stock-badge-out"><i class="fa fa-times-circle"></i> Agotado (0)</span>';
    } else if (p.stock <= p.min_stock) {
      stockBadge = `<span class="stock-badge-low"><i class="fa fa-exclamation-triangle"></i> Bajo Stock (${p.stock})</span>`;
    } else {
      stockBadge = `<span class="stock-badge-high"><i class="fa fa-check-circle"></i> Disponible (${p.stock})</span>`;
    }

    return `
      <tr>
        <td class="fw-semibold font-monospace">${p.sku}</td>
        <td>
          <div class="fw-bold">${p.name}</div>
          <small class="text-muted">Cód: ${p.barcode || 'N/A'}</small>
        </td>
        <td><span class="badge bg-secondary-subtle text-secondary border">${p.category_name}</span></td>
        <td class="text-end fw-bold text-success">${charts.formatCurrency(p.price)}</td>
        <td class="text-center">${stockBadge}</td>
        <td class="text-center text-muted">${p.min_stock} und</td>
        <td class="text-center">
          <button class="btn btn-sm btn-outline-primary" onclick="alert('Producto seleccionado: ${p.name} - Precio: ${charts.formatCurrency(p.price)}')">
            <i class="fa fa-shopping-cart"></i> Cotizar
          </button>
        </td>
      </tr>
    `;
  }).join('');
}
