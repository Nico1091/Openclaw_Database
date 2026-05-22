import json
import sqlite3
from datetime import datetime
from pathlib import Path
import os

def extract_conversations_from_jsonl():
    """Extrae conversaciones completas de archivos .jsonl de OpenClaw"""
    db_path = Path(__file__).parent / "database_ia.db"
    openclaw_path = Path.home() / ".openclaw"
    sessions_path = openclaw_path / "agents" / "main" / "sessions"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Buscar archivos .jsonl de sesiones
    jsonl_files = list(sessions_path.glob("*.jsonl"))
    
    for jsonl_file in jsonl_files:
        if "trajectory" in jsonl_file.name:
            continue  # Skip trajectory files
            
        session_id = jsonl_file.stem
        print(f"Procesando sesión: {session_id}")
        
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    
                    # Extraer mensajes
                    if data.get("type") == "message":
                        message_data = data.get("message", {})
                        role = message_data.get("role")
                        content = message_data.get("content")
                        timestamp = data.get("timestamp")
                        
                        # Extraer contenido del mensaje
                        content_text = ""
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict):
                                    if item.get("type") == "text":
                                        content_text += item.get("text", "")
                                    elif item.get("type") == "thinking":
                                        content_text += f"[THINKING]: {item.get('thinking', '')}\n"
                        
                        # Calcular tokens si están disponibles
                        tokens = 0
                        if "usage" in message_data:
                            tokens = message_data["usage"].get("totalTokens", 0)
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO messages 
                            (session_id, role, content, timestamp, tokens)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            session_id,
                            role,
                            content_text,
                            timestamp,
                            tokens
                        ))
                
                except json.JSONDecodeError:
                    continue
    
    conn.commit()
    conn.close()
    print("Conversaciones extraídas y almacenadas exitosamente en SQL")

def extract_data():
    """Extrae modelos y sesiones de OpenClaw y los guarda en SQL"""
    db_path = Path(__file__).parent / "database_ia.db"
    openclaw_path = Path.home() / ".openclaw"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Extraer modelos
    models_file = openclaw_path / "agents" / "main" / "agent" / "models.json"
    if models_file.exists():
        with open(models_file, 'r', encoding='utf-8') as f:
            models_data = json.load(f)
            
        for provider_name, provider_data in models_data.get("providers", {}).items():
            for model in provider_data.get("models", []):
                cursor.execute('''
                    INSERT OR REPLACE INTO models 
                    (model_id, name, provider, reasoning, input_types, context_window, max_tokens, cost_input, cost_output, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    model.get("id"),
                    model.get("name"),
                    provider_name,
                    model.get("reasoning", False),
                    json.dumps(model.get("input", [])),
                    model.get("contextWindow"),
                    model.get("maxTokens"),
                    model.get("cost", {}).get("input", 0),
                    model.get("cost", {}).get("output", 0),
                    datetime.now().isoformat()
                ))
    
    # Extraer sesiones
    sessions_file = openclaw_path / "agents" / "main" / "sessions" / "sessions.json"
    if sessions_file.exists():
        with open(sessions_file, 'r', encoding='utf-8') as f:
            sessions_data = json.load(f)
            
        for session_key, session_data in sessions_data.items():
            if isinstance(session_data, dict):
                cursor.execute('''
                    INSERT OR REPLACE INTO sessions 
                    (session_id, session_key, model_provider, model, status, chat_type, channel, 
                     started_at, ended_at, last_interaction_at, runtime_ms, input_tokens, 
                     output_tokens, total_tokens, estimated_cost_usd, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_data.get("sessionId"),
                    session_key,
                    session_data.get("modelProvider"),
                    session_data.get("model"),
                    session_data.get("status"),
                    session_data.get("chatType"),
                    session_data.get("route", {}).get("channel") if session_data.get("route") else None,
                    datetime.fromtimestamp(session_data.get("sessionStartedAt", 0) / 1000).isoformat() if session_data.get("sessionStartedAt") else None,
                    datetime.fromtimestamp(session_data.get("endedAt", 0) / 1000).isoformat() if session_data.get("endedAt") else None,
                    datetime.fromtimestamp(session_data.get("lastInteractionAt", 0) / 1000).isoformat() if session_data.get("lastInteractionAt") else None,
                    session_data.get("runtimeMs"),
                    session_data.get("inputTokens"),
                    session_data.get("outputTokens"),
                    session_data.get("totalTokens"),
                    session_data.get("estimatedCostUsd"),
                    datetime.now().isoformat()
                ))
                
                # Extraer skills usadas
                skills_snapshot = session_data.get("skillsSnapshot", {})
                if isinstance(skills_snapshot, dict):
                    for skill in skills_snapshot.get("skills", []):
                        cursor.execute('''
                            INSERT INTO skills (session_id, skill_name, skill_location, required_env)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            session_data.get("sessionId"),
                            skill.get("name"),
                            skill.get("location"),
                            json.dumps(skill.get("requiredEnv", []))
                        ))
    
    conn.commit()
    conn.close()
    print("Datos extraídos y almacenados exitosamente en SQL")

if __name__ == "__main__":
    extract_data()
    extract_conversations_from_jsonl()
