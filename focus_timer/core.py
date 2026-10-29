"""Session planning, logging and summaries (the countdown itself lives in the CLI)."""
import csv
import datetime as dt
import os
from collections import defaultdict
from dataclasses import dataclass

FIELDS = ["start", "end", "minutes", "kind", "project", "task", "completed", "note"]


@dataclass
class Session:
    start: dt.datetime
    end: dt.datetime
    kind: str = "focus"            # focus | short_break | long_break
    project: str = ""
    task: str = ""
    completed: bool = True
    note: str = ""

    @property
    def minutes(self):
        return round((self.end - self.start).total_seconds() / 60, 2)

    def row(self):
        return {"start": self.start.isoformat(timespec="seconds"), "end": self.end.isoformat(timespec="seconds"),
                "minutes": self.minutes, "kind": self.kind, "project": self.project, "task": self.task,
                "completed": "yes" if self.completed else "no", "note": self.note}


def plan_cycle(focus=25, short_break=5, long_break=15, rounds=4, cycles=1):
    """Return [(kind, minutes)] for the classic Pomodoro pattern."""
    plan = []
    for c in range(cycles):
        for r in range(rounds):
            plan.append(("focus", focus))
            last = r == rounds - 1
            if not (last and c == cycles - 1):
                plan.append(("long_break" if last else "short_break", long_break if last else short_break))
    return plan


class SessionLog:
    def __init__(self, path=None):
        self.path = path or os.environ.get("FOCUS_LOG", os.path.join(os.path.expanduser("~"), "focus_log.csv"))

    def append(self, session):
        new = not os.path.exists(self.path)
        with open(self.path, "a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            if new:
                w.writeheader()
            w.writerow(session.row())

    def read(self):
        if not os.path.exists(self.path):
            return []
        out = []
        with open(self.path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                out.append(Session(dt.datetime.fromisoformat(r["start"]), dt.datetime.fromisoformat(r["end"]), r["kind"],
                                   r["project"], r["task"], r["completed"] == "yes", r.get("note", "")))
        return out


def summarize(sessions, since=None, until=None):
    """Focus minutes by project and by day, completed vs interrupted, current daily streak."""
    focus = [s for s in sessions if s.kind == "focus" and (since is None or s.start.date() >= since)
             and (until is None or s.start.date() <= until)]
    by_project, by_day = defaultdict(float), defaultdict(float)
    for s in focus:
        by_project[s.project or "(none)"] += s.minutes
        by_day[s.start.date().isoformat()] += s.minutes
    done = sum(1 for s in focus if s.completed)
    days = sorted({s.start.date() for s in focus})
    streak = 0
    if days:
        d = days[-1]
        day_set = set(days)
        while d in day_set:
            streak += 1
            d -= dt.timedelta(days=1)
    return {"sessions": len(focus), "completed": done, "interrupted": len(focus) - done,
            "focus_hours": round(sum(s.minutes for s in focus) / 60, 2),
            "by_project": dict(sorted(by_project.items(), key=lambda kv: -kv[1])),
            "by_day": dict(sorted(by_day.items())), "streak_days": streak}
