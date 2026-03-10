#!/usr/bin/env bash
set -euo pipefail

TASKS_DIR="$(cd "$(dirname "$0")" && pwd)/tasks"
ARCHIVE_DIR="$(cd "$(dirname "$0")" && pwd)/archive"

# Map short names to files
declare -A FILE_MAP=(
  [personal]="personal.md"
  [sunbelt]="sunbelt.md"
  [app]="planyfi-app.md"
  [marketing]="planyfi-marketing.md"
)

usage() {
  cat <<'USAGE'
Work Planner CLI

Usage:
  task.sh list [area]                         List open tasks (all areas or one)
  task.sh add <area> <section> "task text"    Add a task
  task.sh done <area> <line-number>           Mark a task complete
  task.sh delegate <area> <line-number> "name"  Tag a task as delegated
  task.sh archive                             Move completed tasks to archive
  task.sh delegated                           Show all delegated tasks

Areas: personal, sunbelt, app, marketing
USAGE
  exit 1
}

resolve_file() {
  local area="$1"
  local file="${FILE_MAP[$area]:-}"
  if [[ -z "$file" ]]; then
    echo "Unknown area: $area" >&2
    echo "Valid areas: personal, sunbelt, app, marketing" >&2
    exit 1
  fi
  echo "$TASKS_DIR/$file"
}

cmd_list() {
  local area="${1:-}"
  if [[ -n "$area" ]]; then
    local file
    file=$(resolve_file "$area")
    echo ""
    cat "$file"
  else
    for key in personal sunbelt app marketing; do
      local file="$TASKS_DIR/${FILE_MAP[$key]}"
      echo ""
      cat "$file"
      echo ""
    done
  fi
}

cmd_add() {
  local area="$1" section="$2" text="$3"
  local file
  file=$(resolve_file "$area")

  # Find the section header and append the task after it
  local in_section=false
  local inserted=false
  local tmpfile
  tmpfile=$(mktemp)

  while IFS= read -r line; do
    echo "$line" >> "$tmpfile"
    if [[ "$line" =~ ^##[[:space:]]+(.*) ]]; then
      local header="${BASH_REMATCH[1]}"
      if [[ "${header,,}" == "${section,,}" ]]; then
        in_section=true
      else
        # If we were in the section and hit a new header, we missed inserting
        if $in_section && ! $inserted; then
          # Insert before this header — but we already wrote this line
          # Simpler: just append after the target header
          :
        fi
        in_section=false
      fi
    fi
    # Insert after the section header line
    if $in_section && ! $inserted && [[ "$line" =~ ^## ]]; then
      echo "- [ ] $text" >> "$tmpfile"
      inserted=true
    fi
  done < "$file"

  if $inserted; then
    mv "$tmpfile" "$file"
    echo "Added to $area/$section: $text"
  else
    rm "$tmpfile"
    echo "Section '$section' not found in $area" >&2
    exit 1
  fi
}

cmd_done() {
  local area="$1" line_num="$2"
  local file
  file=$(resolve_file "$area")

  if ! sed -n "${line_num}p" "$file" | grep -q '\- \[ \]'; then
    echo "Line $line_num is not an open task" >&2
    exit 1
  fi

  sed -i "${line_num}s/- \[ \]/- [x]/" "$file"
  local task
  task=$(sed -n "${line_num}p" "$file" | sed 's/- \[x\] //')
  echo "Completed: $task"
}

cmd_delegate() {
  local area="$1" line_num="$2" name="$3"
  local file
  file=$(resolve_file "$area")

  if ! sed -n "${line_num}p" "$file" | grep -q '\- \['; then
    echo "Line $line_num is not a task" >&2
    exit 1
  fi

  # Add delegation tag if not already present
  if sed -n "${line_num}p" "$file" | grep -q '@delegated'; then
    echo "Task already delegated" >&2
    exit 1
  fi

  sed -i "${line_num}s/$/ @delegated($name)/" "$file"
  local task
  task=$(sed -n "${line_num}p" "$file")
  echo "Delegated: $task"
}

cmd_delegated() {
  echo ""
  echo "=== Delegated Tasks ==="
  for key in personal sunbelt app marketing; do
    local file="$TASKS_DIR/${FILE_MAP[$key]}"
    local matches
    matches=$(grep -n '@delegated' "$file" 2>/dev/null | grep -v '<!--' || true)
    if [[ -n "$matches" ]]; then
      echo ""
      echo "[$key]"
      echo "$matches"
    fi
  done
  echo ""
}

cmd_archive() {
  local month_dir="$ARCHIVE_DIR/$(date +%Y-%m)"
  mkdir -p "$month_dir"
  local date_stamp
  date_stamp=$(date +%Y-%m-%d)
  local archived=0

  for key in personal sunbelt app marketing; do
    local file="$TASKS_DIR/${FILE_MAP[$key]}"
    local archive_file="$month_dir/${FILE_MAP[$key]}"

    # Extract completed tasks
    local completed
    completed=$(grep '\- \[x\]' "$file" 2>/dev/null || true)
    if [[ -n "$completed" ]]; then
      echo "# Archived $date_stamp" >> "$archive_file"
      echo "$completed" >> "$archive_file"
      echo "" >> "$archive_file"

      # Remove completed tasks from active file
      sed -i '/- \[x\]/d' "$file"
      local count
      count=$(echo "$completed" | wc -l)
      archived=$((archived + count))
      echo "Archived $count tasks from $key"
    fi
  done

  if [[ $archived -eq 0 ]]; then
    echo "No completed tasks to archive."
  else
    echo "Total archived: $archived tasks → $month_dir/"
  fi
}

# Main dispatch
[[ $# -lt 1 ]] && usage

case "$1" in
  list)      cmd_list "${2:-}" ;;
  add)       [[ $# -lt 4 ]] && usage; cmd_add "$2" "$3" "$4" ;;
  done)      [[ $# -lt 3 ]] && usage; cmd_done "$2" "$3" ;;
  delegate)  [[ $# -lt 4 ]] && usage; cmd_delegate "$2" "$3" "$4" ;;
  delegated) cmd_delegated ;;
  archive)   cmd_archive ;;
  *)         usage ;;
esac
