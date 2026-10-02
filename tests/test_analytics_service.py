import pytest
from fastapi.testclient import TestClient
from conftest import load_microservice

analytics_module = load_microservice("service_sales_analytics", "analytics_app_module")
client = TestClient(analytics_module.app)


def setup_module():
    analytics_module.init_db()


def test_analytics_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "sales_and_analytics"
    assert data["status"] == "ok"
    assert data["port"] == 8003


def test_get_kpis():
    response = client.get("/analytics/kpis")
    assert response.status_code == 200
    kpis = response.json()
    assert kpis["total_sales"] > 0
    assert kpis["total_revenue"] > 0
    assert kpis["total_cost"] > 0
    assert kpis["net_profit"] > 0
    assert kpis["profit_margin_pct"] > 0
    assert kpis["avg_ticket"] > 0
    expected_profit = round(kpis["total_revenue"] - kpis["total_cost"], 2)
    assert abs(kpis["net_profit"] - expected_profit) < 1.0


def test_get_sales_trend():
    response = client.get("/analytics/sales-trend")
    assert response.status_code == 200
    trend = response.json()
    assert isinstance(trend, list)
    assert len(trend) >= 3
    for entry in trend:
        assert "month" in entry
        assert "revenue" in entry
        assert "profit" in entry


def test_get_top_products():
    response = client.get("/analytics/top-products?limit=5")
    assert response.status_code == 200
    top = response.json()
    assert isinstance(top, list)
    assert len(top) <= 5
    assert len(top) > 0
    assert "product_name" in top[0]
    assert "total_revenue" in top[0]


def test_get_sales_by_category():
    response = client.get("/analytics/by-category")
    assert response.status_code == 200
    by_cat = response.json()
    assert isinstance(by_cat, list)
    assert len(by_cat) >= 3


def test_get_sales_by_payment_method():
    response = client.get("/analytics/by-payment-method")
    assert response.status_code == 200
    methods = response.json()
    assert isinstance(methods, list)
    assert len(methods) >= 2


def test_get_recent_sales():
    response = client.get("/analytics/recent-sales?limit=10")
    assert response.status_code == 200
    sales = response.json()
    assert isinstance(sales, list)
    assert len(sales) <= 10
    if len(sales) > 0:
        assert "invoice_code" in sales[0]
        assert "items" in sales[0]
