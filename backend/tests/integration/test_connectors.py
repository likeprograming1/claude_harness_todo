import pytest

from httpx import AsyncClient

pytestmark = pytest.mark.asyncio(loop_scope="session")

BASE = "/api/v1/connectors"

CONN = {
    "connector_id": "J1",
    "manufacturer": "Molex",
    "pin_count": 4,
    "housing_type": "Rectangular",
    "gender": "male",
}

CONN_B = {**CONN, "connector_id": "J2", "gender": "female"}


async def _create(client: AsyncClient, payload: dict = CONN) -> dict:
    r = await client.post(BASE, json=payload)
    assert r.status_code == 201
    return r.json()


# ── happy paths ─────────────────────────────────────────────────────────────

async def test_create_connector_201(http_client: AsyncClient) -> None:
    data = await _create(http_client)
    assert data["connector_id"] == "J1"
    assert data["waterproof_status"] == "not_waterproof"
    assert data["id"] != ""


async def test_list_connectors_200(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.get(BASE)
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_get_connector_200(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.get(f"{BASE}/J1")
    assert r.status_code == 200
    assert r.json()["connector_id"] == "J1"


async def test_update_connector_200(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.put(f"{BASE}/J1", json={"pin_count": 8})
    assert r.status_code == 200
    assert r.json()["pin_count"] == 8


async def test_delete_connector_204(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.delete(f"{BASE}/J1")
    assert r.status_code == 204
    assert (await http_client.get(f"{BASE}/J1")).status_code == 404


# ── mate ─────────────────────────────────────────────────────────────────────

async def test_mate_connectors_200(http_client: AsyncClient) -> None:
    await _create(http_client, CONN)
    await _create(http_client, CONN_B)
    r = await http_client.post(f"{BASE}/J1/mate/J2")
    assert r.status_code == 200
    body = r.json()
    assert body["a"]["mating_connector_id"] == "J2"
    assert body["b"]["mating_connector_id"] == "J1"


async def test_mate_idempotent(http_client: AsyncClient) -> None:
    await _create(http_client, CONN)
    await _create(http_client, CONN_B)
    await http_client.post(f"{BASE}/J1/mate/J2")
    r = await http_client.post(f"{BASE}/J1/mate/J2")
    assert r.status_code == 200


async def test_mate_self_422(http_client: AsyncClient) -> None:
    await _create(http_client)
    r = await http_client.post(f"{BASE}/J1/mate/J1")
    assert r.status_code == 422


async def test_mate_already_mated_409(http_client: AsyncClient) -> None:
    conn_c = {**CONN, "connector_id": "J3"}
    await _create(http_client, CONN)
    await _create(http_client, CONN_B)
    await _create(http_client, conn_c)
    await http_client.post(f"{BASE}/J1/mate/J2")
    # J1 is already mated to J2 — mating with J3 should 409
    r = await http_client.post(f"{BASE}/J1/mate/J3")
    assert r.status_code == 409


# ── 404 ─────────────────────────────────────────────────────────────────────

async def test_get_connector_404(http_client: AsyncClient) -> None:
    assert (await http_client.get(f"{BASE}/NOPE")).status_code == 404


async def test_update_connector_404(http_client: AsyncClient) -> None:
    assert (await http_client.put(f"{BASE}/NOPE", json={"pin_count": 2})).status_code == 404


async def test_delete_connector_404(http_client: AsyncClient) -> None:
    assert (await http_client.delete(f"{BASE}/NOPE")).status_code == 404


async def test_mate_connector_a_404(http_client: AsyncClient) -> None:
    await _create(http_client, CONN_B)
    assert (await http_client.post(f"{BASE}/NOPE/mate/J2")).status_code == 404


async def test_mate_connector_b_404(http_client: AsyncClient) -> None:
    await _create(http_client)
    assert (await http_client.post(f"{BASE}/J1/mate/NOPE")).status_code == 404


# ── 409 / 422 ────────────────────────────────────────────────────────────────

async def test_create_connector_409_duplicate(http_client: AsyncClient) -> None:
    await _create(http_client)
    assert (await http_client.post(BASE, json=CONN)).status_code == 409


async def test_create_connector_422_pin_count_zero(http_client: AsyncClient) -> None:
    assert (await http_client.post(BASE, json={**CONN, "pin_count": 0})).status_code == 422


async def test_create_connector_422_pin_count_negative(http_client: AsyncClient) -> None:
    assert (await http_client.post(BASE, json={**CONN, "pin_count": -1})).status_code == 422
