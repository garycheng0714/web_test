"""Turn designer output into claim and missing-requirement eval units."""

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum

from designer_eval.requirements import Requirement
from web_test.planning.schema import Case, DesignOutput


class UnitKind(StrEnum):
    CLAIM = "claim"
    REQUIREMENT = "requirement"


@dataclass(frozen=True)
class UnitSpec:
    kind: UnitKind
    target_id: str
    name: str
    attributes: dict[str, str]


@dataclass(frozen=True)
class EvalUnit:
    kind: UnitKind
    target_id: str
    span_id: str
    name: str
    attributes: dict[str, str]


def case_id(index: int) -> str:
    return f"case-{index}"


def case_fingerprint(case: Case) -> str:
    data = {
        "module_feature": case.module_feature,
        "test_scenario": case.test_scenario,
        "preconditions": [" ".join(item.split()) for item in case.preconditions],
        "steps": [
            {
                "action": " ".join(step.action.split()),
                "expected_result": " ".join(step.expected_result.split()),
            }
            for step in case.steps
        ],
    }
    encoded = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def duplicate_groups(design: DesignOutput) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for index, case in enumerate(design.cases, start=1):
        groups.setdefault(case_fingerprint(case), []).append(case_id(index))
    return {fingerprint: ids for fingerprint, ids in groups.items() if len(ids) > 1}


def plan_units(
    *,
    prd_name: str,
    design: DesignOutput,
    requirements: list[Requirement],
    run_id: str,
) -> list[UnitSpec]:
    """One claim per (requirement, case) pair, plus a span for each missing requirement."""
    by_id = {requirement.id: requirement for requirement in requirements}
    claimed_by: dict[str, list[str]] = {requirement.id: [] for requirement in requirements}
    units: list[UnitSpec] = []

    for index, case in enumerate(design.cases, start=1):
        cid = case_id(index)
        for requirement_id in dict.fromkeys(case.requirement_ids):
            requirement = by_id.get(requirement_id)
            if requirement is not None:
                claimed_by[requirement.id].append(cid)
            units.append(
                UnitSpec(
                    kind=UnitKind.CLAIM,
                    target_id=f"{requirement_id}<-{cid}",
                    name=f"claim {requirement_id} <- {cid}"
                    if requirement is not None
                    else f"claim {requirement_id} <- {cid} (invented)",
                    attributes={
                        "openinference.span.kind": "EVALUATOR",
                        "claim.requirement_id": requirement_id,
                        "claim.case_id": cid,
                        "claim.requirement_exists": "true" if requirement else "false",
                        "requirement.id": requirement_id,
                        "case.id": cid,
                        "input.value": requirement.text
                        if requirement is not None
                        else f"missing requirement id: {requirement_id}",
                        "output.value": case.model_dump_json(),
                        "designer.run.id": run_id,
                        "designer.prd": prd_name,
                    },
                )
            )

    for requirement in requirements:
        if claimed_by[requirement.id]:
            continue
        units.append(
            UnitSpec(
                kind=UnitKind.REQUIREMENT,
                target_id=requirement.id,
                name=f"requirement {requirement.id} (missing)",
                attributes={
                    "openinference.span.kind": "EVALUATOR",
                    "requirement.id": requirement.id,
                    "requirement.missing": "true",
                    "requirement.claimed_by": "[]",
                    "input.value": requirement.text,
                    "output.value": "[]",
                    "designer.run.id": run_id,
                    "designer.prd": prd_name,
                },
            )
        )

    return units
