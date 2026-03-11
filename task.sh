#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_PATH="$SCRIPT_DIR/data/workplanner.db"

usage() {
  cat <<'USAGE'
Work Planner CLI (SQLite)

Usage:
  task.sh list [area]                         List open tasks (all areas or one)
  task.sh add <area> <section> "task text"    Add a task
  task.sh done <task_id>                      Mark a task complete by ID
  task.sh delegate <task_id> "name"           Set delegated_to by ID
  task.sh delegated                           Show all delegated tasks
  task.sh archive                             Set archived=1 on all done tasks
  task.sh inbox <file|->                      AI-parse raw text into tasks
  task.sh due [today|overdue|week]            Show tasks by due date
  task.sh priority <task_id> <1|2|3|0>        Set priority (0 clears)
  task.sh search "text"                       Search task titles

Areas: sunbelt, app, marketing, personal
USAGE
  exit 1
}

# Helper: run python3 with web/db.py on the path
# We use os.path.dirname(__file__) trick via PYTHONPATH or absolute import.
# On Windows (Git Bash), $SCRIPT_DIR uses /c/... paths that Python can't resolve,
# so we let Python find the web directory relative to db.py's own __file__.
run_py() {
  PYTHONPATH="$SCRIPT_DIR/web" python3 -c "
import sys, os
# Ensure web/ is on path (PYTHONPATH handles it, but add fallback)
_web = os.path.join(os.path.dirname(os.path.abspath('$SCRIPT_DIR')), os.path.basename('$SCRIPT_DIR'), 'web')
if _web not in sys.path:
    sys.path.insert(0, _web)
from db import get_db, init_db
$1
"
}

cmd_list() {
  local area="${1:-}"
  run_py "
init_db()
conn = get_db()
area_filter = '$area'

rows = conn.execute('''
    SELECT a.title AS area_title, s.name AS section_name,
           t.id, t.title, t.done, t.priority, t.due_date, t.delegated_to
    FROM tasks t
    JOIN sections s ON s.id = t.section_id
    JOIN areas a ON a.id = s.area_id
    WHERE t.archived = 0
    ''' + ('AND a.key = ?' if area_filter else '') + '''
    ORDER BY a.position, s.position, t.done ASC, t.position ASC, t.id ASC
''', (area_filter,) if area_filter else ()).fetchall()

current_area = None
current_section = None
for r in rows:
    if r['area_title'] != current_area:
        current_area = r['area_title']
        print()
        print(f'=== {current_area} ===')
    if r['section_name'] != current_section:
        current_section = r['section_name']
        print(f'  [{current_section}]')
    mark = 'x' if r['done'] else ' '
    extra = ''
    if r['delegated_to']:
        extra += f' @delegated({r[\"delegated_to\"]})'
    if r['due_date']:
        extra += f' [due: {r[\"due_date\"]}]'
    if r['priority']:
        extra += f' [P{r[\"priority\"]}]'
    print(f'    [{mark}] #{r[\"id\"]}  {r[\"title\"]}{extra}')
print()
conn.close()
"
}

cmd_add() {
  local area="$1" section="$2" text="$3"
  run_py "
init_db()
conn = get_db()
from db import get_section_id, create_task
sid = get_section_id(conn, '$area', '$section')
if not sid:
    print('Error: section \"$section\" not found in area \"$area\"', file=sys.stderr)
    sys.exit(1)
tid = create_task(conn, sid, '''$text''')
print(f'Added task #{tid} to $area/$section: $text')
conn.close()
"
}

cmd_done() {
  local task_id="$1"
  run_py "
init_db()
conn = get_db()
from db import update_task, get_task
task = get_task(conn, $task_id)
if not task:
    print('Error: task #$task_id not found', file=sys.stderr)
    sys.exit(1)
if task['done']:
    print('Task #$task_id is already completed')
    conn.close()
    sys.exit(0)
update_task(conn, $task_id, done=1)
print(f'Completed: #{$task_id} — {task[\"title\"]}')
conn.close()
"
}

cmd_delegate() {
  local task_id="$1" name="$2"
  run_py "
init_db()
conn = get_db()
from db import update_task, get_task
task = get_task(conn, $task_id)
if not task:
    print('Error: task #$task_id not found', file=sys.stderr)
    sys.exit(1)
update_task(conn, $task_id, delegated_to='''$name''')
print(f'Delegated: #{$task_id} — {task[\"title\"]} -> $name')
conn.close()
"
}

cmd_delegated() {
  run_py "
init_db()
conn = get_db()

rows = conn.execute('''
    SELECT a.title AS area_title, s.name AS section_name,
           t.id, t.title, t.done, t.delegated_to, t.due_date
    FROM tasks t
    JOIN sections s ON s.id = t.section_id
    JOIN areas a ON a.id = s.area_id
    WHERE t.delegated_to IS NOT NULL AND t.delegated_to != \"\"
          AND t.archived = 0
    ORDER BY a.position, s.position, t.position
''').fetchall()

print()
print('=== Delegated Tasks ===')
if not rows:
    print('  (none)')
else:
    current_area = None
    for r in rows:
        if r['area_title'] != current_area:
            current_area = r['area_title']
            print(f'  [{current_area}]')
        mark = 'x' if r['done'] else ' '
        extra = f' @delegated({r[\"delegated_to\"]})'
        if r['due_date']:
            extra += f' [due: {r[\"due_date\"]}]'
        print(f'    [{mark}] #{r[\"id\"]}  {r[\"title\"]}{extra}')
print()
conn.close()
"
}

