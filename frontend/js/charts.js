/**
 * GestPro Analytics - Chart.js Controllers
 * Maneja el ciclo de vida y renderizado de los 4 gráficos interactivos del Dashboard.
 */

let salesTrendChartInstance = null;
let topProductsChartInstance = null;
let categoryChartInstance = null;
let paymentMethodChartInstance = null;

const charts = {
  // Formateador de moneda en pesos colombianos ($ COP)
  formatCurrency(value) {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0
    }).format(value);
  },

  // Gráfico 1: Tendencia Mensual de Ventas vs Utilidad
  renderSalesTrend(trendData) {
    const ctx = document.getElementById('salesTrendChart');
    if (!ctx) return;

    if (salesTrendChartInstance) {
      salesTrendChartInstance.destroy();
    }

    const labels = trendData.map(d => d.month);
    const revenues = trendData.map(d => d.revenue);
    const profits = trendData.map(d => d.profit);

    salesTrendChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Ingresos Brutos',
            data: revenues,
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.1)',
            fill: true,
            tension: 0.35,
            borderWidth: 2.5,
            pointRadius: 4,
            pointBackgroundColor: '#2563eb'
          },
          {
            label: 'Utilidad Neta',
            data: profits,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true,
            tension: 0.35,
            borderWidth: 2.5,
            pointRadius: 4,
            pointBackgroundColor: '#10b981'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { intersect: false, mode: 'index' },
        plugins: {
          legend: { position: 'top' },
          tooltip: {
            callbacks: {
              label: (context) => `${context.dataset.label}: ${charts.formatCurrency(context.raw)}`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (val) => '$' + (val / 1000000).toFixed(1) + 'M'
            },
            grid: { color: '#f1f5f9' }
          },
          x: { grid: { display: false } }
        }
      }
    });
  },

  // Gráfico 2: Top 5 Productos por Facturación
  renderTopProducts(topData) {
    const ctx = document.getElementById('topProductsChart');
    if (!ctx) return;

    if (topProductsChartInstance) {
      topProductsChartInstance.destroy();
    }

    const labels = topData.map(d => d.product_name.length > 25 ? d.product_name.substring(0, 22) + '...' : d.product_name);
    const revenues = topData.map(d => d.total_revenue);

    topProductsChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Facturación ($ COP)',
          data: revenues,
          backgroundColor: '#3b82f6',
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `Ventas: ${charts.formatCurrency(ctx.raw)}`
            }
          }
        },
        scales: {
          x: {
            ticks: {
              callback: (val) => '$' + (val / 1000000).toFixed(1) + 'M'
            },
            grid: { color: '#f1f5f9' }
          },
          y: { grid: { display: false } }
        }
      }
    });
  },

  // Gráfico 3: Distribución por Categoría Comercial
  renderCategoryDistribution(catData) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    if (categoryChartInstance) {
      categoryChartInstance.destroy();
    }

    const labels = catData.map(d => d.category_name);
    const revenues = catData.map(d => d.total_revenue);
    const palette = ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'];

    categoryChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: revenues,
          backgroundColor: palette,
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12 } },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${charts.formatCurrency(ctx.raw)}`
            }
          }
        },
        cutout: '65%'
      }
    });
  },

  // Gráfico 4: Participación de Métodos de Pago
  renderPaymentMethodDistribution(methodData) {
    const ctx = document.getElementById('paymentMethodChart');
    if (!ctx) return;

    if (paymentMethodChartInstance) {
      paymentMethodChartInstance.destroy();
    }

    const labels = methodData.map(d => d.payment_method);
    const totals = methodData.map(d => d.total_amount);
    const palette = ['#10b981', '#6366f1', '#f97316'];

    paymentMethodChartInstance = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{
          data: totals,
          backgroundColor: palette,
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12 } },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${charts.formatCurrency(ctx.raw)}`
            }
          }
        }
      }
    });
  }
};
