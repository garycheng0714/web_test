"""Turn designer output into requirement and claim eval units."""

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum

from pydantic import BaseModel

from evals.designer.designer_eval.requirements import Requirement
from web_test.planning.cases_writer import render_case_section
from web_test.planning.schema import Case, CaseType, DesignOutput

_PARENT_REQUIREMENT = re.compile(r"^(FR-[A-Z]+-\d+)(?:-AC\d+)?$")


class UnitKind(StrEnum):
    REQUIREMENT = "requirement"
    CLAIM = "claim"


@dataclass(frozen=True)
class UnitSpec:
    kind: UnitKind
    target_id: str
    name: str
    attributes: dict[str, str]
    parent_target_id: str | None = None


@dataclass(frozen=True)
class EvalUnit:
    kind: UnitKind
    target_id: str
    span_id: str
    name: str
    attributes: dict[str, str]
    parent_span_id: str | None = None


class RunFindings(BaseModel):
    """IDs and case ids the run could not turn into claims."""

    non_requirement_ids: dict[str, list[str]] = {}
    invalid_requirement_ids: dict[str, list[str]] = {}
    multi_requirement_cases: list[str] = []


@dataclass(frozen=True)
class PlanResult:
    units: list[UnitSpec]
    findings: RunFindings


def test_type_slug(test_type: CaseType) -> str:
    value = test_type.value
    return "data-persistence" if value == "DataPersistence" else value.lower()


def case_id(index: int, test_type: CaseType) -> str:
    return f"case-{index}-{test_type_slug(test_type)}"


def normalize_requirement_id(requirement_id: str) -> str:
    """Map derived AC ids such as FR-ACC-04-AC1 back to the PRD's parent id."""
    match = _PARENT_REQUIREMENT.match(requirement_id)
    return match.group(1) if match else requirement_id


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
        groups.setdefault(case_fingerprint(case), []).append(case_id(index, case.test_type))
    return {fingerprint: ids for fingerprint, ids in groups.items() if len(ids) > 1}


def _classify_ids(
    case: Case, by_id: dict[str, Requirement]
) -> tuple[dict[str, list[str]], list[str], list[str]]:
    """Split a case's requirement ids into valid parents, unknown FRs, and non-FR ids."""
    raw_by_parent: dict[str, list[str]] = {}
    invalid: list[str] = []
    non_requirement: list[str] = []
    for raw_id in case.requirement_ids:
        parent_id = normalize_requirement_id(raw_id)
        if parent_id in by_id:
            raw_by_parent.setdefault(parent_id, [])
            if raw_id not in raw_by_parent[parent_id]:
                raw_by_parent[parent_id].append(raw_id)
        elif raw_id.startswith("FR-"):
            if raw_id not in invalid:
                invalid.append(raw_id)
        elif raw_id not in non_requirement:
            non_requirement.append(raw_id)
    return raw_by_parent, invalid, non_requirement


def _claim_spec(
    *,
    case: Case,
    index: int,
    cid: str,
    requirement: Requirement,
    raw_ids: list[str],
    multi_requirement: bool,
    run_id: str,
    prd_name: str,
) -> UnitSpec:
    return UnitSpec(
        kind=UnitKind.CLAIM,
        target_id=f"{cid}->{requirement.id}",
        name=f"claim {cid} -> {requirement.id}",
        parent_target_id=requirement.id,
        attributes={
            "openinference.span.kind": "EVALUATOR",
            "claim.requirement_id": requirement.id,
            "claim.requirement_raw_ids": json.dumps(raw_ids, ensure_ascii=False),
            "claim.case_id": cid,
            "claim.case_index": str(index),
            "claim.multi_requirement_case": "true" if multi_requirement else "false",
            "case.test_type": case.test_type.value,
            "requirement.id": requirement.id,
            "case.id": cid,
            "input.value": requirement.text,
            "input.mime_type": "text/markdown",
            "output.value": render_case_section(case, index=index),
            "output.mime_type": "text/markdown",
            "designer.run.id": run_id,
            "designer.prd": prd_name,
        },
    )


def _requirement_spec(
    requirement: Requirement, case_ids: list[str], *, run_id: str, prd_name: str
) -> UnitSpec:
    missing = not case_ids
    return UnitSpec(
        kind=UnitKind.REQUIREMENT,
        target_id=requirement.id,
        name=f"requirement {requirement.id}" + (" (missing)" if missing else ""),
        attributes={
            "openinference.span.kind": "EVALUATOR",
            "requirement.id": requirement.id,
            "requirement.missing": "true" if missing else "false",
            "requirement.claim_count": str(len(case_ids)),
            "requirement.claimed_by": json.dumps(case_ids, ensure_ascii=False),
            "input.value": requirement.text,
            "input.mime_type": "text/markdown",
            "output.value": "\n".join(f"- {cid}" for cid in case_ids) or "(no claims)",
            "output.mime_type": "text/markdown",
            "designer.run.id": run_id,
            "designer.prd": prd_name,
        },
    )


def plan_units(
    *,
    prd_name: str,
    design: DesignOutput,
    requirements: list[Requirement],
    run_id: str,
) -> PlanResult:
    """Build one requirement span per PRD requirement and one claim per case x valid FR."""
    by_id = {requirement.id: requirement for requirement in requirements}
    claimed_by: dict[str, list[str]] = {requirement.id: [] for requirement in requirements}
    claim_specs: list[UnitSpec] = []
    findings = RunFindings()

    for index, case in enumerate(design.cases, start=1):
        cid = case_id(index, case.test_type)
        raw_by_parent, invalid, non_requirement = _classify_ids(case, by_id)
        if invalid:
            findings.invalid_requirement_ids[cid] = invalid
        if non_requirement:
            findings.non_requirement_ids[cid] = non_requirement
        multi_requirement = len(raw_by_parent) > 1
        if multi_requirement:
            findings.multi_requirement_cases.append(cid)
        for requirement_id, raw_ids in raw_by_parent.items():
            claimed_by[requirement_id].append(cid)
            claim_specs.append(
                _claim_spec(
                    case=case,
                    index=index,
                    cid=cid,
                    requirement=by_id[requirement_id],
                    raw_ids=raw_ids,
                    multi_requirement=multi_requirement,
                    run_id=run_id,
                    prd_name=prd_name,
                )
            )

    requirement_specs = [
        _requirement_spec(
            requirement,
            claimed_by[requirement.id],
            run_id=run_id,
            prd_name=prd_name,
        )
        for requirement in requirements
    ]
    return PlanResult(units=requirement_specs + claim_specs, findings=findings)
