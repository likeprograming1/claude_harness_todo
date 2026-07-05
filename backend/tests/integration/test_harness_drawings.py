import pytest

from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

WIRES_BASE = "/api/v1/wires"
CONN_BASE = "/api/v1/connectors"
BASE = "/api/v1/harness/drawings"

WIRE = {"wire_id": "W001", "gauge_awg": 14, "material": "copper",
        "color": "red", "length_mm": 500.0, "insulation_rating_v": 600.0}
CONN_A = {"connector_id": "J1", "manufacturer": "AMP", "pin_count": 4,
           "housing_type": "Rectangular", "gender": "male"}
CONN_B = {"connector_id": "J2", "manufacturer": "AMP", "pin_count": 4,
           "housing_type": "Rectangular", "gender": "female"}

CIRCUIT = {
    "circuit_id": "C1",
    "from_connector_id": "J1", "from_connector_pin": 1,
    "to_connector_id": "J2", "to_connector_pin": 1,
    "wire_id": "W001", "signal_name": "IGN",
}

DRAWING = {
    "drawing_id": "D001",
    "revision": "Rev.A",
    "title": "Main Harness",
    "wire_ids": ["W001"],
    "connector_ids": ["J1", "J2"],
    "circuits": [CIRCUIT],
}


async def _seed(client: AsyncClient) -> None:
    """Insert prerequisite wire and connectors."""
    assert (await client.post(WIRES_BASE, json=WIRE)).status_code == 201
    assert (await client.post(CONN_BASE, json=CONN_A)).status_code == 201
    assert (await client.post(CONN_BASE, json=CONN_B)).status_code == 201


async def _create(client: AsyncClient) -> dict:
    await _seed(client)
    r = await client.post(BASE, json=DRAWING)
    assert r.status_code == 201
    return r.json()


# ── happy paths ─────────────────────────────────────────────────────────────

async def test_create_drawing_201(http_client: AsyncClient) -> None:
    data = await _create(http_client)
    assert data["drawing_id"] == "D001"
    assert data["revision"] == "Rev.A"
    assert len(data["circuits"]) == 1


async def test_list_drawings_200(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.get(BASE)
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_get_drawing_200(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.get(f"{BASE}/D001")
    assert r.status_code == 200
    assert r.json()["drawing_id"] == "D001"


async def test_update_drawing_200(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.put(f"{BASE}/D001", json={"title": "Updated Harness"})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Updated Harness"


async def test_update_drawing_auto_bumps_revision(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.put(f"{BASE}/D001", json={"title": "Rev bump"})
    assert r.status_code == 200
    assert r.json()["revision"] == "Rev.B"


async def test_update_drawing_explicit_revision(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.put(f"{BASE}/D001", json={"revision": "Rev.Z", "title": "X"})
    assert r.status_code == 200
    assert r.json()["revision"] == "Rev.Z"


async def test_delete_drawing_204(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.delete(f"{BASE}/D001")
    assert r.status_code == 204
    assert (await http_client.get(f"{BASE}/D001")).status_code == 404


# ── validate endpoint ────────────────────────────────────────────────────────

async def test_validate_drawing_valid(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.post(f"{BASE}/D001/validate")
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is True
    assert body["errors"] == []


async def test_validate_drawing_pin_out_of_bounds(http_client: AsyncClient) -> None:
    await _seed(http_client)
    bad_circuit = {**CIRCUIT, "from_connector_pin": 99}
    drawing = {**DRAWING, "circuits": [bad_circuit]}
    assert (await http_client.post(BASE, json=drawing)).status_code == 201
    r = await http_client.post(f"{BASE}/D001/validate")
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is False
    assert any("from_connector_pin" in e for e in body["errors"])


async def test_validate_drawing_duplicate_pin_assignment(http_client: AsyncClient) -> None:
    await _seed(http_client)
    c2 = {**CIRCUIT, "circuit_id": "C2", "to_connector_pin": 1}  # same J2 pin 1
    drawing = {**DRAWING, "circuits": [CIRCUIT, c2]}
    assert (await http_client.post(BASE, json=drawing)).status_code == 201
    r = await http_client.post(f"{BASE}/D001/validate")
    assert r.status_code == 200
    assert r.json()["valid"] is False


# ── 404 ─────────────────────────────────────────────────────────────────────

async def test_get_drawing_404(http_client: AsyncClient) -> None:
    assert (await http_client.get(f"{BASE}/NOPE")).status_code == 404


async def test_update_drawing_404(http_client: AsyncClient) -> None:
    assert (await http_client.put(f"{BASE}/NOPE", json={"title": "X"})).status_code == 404


async def test_delete_drawing_404(http_client: AsyncClient) -> None:
    assert (await http_client.delete(f"{BASE}/NOPE")).status_code == 404


async def test_validate_drawing_404(http_client: AsyncClient) -> None:
    assert (await http_client.post(f"{BASE}/NOPE/validate")).status_code == 404


# ── 409 conflict ────────────────────────────────────────────────────────────

async def test_create_drawing_409_duplicate(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.post(BASE, json=DRAWING)
    assert r.status_code == 409


# ── 422 validation ───────────────────────────────────────────────────────────

async def test_create_drawing_422_invalid_revision(http_client: AsyncClient) -> None:
    await _seed(http_client)
    r = await http_client.post(BASE, json={**DRAWING, "revision": "RevA"})
    assert r.status_code == 422


async def test_create_drawing_422_duplicate_circuit_id(http_client: AsyncClient) -> None:
    await _seed(http_client)
    dup = {**CIRCUIT, "from_connector_pin": 2}  # same circuit_id "C1"
    r = await http_client.post(BASE, json={**DRAWING, "circuits": [CIRCUIT, dup]})
    assert r.status_code == 422


async def test_create_drawing_422_missing_wire_ref(http_client: AsyncClient) -> None:
    await _seed(http_client)
    r = await http_client.post(BASE, json={**DRAWING, "wire_ids": ["W_GHOST"]})
    assert r.status_code == 422


async def test_create_drawing_422_missing_connector_ref(http_client: AsyncClient) -> None:
    await _seed(http_client)
    bad_circuit = {**CIRCUIT, "from_connector_id": "J_GHOST"}
    r = await http_client.post(BASE, json={**DRAWING, "circuits": [bad_circuit]})
    assert r.status_code == 422


async def test_update_drawing_422_revision_past_z(http_client: AsyncClient) -> None:
    await _create(http_client)
    # Bump to Rev.Z explicitly
    await http_client.put(f"{BASE}/D001", json={"revision": "Rev.Z", "title": "X"})
    # Next auto-bump should 422
    r = await http_client.put(f"{BASE}/D001", json={"title": "Y"})
    assert r.status_code == 422
