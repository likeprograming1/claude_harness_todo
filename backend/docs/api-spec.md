# API Specification — Harness Engineering API

Base path: `/api/v1`
Content-Type: `application/json`

---

## Wire — `/api/v1/wires`

### `GET /wires`
Returns the full list of wires.

**Response 200**
```json
[{
  "id": "64abc...",
  "wire_id": "W001",
  "gauge_awg": 14,
  "material": "copper",
  "color": "red",
  "length_mm": 500.0,
  "insulation_rating_v": 600.0,
  "max_current_a": 15.0
}]
```

### `GET /wires/{wire_id}`
**Response 200** — WireResponse
**Response 404** — `{ "detail": "Wire 'W001' not found" }`

### `POST /wires`
Create a new wire.

**Request body** — WireCreate
**Response 201** — WireResponse
**Response 409** — Duplicate `wire_id`
**Response 422** — Invalid AWG gauge or `insulation_rating_v <= 0`

### `PUT /wires/{wire_id}`
Partial update — only provided fields are changed.

**Request body** — WireUpdate
**Response 200** — WireResponse
**Response 404** — `wire_id` not found

### `DELETE /wires/{wire_id}`
**Response 204** — Deleted (no body)
**Response 404** — `wire_id` not found
**Response 409** — Wire is referenced by one or more harness drawings

---

## Connector — `/api/v1/connectors`

### `GET /connectors`
**Response 200** — `list[ConnectorResponse]`

### `GET /connectors/{connector_id}`
**Response 200** — ConnectorResponse
**Response 404**

### `POST /connectors`
**Request body** — ConnectorCreate
**Response 201** — ConnectorResponse
**Response 409** — Duplicate `connector_id`
**Response 422** — `pin_count <= 0`

### `PUT /connectors/{connector_id}`
**Request body** — ConnectorUpdate
**Response 200** — ConnectorResponse
**Response 404**

### `DELETE /connectors/{connector_id}`
**Response 204** — Deleted (no body)
**Response 404**

### `POST /connectors/{a_id}/mate/{b_id}`
Link two connectors as a symmetric mating pair (A→B and B→A set simultaneously).

**Response 200**
```json
{
  "a": { ...ConnectorResponse },
  "b": { ...ConnectorResponse }
}
```
**Response 404** — `a_id` or `b_id` not found
**Response 409** — Either connector is already mated to a different connector
**Response 422** — `a_id == b_id` (self-mating not allowed)

---

## Harness Drawing — `/api/v1/harness/drawings`

### `GET /harness/drawings`
**Response 200** — `list[HarnessDrawingResponse]`

### `GET /harness/drawings/{drawing_id}`
**Response 200** — HarnessDrawingResponse
**Response 404**

### `POST /harness/drawings`
**Request body** — HarnessDrawingCreate
**Response 201** — HarnessDrawingResponse
**Response 409** — Duplicate `drawing_id`
**Response 422** — Invalid revision format, duplicate `circuit_id`, referential integrity violation

### `PUT /harness/drawings/{drawing_id}`
If `revision` is omitted, the current revision letter is auto-bumped (e.g. `Rev.A` → `Rev.B`).

**Request body** — HarnessDrawingUpdate
**Response 200** — HarnessDrawingResponse
**Response 404**
**Response 422** — Referential integrity violation, or revision is already `Rev.Z` (cannot bump further)

### `DELETE /harness/drawings/{drawing_id}`
**Response 204** — Deleted (no body)
**Response 404**

### `POST /harness/drawings/{drawing_id}/validate`
Full validation of a drawing — non-destructive, no DB writes.

**Response 200** — ValidationReport (always 200; check `valid` field for result)

```json
{ "drawing_id": "D001", "valid": true, "errors": [], "warnings": [] }
```
```json
{
  "drawing_id": "D001",
  "valid": false,
  "errors": ["Circuit C3: from_connector_pin 5 exceeds J2 pin_count 4"],
  "warnings": []
}
```

---

## Health

### `GET /health`
**Response 200** — `{ "status": "ok" }`

---

## Common Error Formats

| Status | Meaning | Trigger |
|--------|---------|---------|
| 422 | Unprocessable Entity | Pydantic validation failure, business rule violation |
| 404 | Not Found | Entity does not exist |
| 409 | Conflict | Duplicate creation, deletion blocked by reference |
