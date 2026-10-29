# focus-timer

**A Pomodoro timer for deep research work that logs every session by project, so you can see
where your writing, analysis and reading time actually goes.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Research progress depends on long blocks of focused work, which meetings, e-mail and chat constantly
fragment. Timeboxing (25-minute focus blocks with short breaks) helps start and sustain hard tasks such
as writing. Logging the blocks turns vague feelings ("I never get to write") into data you can act on,
for example in supervisor meetings or when reporting time per grant.

## Features

- Classic cycles (focus / short break / long break), configurable lengths and rounds, or `--once`
- Every session appended to a CSV log (start, end, minutes, kind, project, task, completed)
- Ctrl+C marks a session as interrupted instead of losing it
- `log` adds sessions after the fact (e.g. writing done away from the computer)
- `report`: focus hours per project for the last N days, interruptions and daily streak

## Usage

```bash
pip install .
focus-timer start -p "paper-2" -t "results section"
focus-timer start --once --focus 50 -p thesis
focus-timer log 90 -p grant --note "budget justification"
focus-timer report --days 30
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
