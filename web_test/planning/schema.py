from enum import StrEnum

from pydantic import BaseModel


class Priority(StrEnum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Severity(StrEnum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"
    TRIVIAL = "Trivial"


class CaseType(StrEnum):
    FUNCTIONAL = "Functional"
    NEGATIVE = "Negative"
    BOUNDARY = "Boundary"
    VALIDATION = "Validation"
    UI = "UI"
    PERMISSION = "Permission"
    WORKFLOW = "Workflow"
    INTEGRATION = "Integration"
    REGRESSION = "Regression"
    USABILITY = "Usability"
    DATA_PERSISTENCE = "DataPersistence"


class CaseStatus(StrEnum):
    NOT_RUN = "NotRun"
    PASS = "Pass"
    FAIL = "Fail"
    BLOCKED = "Blocked"


class Case(BaseModel):
    test_case_id: str
    requirement_ids: list[str]
    module_feature: str
    test_scenario: str
    preconditions: list[str]
    test_steps: list[str]
    test_data: str | None = None
    expected_result: str
    priority: Priority
    severity: Severity
    test_type: CaseType
    status: CaseStatus = CaseStatus.NOT_RUN
    notes: str = ""


class QaReport(BaseModel):
    requirement_summary: list[str]
    coverage_areas: list[str]
    assumptions: list[str]
    clarifications_needed: list[str]
    test_cases: list[Case]
    missing_unclear_requirements: list[str]
    suggested_improvements: list[str]