cmd_archive() {
  run_py "
init_db()
conn = get_db()
from db import archive_completed
count = archive_completed(conn)
if count == 0:
    print('No completed tasks to archive.')
else:
    print(f'Archived {count} task(s).')
conn.close()
"
}

cmd_inbox() {
  local src="${1:-}"
  if [[ -z "$src" ]]; then
    echo "Usage: task.sh inbox <file|->  (use - for stdin)" >&2
    exit 1
  fi

  if [[ "$src" == "-" ]]; then
    python3 "$SCRIPT_DIR/web/inbox_cli.py"
  else
    if [[ ! -f "$src" ]]; then
      echo "File not found: $src" >&2
      exit 1
    fi
    python3 "$SCRIPT_DIR/web/inbox_cli.py" < "$src"
  fi
}

cmd_due() {
  local filter="${1:-today}"
  run_py "
init_db()
conn = get_db()
from db import get_tasks_due_today, get_tasks_overdue, get_tasks_upcoming

filt = '$filter'
if filt == 'today':
    tasks = get_tasks_due_today(conn)
    label = 'Due Today'
elif filt == 'overdue':
    tasks = get_tasks_overdue(conn)
    label = 'Overdue'
elif filt == 'week':
    tasks = get_tasks_upcoming(conn, days=7)
    label = 'Due This Week'
else:
    print('Unknown filter: $filter  (use: today, overdue, week)', file=sys.stderr)
    sys.exit(1)

print()
print(f'=== {label} ===')
if not tasks:
    print('  (none)')
else:
    for t in tasks:
        mark = 'x' if t['done'] else ' '
        area = t.get('area_title', '')
        section = t.get('section_name', '')
        extra = ''
        if t.get('due_date'):
            extra += f' [due: {t[\"due_date\"]}]'
        if t.get('priority'):
            extra += f' [P{t[\"priority\"]}]'
        if t.get('delegated_to'):
            extra += f' @delegated({t[\"delegated_to\"]})'
        print(f'  [{mark}] #{t[\"id\"]}  {area} / {section}: {t[\"title\"]}{extra}')
print()
conn.close()
"
}

cmd_priority() {
  local task_id="$1" level="$2"
  run_py "
init_db()
conn = get_db()
from db import update_task, get_task
task = get_task(conn, $task_id)
if not task:
    print('Error: task #$task_id not found', file=sys.stderr)
    sys.exit(1)
p = $level
if p == 0:
    p = None
update_task(conn, $task_id, priority=p)
if p:
    print(f'Set priority P{p} on #{$task_id} — {task[\"title\"]}')
else:
    print(f'Cleared priority on #{$task_id} — {task[\"title\"]}')
conn.close()
"
}

cmd_search() {
  local query="$1"
  run_py "
init_db()
conn = get_db()

rows = conn.execute('''
    SELECT a.title AS area_title, s.name AS section_name,
           t.id, t.title, t.done, t.priority, t.due_date, t.delegated_to
    FROM tasks t
    JOIN sections s ON s.id = t.section_id
    JOIN areas a ON a.id = s.area_id
    WHERE t.title LIKE ? AND t.archived = 0
    ORDER BY a.position, s.position, t.position
''', ('%$query%',)).fetchall()

print()
print(f'=== Search: \"$query\" ===')
if not rows:
    print('  No matching tasks.')
else:
    for r in rows:
        mark = 'x' if r['done'] else ' '
        extra = ''
        if r['delegated_to']:
            extra += f' @delegated({r[\"delegated_to\"]})'
        if r['due_date']:
            extra += f' [due: {r[\"due_date\"]}]'
        if r['priority']:
            extra += f' [P{r[\"priority\"]}]'
        print(f'  [{mark}] #{r[\"id\"]}  {r[\"area_title\"]} / {r[\"section_name\"]}: {r[\"title\"]}{extra}')
print()
conn.close()
"
}

# Main dispatch
[[ $# -lt 1 ]] && usage

case "$1" in
  list)      cmd_list "${2:-}" ;;
  add)       [[ $# -lt 4 ]] && usage; cmd_add "$2" "$3" "$4" ;;
  done)      [[ $# -lt 2 ]] && usage; cmd_done "$2" ;;
  delegate)  [[ $# -lt 3 ]] && usage; cmd_delegate "$2" "$3" ;;
  delegated) cmd_delegated ;;
  archive)   cmd_archive ;;
  inbox)     cmd_inbox "${2:-}" ;;
  due)       cmd_due "${2:-today}" ;;
  priority)  [[ $# -lt 3 ]] && usage; cmd_priority "$2" "$3" ;;
  search)    [[ $# -lt 2 ]] && usage; cmd_search "$2" ;;
  *)         usage ;;
esac
