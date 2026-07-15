from __future__ import annotations

import json

import aiosqlite
from db import get_db
from fastapi import APIRouter, Depends
from models import RtoPilotDetail, RtoPilotRef, RtoPilotRequirements, RtoPilotTag

router = APIRouter(prefix="/api/v1", tags=["rto-pilots"])


def _row_to_detail(row) -> RtoPilotDetail:
    tags_raw = json.loads(row["tags_json"] or "[]")
    req_raw = json.loads(row["requirements_json"]) if row["requirements_json"] else None

    requirements = None
    if req_raw:
        requirements = RtoPilotRequirements(
            hiring_requirements=req_raw.get("hiring_requirements", []),
            hiring_visibility_requirements=req_raw.get("hiring_visibility_requirements", []),
            required_system_owner=req_raw.get("required_system_owner", []),
            required_system_core_ids=req_raw.get("required_system_core_ids", []),
            required_pilot_ids=[RtoPilotRef(**r) for r in req_raw.get("required_pilot_ids", [])],
            conflicting_pilot_ids=[RtoPilotRef(**r) for r in req_raw.get("conflicting_pilot_ids", [])],
        )

    return RtoPilotDetail(
        id=row["id"],
        ui_name=row["ui_name"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        callsign=row["callsign"],
        gender=row["gender"],
        faction=row["faction"],
        age=row["age"],
        details=row["details"],
        icon=row["icon"],
        can_pilot=json.loads(row["can_pilot_json"] or "[]"),
        tags=[RtoPilotTag(**t) for t in tags_raw],
        requirements=requirements,
        source_mod=row["source_mod"],
    )


@router.get("/rto-pilots", response_model=list[RtoPilotDetail])
async def list_rto_pilots(db: aiosqlite.Connection = Depends(get_db)) -> list[RtoPilotDetail]:
    async with db.execute("SELECT * FROM rto_pilot ORDER BY ui_name ASC") as cur:
        rows = await cur.fetchall()
    return [_row_to_detail(r) for r in rows]
