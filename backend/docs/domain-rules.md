# Harness Engineering — Domain Rules

## Wire

### AWG Gauge
- Valid gauges (16 values): `0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30`
- Any value outside this set → 422 Unprocessable Entity
- When `gauge_awg` changes, `max_current_a` must be recomputed from the SAE ampacity table and persisted

### SAE Chassis-Wiring Ampacity Table
| AWG | max_current_a |
|-----|--------------|
| 0   | 245.0 A      |
| 2   | 185.0 A      |
| 4   | 125.0 A      |
| 6   | 80.0 A       |
| 8   | 55.0 A       |
| 10  | 30.0 A       |
| 12  | 20.0 A       |
| 14  | 15.0 A       |
| 16  | 13.0 A       |
| 18  | 10.0 A       |
| 20  | 5.0 A        |
| 22  | 3.0 A        |
| 24  | 2.0 A        |
| 26  | 1.0 A        |
| 28  | 0.5 A        |
| 30  | 0.3 A        |

### Insulation Voltage Rating
- `insulation_rating_v > 0` required (422 if violated)
- Values below 12 V emit a `logger.warning` — they are accepted, not rejected

### Wire Material
- Allowed values: `copper`, `aluminum`, `copper_clad_aluminum`

### Wire Deletion Constraint
- A wire referenced in any `HarnessDrawing.wire_ids` cannot be deleted → 409 Conflict

---

## Connector

### Pin Count
- `pin_count > 0` required (422 if violated)

### Gender
- Allowed values: `male`, `female`, `neutral`

### Waterproof Status
- Allowed values: `not_waterproof`, `IP54`, `IP67`, `IP68`
- Default: `not_waterproof`

### Mating Connector (symmetric link)
- `POST /connectors/{a_id}/mate/{b_id}` sets A→B and B→A simultaneously in a single atomic update
- If either connector is already mated to a different connector → 409 Conflict
- `a_id == b_id` (self-mating) → 422

---

## Harness Drawing

### Revision Format
- Pattern: `^Rev\.[A-Z]$` (examples: `Rev.A`, `Rev.B`, …, `Rev.Z`)
- Format violation → 422
- On `PUT` without an explicit revision, the current letter is auto-bumped one step (e.g. `Rev.A` → `Rev.B`); bumping past `Rev.Z` → 422

### Duplicate circuit_id
- `circuit_id` values must be unique within a drawing
- Enforced at the schema level (`model_validator`) → 422

### Referential Integrity
All of the following IDs must exist in the database before a drawing is saved or updated:

| Field | Must exist in |
|-------|--------------|
| `wire_ids[]` | `wires` collection |
| `connector_ids[]` | `connectors` collection |
| `circuit.wire_id` | `wires` collection |
| `circuit.from_connector_id` | `connectors` collection |
| `circuit.to_connector_id` | `connectors` collection |

Violation → `HarnessValidationError` (422)

---

## Validation Report (`POST /harness/drawings/{id}/validate`)

`ValidationReport` fields: `drawing_id`, `valid: bool`, `errors: list[str]`, `warnings: list[str]`

### Validation checks (in order)
1. **Reference existence** — every `wire_id` and `connector_id` referenced in the drawing (top-level lists and inside circuits) exists in the DB
2. **Pin number bounds** — `from_connector_pin` and `to_connector_pin` of each circuit are within `1..connector.pin_count` (1-indexed)
3. **Duplicate circuit_id** — no two circuits in the drawing share the same `circuit_id`
4. **Duplicate pin assignment** — no two circuits connect to the same pin of the same connector (e.g. two circuits both using J1 pin 3 is invalid)

All checks pass → `{ "valid": true, "errors": [], "warnings": [] }`
Any check fails → `{ "valid": false, "errors": ["..."] }`
