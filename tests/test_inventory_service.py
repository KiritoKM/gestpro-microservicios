import pytest
from fastapi.testclient import TestClient
from conftest import load_microservice

inventory_module = load_microservice("service_inventory", "inventory_app_module")
client = TestClient(inventory_module.app)


def setup_module():
    inventory_module.init_db()


def test_inventory_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "inventory_and_catalog"
    assert data["status"] == "ok"
    assert data["port"] == 8002


def test_get_categories():
    response = client.get("/inventory/categories")
    assert response.status_code == 200
    cats = response.json()
    assert isinstance(cats, list)
    assert len(cats) >= 5
    names = [c["name"] for c in cats]
    assert "Tecnología" in names
    assert "Audio" in names


def test_get_products_list():
    response = client.get("/inventory/products")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list)
    assert len(products) >= 10


def test_search_products_by_name():
    response = client.get("/inventory/products?search=Lenovo")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 1
    assert "Lenovo" in products[0]["name"]


def test_filter_products_by_category():
    response = client.get("/inventory/products?category_id=1")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 1
    for p in products:
        assert p["category_id"] == 1


def test_low_stock_endpoint():
    response = client.get("/inventory/low-stock")
    assert response.status_code == 200
    low_stock = response.json()
    assert isinstance(low_stock, list)
    for p in low_stock:
        assert p["stock"] <= p["min_stock"]


def test_inventory_stats():
    response = client.get("/inventory/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_products"] > 0
    assert stats["total_units"] > 0
    assert stats["total_inventory_cost"] > 0
    assert stats["total_inventory_retail_value"] > stats["total_inventory_cost"]
