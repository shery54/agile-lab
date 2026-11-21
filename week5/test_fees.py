import pytest

from fees import Course, StudentType, fee_report, process_all, tuition_fee
from legacy_fees import calc


def legacy_courses(*hours):
    return [{"h": h} for h in hours]


def courses(*hours):
    return [Course(h) for h in hours]


def student(name, kind):
    return {"name": name, "type": kind, "courses": courses(3), "summer": False}


@pytest.mark.parametrize(
    "hours, code, kind, summer",
    [
        ((3, 3, 3), 1, StudentType.REGULAR, False),
        ((3, 3, 3, 3, 3, 3), 1, StudentType.REGULAR, True),
        ((3, 4), 2, StudentType.STAFF_CHILD, False),
        ((3, 3), 3, StudentType.SCHOLARSHIP, True),
    ],
)
def test_same_result_as_legacy(hours, code, kind, summer):
    old = calc(legacy_courses(*hours), code, 2026, summer, None)
    new = tuition_fee(courses(*hours), kind, summer)
    assert new == old


def test_large_fee_gets_reduction():
    # 18 hours x 350 = 6300 > 6000, so 200 is taken off
    assert tuition_fee(courses(6, 6, 6), StudentType.REGULAR) == 6100


def test_scholarship_student_is_not_skipped():
    students = [
        student("Sara", StudentType.REGULAR),
        student("Omar", StudentType.SCHOLARSHIP),
    ]
    assert process_all(students) == {"Sara": 1050, "Omar": 0}


# Extra characterization tests: edges of the legacy behaviour
def test_fee_just_under_threshold_has_no_reduction():
    # 17 hours x 350 = 5950, not above 6000
    assert tuition_fee(courses(17), StudentType.REGULAR) == 5950


def test_discount_and_extras_match_legacy():
    old = calc(legacy_courses(4, 4), 1, 2026, False, 100, [25, 10])
    new = tuition_fee(courses(4, 4), StudentType.REGULAR, False, 100, (25, 10))
    assert new == old


def test_report_text_for_regular_student():
    assert fee_report(courses(3), StudentType.REGULAR) == "Student fee: 1050"


def test_report_flags_high_fee():
    report = fee_report(courses(6, 6, 6), StudentType.REGULAR)
    assert report == "Student fee: 6100\nHigh fee"