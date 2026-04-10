#!/usr/bin/env python3
"""Work Planner local server — serves the browser UI and reads/writes task markdown files."""
import subprocess
import yaml
from pathlib import Path
from flask import Flask, jsonify, request, send_file, abort

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / 'config.yaml'
TASKS_DIR = BASE_DIR / 'tasks'
WEB_DIR = BASE_DIR / 'web'

app = Flask(__name__)


def load_config():
    with open(CONFIG_PATH, encoding='utf-8') as f:
        return yaml.safe_load(f)


@app.route('/')
def index():
    return send_file(WEB_DIR / 'index.html')


@app.route('/api/areas')
def get_areas():
    config = load_config()
    result = {}
    for key, val in config['areas'].items():
        result[key] = {
            'file': val['file'],
            'sections': val.get('sections', []),
        }
    return jsonify(result)


@app.route('/api/tasks/<area>', methods=['GET'])
def get_tasks(area):
    config = load_config()
    if area not in config['areas']:
        abort(404)
    file_path = TASKS_DIR / config['areas'][area]['file']
    with open(file_path, encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/api/tasks/<area>', methods=['POST'])
def save_tasks(area):
    config = load_config()
    if area not in config['areas']:
        abort(404)
    file_path = TASKS_DIR / config['areas'][area]['file']
    content = request.get_data(as_text=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    rel_path = f"tasks/{config['areas'][area]['file']}"
    try:
        subprocess.run(['git', 'add', rel_path], cwd=BASE_DIR, check=True, capture_output=True)
        result = subprocess.run(
            ['git', 'commit', '-m', f'UI: update {area} tasks'],
            cwd=BASE_DIR, capture_output=True, text=True
        )
        if result.returncode == 0:
            subprocess.run(['git', 'push'], cwd=BASE_DIR, capture_output=True)
    except Exception:
        pass  # don't fail the request if git is unavailable
    return jsonify({'ok': True})


if __name__ == '__main__':
    print('Work Planner running at http://localhost:5000')
    app.run(debug=False, port=5000)
