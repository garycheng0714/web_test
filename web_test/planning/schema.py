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


class Step(BaseModel):
    action: str
    expected_result: str


class Case(BaseModel):
    requirement_ids: list[str]
    module_feature: str
    test_scenario: str
    preconditions: list[str] = []
    steps: list[Step]
    priority: Priority
    severity: Severity
    test_type: CaseType
    notes: str = ""
