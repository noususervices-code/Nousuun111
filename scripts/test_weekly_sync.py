import copy
import unittest
from sync_weekly_events import normalize_event, validate_report


class WeeklySyncTests(unittest.TestCase):
    def setUp(self):
        self.event = {"nimi": "Työpaja", "pvm": "2026-09-16", "linkki": "https://example.org/event", "kuvaus": "Alle 30-vuotiaille helsinkiläisille.", "miksi_suositeltu": "Hyvä harjoitus.", "osallistuminen": "Ikä- ja asuinpaikkaraja; tarkista paikkatilanne."}
        self.report = {"viikko": "2026-W37", "tapahtumat": [self.event]}

    def test_description_and_restrictions_survive(self):
        result = normalize_event(self.event)
        self.assertEqual(result["description"], self.event["kuvaus"])
        self.assertEqual(result["access"], self.event["osallistuminen"])

    def test_unknown_access_not_promised_open(self):
        self.event.pop("osallistuminen")
        self.assertEqual(normalize_event(self.event)["access"], "Tarkista osallistumisehdot järjestäjältä")

    def test_valid_report(self):
        validate_report(self.report)

    def test_empty_missing_or_invalid_report_rejected(self):
        for report in ({}, {"viikko": "2026-W37", "tapahtumat": []}, {"viikko": "2026-W99", "tapahtumat": [self.event]}):
            with self.subTest(report=report), self.assertRaises(ValueError):
                validate_report(report)

    def test_invalid_url_and_date_rejected(self):
        for key, value in (("linkki", "javascript:alert(1)"), ("pvm", "2026-99-01"), ("ilmoittautuminen_paattyy", "bad")):
            report = copy.deepcopy(self.report)
            report["tapahtumat"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_report(report)

    def test_duplicate_or_mismatched_mirror_rejected(self):
        report = copy.deepcopy(self.report)
        report["tapahtumat"].append(copy.deepcopy(self.event))
        with self.assertRaises(ValueError):
            validate_report(report)
        self.report["events"] = []
        with self.assertRaises(ValueError):
            validate_report(self.report)

    def test_registration_deadline_survives(self):
        self.event["ilmoittautuminen_paattyy"] = "2026-09-09"
        self.assertEqual(normalize_event(self.event)["registration_deadline"], "2026-09-09")


if __name__ == "__main__":
    unittest.main()
