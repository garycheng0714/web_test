from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class VerificationStatus(StrEnum):
    PASS = "PASS"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


class CheckDimension(StrEnum):
    """The quality dimension a review question checks."""

    AC_ALIGNMENT = "AC alignment"
    STEP_REASONABLE = "reasonable"
    STEP_CONTINUITY = "continuity"
    STEP_OBSERVABLE = "observable"


_RANK = {
    VerificationStatus.PASS: 0,
    VerificationStatus.NEEDS_REVIEW: 1,
    VerificationStatus.BLOCKED: 2,
    VerificationStatus.FAIL: 3,
}


@dataclass(frozen=True)
class Bands:
    """The probability bands that turn one Jev answer into a verification status."""

    pass_min: float = 0.8
    needs_review_min: float = 0.5

    def classify(self, probability: float | None) -> VerificationStatus:
        if probability is None:
            return VerificationStatus.BLOCKED
        if probability >= self.pass_min:
            return VerificationStatus.PASS
        if probability >= self.needs_review_min:
            return VerificationStatus.NEEDS_REVIEW
        return VerificationStatus.FAIL


@dataclass(frozen=True)
class CheckOutcome:
    """One Jev question and the status its probability produced."""

    question_id: str
    label: str
    dimension: CheckDimension
    probability: float | None
    status: VerificationStatus


@dataclass(frozen=True)
class DeterministicOutcome:
    """One structural check that needs no model judgment."""

    check_id: str
    label: str
    status: VerificationStatus
    detail: str = ""

    def __post_init__(self) -> None:
        if self.status not in (VerificationStatus.PASS, VerificationStatus.FAIL):
            raise ValueError("a deterministic outcome is PASS or FAIL")


@dataclass(frozen=True)
class UnitOutcome:
    """The aggregated status for one step or one case."""

    key: str
    label: str
    status: VerificationStatus


@dataclass(frozen=True)
class Override:
    """A human adjudication recorded against the status it replaced."""

    original: VerificationStatus
    reason: str
    head_sha: str | None = None


@dataclass(frozen=True)
class VerificationResult:
    """The review's verdict and the per-unit evidence behind it."""

    status: VerificationStatus          # 檔案層級：Jev + structure 聚合後的最終結果
    checks: tuple[CheckOutcome, ...]    # 每個預期 Jev 問題的結果；缺答案為 BLOCKED
    steps: tuple[UnitOutcome, ...]      # 每個 step 的聚合結果
    cases: tuple[UnitOutcome, ...]      # 每個 case 的聚合結果
    structure: tuple[DeterministicOutcome, ...] = ()  # 不用 Jev 的結構檢查
    jev_status: VerificationStatus | None = None      # 只看 Jev 的結果；結構檢查前
    blocked_reason: str | None = None   # 整份無法判斷的原因；部分缺答案時為 None
    override: Override | None = None    # 人工裁決；ticket 24 才會填入


@dataclass(frozen=True)
class VerificationBinding:
    """The exact inputs and configuration the result was produced from."""

    prd_digest: str                     # 被判斷的 PRD 文字 SHA-256
    test_case_digest: str               # 被判斷的 test-case 檔案 SHA-256
    model: str                          # 釘住的 Jev model id
    question_set_version: str           # 問題集 hash；不含 PRD 內容
    bands: Bands                        # probability 的分類門檻
    check_set_version: str              # deterministic 檢查規則的版本


@dataclass(frozen=True)
class VerificationRecord:
    """The verdict plus the exact inputs and configuration it was bound to."""

    result: VerificationResult
    binding: VerificationBinding


def worst(statuses: Iterable[VerificationStatus]) -> VerificationStatus:
    """Aggregate statuses with FAIL > BLOCKED > NEEDS_REVIEW > PASS."""
    values = list(statuses)
    if not values:
        return VerificationStatus.BLOCKED
    return max(values, key=_RANK.__getitem__)


def digest_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()
