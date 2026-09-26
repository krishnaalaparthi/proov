# test_fleet_report.py
from fleet_report import fleet_summary

SAMPLE = [
    {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
    {"id": "VOS-2210", "odometer": 48400, "last_service_km": 45000},
]


def test_summary_counts_due_cars():
    # Only VOS-4471 is nearly worn, so exactly one car is due.
    assert fleet_summary(SAMPLE)["due"] == 1


def test_summary_handles_missing_last_service_km():
    # VOS-7788 has no last_service_km — must not crash, and average_wear must be precise.
    fleet = [
        {"id": "VOS-4471", "odometer": 14900, "last_service_km": 0},
        {"id": "VOS-7788", "odometer": 92000},   # no last_service_km key
    ]
    result = fleet_summary(fleet)
    # Must not have raised — reaching here means no crash
    # VOS-4471: wear_percent(14900, 15000) = 99.333...
    # VOS-7788: wear_percent(92000, 15000) = 613.333...
    # average = (99.333... + 613.333...) / 2 = 356.333...
    assert isinstance(result["average_wear"], float), "average_wear must be a float, not an int"
    assert abs(result["average_wear"] - 356.333) < 0.01
