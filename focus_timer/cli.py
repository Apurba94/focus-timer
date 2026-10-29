"""Command-line interface for focus-timer."""
import argparse
import datetime as dt
import sys
import time

from .core import Session, SessionLog, plan_cycle, summarize


def countdown(minutes, label, tick=1.0, sleep=time.sleep, out=sys.stdout):
    """Show a countdown; returns True if completed, False if interrupted with Ctrl+C."""
    total = int(minutes * 60)
    try:
        for left in range(total, 0, -1):
            if left % max(1, int(tick)) == 0:
                out.write("\r%s  %02d:%02d " % (label, left // 60, left % 60))
                out.flush()
            sleep(1)
        out.write("\r%s  done!      \a\n" % label)
        return True
    except KeyboardInterrupt:
        out.write("\n%s interrupted\n" % label)
        return False


def main(argv=None, sleep=time.sleep, now=dt.datetime.now):
    ap = argparse.ArgumentParser(prog="focus-timer", description="Pomodoro timer that logs research focus time.")
    ap.add_argument("--log", help="CSV log (default ~/focus_log.csv or $FOCUS_LOG)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start", help="run focus/break cycles")
    s.add_argument("-p", "--project", default="")
    s.add_argument("-t", "--task", default="")
    s.add_argument("--focus", type=float, default=25)
    s.add_argument("--short", type=float, default=5)
    s.add_argument("--long", type=float, default=15)
    s.add_argument("--rounds", type=int, default=4)
    s.add_argument("--once", action="store_true", help="a single focus session")
    lg = sub.add_parser("log", help="record a session after the fact")
    lg.add_argument("minutes", type=float)
    lg.add_argument("-p", "--project", default="")
    lg.add_argument("-t", "--task", default="")
    lg.add_argument("--note", default="")
    rp = sub.add_parser("report")
    rp.add_argument("--days", type=int, default=7)
    args = ap.parse_args(argv)
    log = SessionLog(args.log)
    if args.cmd == "start":
        plan = [("focus", args.focus)] if args.once else plan_cycle(args.focus, args.short, args.long, args.rounds)
        for kind, minutes in plan:
            t0 = now()
            ok = countdown(minutes, "%s %s" % (kind.replace("_", " "), args.project), sleep=sleep)
            log.append(Session(t0, now(), kind, args.project, args.task, ok))
            if not ok:
                break
        return 0
    if args.cmd == "log":
        end = now()
        log.append(Session(end - dt.timedelta(minutes=args.minutes), end, "focus", args.project, args.task, True, args.note))
        print("logged %g min" % args.minutes)
        return 0
    rep = summarize(log.read(), since=now().date() - dt.timedelta(days=args.days - 1))
    print("Last %d days: %.1f focus hours in %d sessions (%d interrupted), streak %d day(s)" % (
        args.days, rep["focus_hours"], rep["sessions"], rep["interrupted"], rep["streak_days"]))
    for p, m in rep["by_project"].items():
        print("  %-25s %6.1f h %s" % (p[:25], m / 60, "#" * int(m // 30)))
    return 0
