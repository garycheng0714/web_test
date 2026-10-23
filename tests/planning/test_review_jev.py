from typesafe_sdk import NoulAnswer

from web_test.planning.review.jev import JevAnswer, _normalize


def test_normalize_maps_a_noul_answer_to_a_verdict():
    assert _normalize(NoulAnswer(noul=0.9)) == JevAnswer(0.9)
    assert _normalize(NoulAnswer(noul=0.2)) == JevAnswer(0.2)


def test_normalize_ignores_other_answers():
    assert _normalize(object()) == JevAnswer(None)
