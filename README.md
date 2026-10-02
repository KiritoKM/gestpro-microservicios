# Proyecto: Microservicios GestPro

Proyecto realizado para la asignatura de **Redes e Infraestructura** con el profesor **Walter**.

Este proyecto toma la base de la aplicación de ventas que teniamos como proyecto en conjunto pasado y la adapta a una arquitectura de microservicios distribuida, utilizando FastAPI para el backend, Nginx como proxy inverso y servidor web en el frontend, y automatización con Vagrant y Ansible.

## Arquitectura

El sistema está dividido en dos máquinas:

1. **Backend (`192.168.56.10`):**
   - **Microservicio de Usuarios (`service_users`):** Corre en el puerto `8001`. Maneja el login y los roles de usuario (`admin` y `vendedor`).
   - **Microservicio de Inventario (`service_inventory`):** Corre en el puerto `8002`. Maneja el catálogo de productos, categorías y stock.
   - **Microservicio de Analítica (`service_sales_analytics`):** Corre en el puerto `8003`. Procesa las ventas registradas y genera métricas (ingresos, costos, utilidades y gráficos).
   - Cada servicio tiene su propia base de datos y su propio servicio systemd (`gestpro-*.service`).

2. **Frontend (`192.168.56.20`):**
   - Servidor web **Nginx** en el puerto `80`.
   - Sirve la interfaz web (HTML, CSS y JS con Bootstrap y Chart.js).
   - Funciona como Proxy Inverso: redirige las peticiones `/api/users/`, `/api/inventory/` y `/api/analytics/` hacia la máquina de backend.

## Perfiles de Usuario

- **Gerente (Admin):** Puede ver los indicadores de ventas, utilidades, margen de la ganancia y gráficos de rendimiento mensuales, top de productos y métodos de pago.
- **Vendedor:** Permite buscar productos en tiempo real, filtrar por categoría y consultar precios y disponibilidad de stock.

## Estructura del proyecto

```text
├── Vagrantfile                       # Configuración de las 2 máquinas virtuales
├── ansible/
│   ├── backend.yml                   # Playbook para configurar el Backend
│   └── frontend.yml                  # Playbook para configurar el Frontend
├── backend/
│   ├── service_users/                # Servicio de usuarios (puerto 8001)
│   ├── service_inventory/            # Servicio de catálogo e inventario (puerto 8002)
│   ├── service_sales_analytics/      # Servicio de analítica y ventas (puerto 8003)
│   └── systemd/                      # Archivos de servicio para systemd
├── frontend/
│   ├── index.html                    # Página principal
│   ├── css/styles.css                # Estilos
│   ├── js/                           # Lógica del frontend y gráficos
│   └── nginx/gestpro.conf            # Configuración de Nginx
└── tests/                            # Pruebas unitarias de los servicios
```
