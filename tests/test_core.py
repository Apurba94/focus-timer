import datetime as dt
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from focus_timer.cli import countdown, main
from focus_timer.core import Session, SessionLog, plan_cycle, summarize

T = dt.datetime(2026, 3, 2, 9, 0)


def sess(day, minutes, project="paper", kind="focus", completed=True):
    start = T + dt.timedelta(days=day)
    return Session(start, start + dt.timedelta(minutes=minutes), kind, project, "", completed)


class CoreTests(unittest.TestCase):
    def test_plan_cycle(self):
        plan = plan_cycle(rounds=4)
        self.assertEqual([k for k, _ in plan], ["focus", "short_break"] * 3 + ["focus"])
        two = plan_cycle(rounds=2, cycles=2)
        self.assertEqual(two[3], ("long_break", 15))

    def test_log_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            log = SessionLog(os.path.join(d, "log.csv"))
            log.append(sess(0, 25))
            log.append(sess(0, 10, completed=False))
            rows = log.read()
            self.assertEqual([(r.minutes, r.completed) for r in rows], [(25.0, True), (10.0, False)])

    def test_summary_and_streak(self):
        s = [sess(0, 50), sess(1, 25, "grant"), sess(2, 25), sess(2, 5, kind="short_break"), sess(2, 10, completed=False)]
        rep = summarize(s)
        self.assertEqual((rep["sessions"], rep["interrupted"], rep["streak_days"]), (4, 1, 3))
        self.assertEqual(rep["by_project"], {"paper": 85.0, "grant": 25.0})
        self.assertEqual(summarize(s, since=(T + dt.timedelta(days=2)).date())["sessions"], 2)

    def test_countdown_complete_and_interrupt(self):
        out = io.StringIO()
        self.assertTrue(countdown(0.05, "focus", sleep=lambda s: None, out=out))
        self.assertIn("done", out.getvalue())

        def boom(_):
            raise KeyboardInterrupt
        self.assertFalse(countdown(1, "focus", sleep=boom, out=io.StringIO()))

    def test_cli(self):
        clock = iter(T + dt.timedelta(minutes=i) for i in range(100))
        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "l.csv")
            with redirect_stdout(io.StringIO()) as buf:
                main(["--log", log, "start", "--once", "--focus", "0.02", "-p", "thesis"], sleep=lambda s: None,
                     now=lambda: next(clock))
                main(["--log", log, "log", "30", "-p", "thesis"], now=lambda: T)
                main(["--log", log, "report", "--days", "3"], now=lambda: T)
            self.assertIn("thesis", buf.getvalue())
            self.assertEqual(len(SessionLog(log).read()), 2)


if __name__ == "__main__":
    unittest.main()
