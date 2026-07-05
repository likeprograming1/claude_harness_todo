import pytest

from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

BASE = "/api/v1/wires"

WIRE = {
    "wire_id": "W001",
    "gauge_awg": 14,
    "material": "copper",
    "color": "red",
    "length_mm": 500.0,
    "insulation_rating_v": 600.0,
}


async def _create(client: AsyncClient, payload: dict = WIRE) -> dict:
    r = await client.post(BASE, json=payload)
    assert r.status_code == 201
    return r.json()


# ── happy paths ─────────────────────────────────────────────────────────────

async def test_create_wire_201(http_client: AsyncClient) -> None:
    data = await _create(http_client)
    assert data["wire_id"] == "W001"
    assert data["max_current_a"] == 15.0
    assert data["id"] != ""


async def test_list_wires_200(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.get(BASE)
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_get_wire_200(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.get(f"{BASE}/W001")
    assert r.status_code == 200
    assert r.json()["wire_id"] == "W001"


async def test_update_wire_200(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.put(f"{BASE}/W001", json={"color": "blue"})
    assert r.status_code == 200
    assert r.json()["color"] == "blue"


async def test_update_wire_gauge_recalculates_max_current(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.put(f"{BASE}/W001", json={"gauge_awg": 10})
    assert r.status_code == 200
    assert r.json()["max_current_a"] == 30.0


async def test_delete_wire_204(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.delete(f"{BASE}/W001")
    assert r.status_code == 204
    r2 = await http_client.get(f"{BASE}/W001")
    assert r2.status_code == 404


# ── 404 ─────────────────────────────────────────────────────────────────────

async def test_get_wire_404(http_client: AsyncClient) -> None:
    r = await http_client.get(f"{BASE}/NOPE")
    assert r.status_code == 404


async def test_update_wire_404(http_client: AsyncClient) -> None:
    r = await http_client.put(f"{BASE}/NOPE", json={"color": "blue"})
    assert r.status_code == 404


async def test_delete_wire_404(http_client: AsyncClient) -> None:
    r = await http_client.delete(f"{BASE}/NOPE")
    assert r.status_code == 404


# ── 409 conflict ────────────────────────────────────────────────────────────

async def test_create_wire_409_duplicate(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.post(BASE, json=WIRE)
    assert r.status_code == 409


async def test_delete_wire_409_referenced_by_drawing(http_client: AsyncClient) -> None:
    await _create(http_client)
    conn = {"connector_id": "J1", "manufacturer": "AMP", "pin_count": 4,
            "housing_type": "Rectangular", "gender": "male"}
    await http_client.post("/api/v1/connectors", json=conn)
    drawing = {
        "drawing_id": "D001", "revision": "Rev.A", "title": "Test",
        "wire_ids": ["W001"], "connector_ids": ["J1"], "circuits": [],
    }
    r = await http_client.post("/api/v1/harness/drawings", json=drawing)
    assert r.status_code == 201
    r = await http_client.delete(f"{BASE}/W001")
    assert r.status_code == 409


# ── 422 validation ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("gauge", [1, 3, 99])
async def test_create_wire_422_invalid_awg(http_client: AsyncClient, gauge: int) -> None:
    payload = {**WIRE, "gauge_awg": gauge}
    r = await http_client.post(BASE, json=payload)
    assert r.status_code == 422


async def test_create_wire_422_insulation_zero(http_client: AsyncClient) -> None:
    r = await http_client.post(BASE, json={**WIRE, "insulation_rating_v": 0})
    assert r.status_code == 422


async def test_create_wire_422_insulation_negative(http_client: AsyncClient) -> None:
    r = await http_client.post(BASE, json={**WIRE, "insulation_rating_v": -5})
    assert r.status_code == 422
