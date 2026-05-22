from flask import Flask, render_template, jsonify
import sqlite3
from pathlib import Path
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)
db_path = Path(__file__).parent / "database_ia.db"

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/models')
def get_models():
    conn = get_db_connection()
    models = conn.execute('SELECT * FROM models ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in models])

@app.route('/api/sessions')
def get_sessions():
    conn = get_db_connection()
    sessions = conn.execute('SELECT * FROM sessions ORDER BY started_at DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in sessions])

@app.route('/api/skills')
def get_skills():
    conn = get_db_connection()
    skills = conn.execute('SELECT * FROM skills ORDER BY timestamp DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in skills])

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    
    total_sessions = conn.execute('SELECT COUNT(*) as count FROM sessions').fetchone()['count']
    total_models = conn.execute('SELECT COUNT(*) as count FROM models').fetchone()['count']
    total_tokens = conn.execute('SELECT SUM(total_tokens) as total FROM sessions').fetchone()['total'] or 0
    total_cost = conn.execute('SELECT SUM(estimated_cost_usd) as total FROM sessions').fetchone()['total'] or 0
    
    # Tokens por modelo
    tokens_by_model = conn.execute('''
        SELECT model, SUM(total_tokens) as total 
        FROM sessions 
        GROUP BY model 
        ORDER BY total DESC
    ''').fetchall()
    
    # Sesiones por día
    sessions_by_day = conn.execute('''
        SELECT DATE(started_at) as date, COUNT(*) as count 
        FROM sessions 
        WHERE started_at IS NOT NULL
        GROUP BY DATE(started_at) 
        ORDER BY date DESC
        LIMIT 7
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'total_sessions': total_sessions,
        'total_models': total_models,
        'total_tokens': total_tokens,
        'total_cost': total_cost,
        'tokens_by_model': [dict(row) for row in tokens_by_model],
        'sessions_by_day': [dict(row) for row in sessions_by_day]
    })

@app.route('/api/refresh')
def refresh_data():
    from data_extractor import extract_data, extract_conversations_from_jsonl
    try:
        extract_data()
        extract_conversations_from_jsonl()
        return jsonify({'status': 'success', 'message': 'Datos actualizados exitosamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/messages')
def get_messages():
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY timestamp DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in messages])

@app.route('/api/messages/<session_id>')
def get_messages_by_session(session_id):
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC', (session_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in messages])

def auto_refresh():
    while True:
        try:
            from data_extractor import extract_data, extract_conversations_from_jsonl
            extract_data()
            extract_conversations_from_jsonl()
            print(f"Datos actualizados automáticamente: {datetime.now()}")
        except Exception as e:
            print(f"Error en auto-refresh: {e}")
        time.sleep(300)  # Refrescar cada 5 minutos

if __name__ == '__main__':
    # Iniciar auto-refresh en background
    refresh_thread = threading.Thread(target=auto_refresh, daemon=True)
    refresh_thread.start()
    
    app.run(debug=True, host='127.0.0.1', port=5000)
