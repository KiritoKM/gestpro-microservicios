import pytest
from fastapi.testclient import TestClient
from conftest import load_microservice

users_module = load_microservice("service_users", "int_users_module")
inventory_module = load_microservice("service_inventory", "int_inventory_module")
analytics_module = load_microservice("service_sales_analytics", "int_analytics_module")


@pytest.fixture(scope="module")
def clients():
    users_module.init_db()
    inventory_module.init_db()
    analytics_module.init_db()

    return {
        "users": TestClient(users_module.app),
        "inventory": TestClient(inventory_module.app),
        "analytics": TestClient(analytics_module.app),
    }


def test_cross_service_health(clients):
    """Verifica que los tres microservicios responden health check correctamente"""
    res_users = clients["users"].get("/health")
    res_inv = clients["inventory"].get("/health")
    res_ana = clients["analytics"].get("/health")

    assert res_users.status_code == 200
    assert res_inv.status_code == 200
    assert res_ana.status_code == 200

    assert res_users.json()["status"] == "ok"
    assert res_inv.json()["status"] == "ok"
    assert res_ana.json()["status"] == "ok"


def test_cross_service_catalog_and_analytics_consistency(clients):
    """Verifica que las categorías analizadas en ventas correspondan con las categorías del inventario"""
    res_inv = clients["inventory"].get("/inventory/categories")
    assert res_inv.status_code == 200
    inv_categories = res_inv.json()
    category_names = {c["name"] for c in inv_categories}

    res_ana = clients["analytics"].get("/analytics/by-category")
    assert res_ana.status_code == 200
    analytics_categories = res_ana.json()
    for cat in analytics_categories:
        assert cat["category_name"] in category_names, f"Categoría {cat['category_name']} no existe en inventario"


def test_user_roles_authorization_flow(clients):
    """Verifica que el flujo de login otorgue perfiles coherentes para acceder a datos"""
    # Login como gerente
    res_admin = clients["users"].post("/users/login", json={"username": "admin"}).json()
    assert "user" in res_admin
    assert res_admin["user"]["role"] == "admin"

    # Acceso a analítica financiera
    kpis = clients["analytics"].get("/analytics/kpis").json()
    assert kpis["total_revenue"] > 0

    # Login como cajero
    res_vendedor = clients["users"].post("/users/login", json={"username": "cajero1"}).json()
    assert "user" in res_vendedor
    assert res_vendedor["user"]["role"] == "vendedor"

    # Cajero consulta inventario y disponibilidad
    products = clients["inventory"].get("/inventory/products").json()
    assert len(products) > 0
