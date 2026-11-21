"""Tuition fee calculation for the Student Services App."""

from dataclasses import dataclass
from enum import IntEnum

HOURLY_RATE = 350
LARGE_FEE_THRESHOLD = 6000
LARGE_FEE_REDUCTION = 200
SUMMER_SURCHARGE = 150


class StudentType(IntEnum):
    """Kind of student. The values match the old numeric type codes."""

    REGULAR = 1
    STAFF_CHILD = 2
    SCHOLARSHIP = 3


# Rate table: the share of the normal hourly fee each type pays.
FEE_FACTOR = {
    StudentType.REGULAR: 1,
    StudentType.STAFF_CHILD: 0.5,
    StudentType.SCHOLARSHIP: 0,
}

REPORT_LABEL = {
    StudentType.REGULAR: "Student fee",
    StudentType.STAFF_CHILD: "Staff child fee",
    StudentType.SCHOLARSHIP: "Scholarship fee",
}


@dataclass(frozen=True)
class Course:
    """A course the student is registered for."""

    hours: int


def tuition_fee(courses, student_type, summer=False, discount=0, extras=()):
    """Return the total fee for a list of Course objects.

    The large-fee reduction applies to the tuition only; the summer surcharge,
    the discount and the extras are applied afterwards (same order as the
    legacy code).
    """
    factor = FEE_FACTOR[StudentType(student_type)]
    total = sum(course.hours for course in courses) * HOURLY_RATE * factor
    if total > LARGE_FEE_THRESHOLD:
        total -= LARGE_FEE_REDUCTION
    if summer:
        total += SUMMER_SURCHARGE
    return total - discount + sum(extras)


def fee_report(courses, student_type, summer=False, discount=0):
    """Return a text report of the fee (calculation only, no printing)."""
    fee = tuition_fee(courses, student_type, summer, discount)
    lines = [f"{REPORT_LABEL[StudentType(student_type)]}: {fee}"]
    if fee > LARGE_FEE_THRESHOLD:
        lines.append("High fee")
    return "\n".join(lines)


def process_all(students):
    """Return {name: fee} for every student, including scholarship students."""
    return {
        student["name"]: tuition_fee(
            student["courses"], student["type"], student["summer"]
        )
        for student in students
    }