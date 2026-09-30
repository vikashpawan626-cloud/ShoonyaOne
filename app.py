#!/usr/bin/env python3
"""
ShoonyaOne Mobile Web & PWA Server
Provides conversational chat system, voice interaction, and autonomous device execution.
"""

import os
import sys
import io
import re
import json
import contextlib
import subprocess
from flask import Flask, render_template, request, jsonify, send_from_directory
from shoonya.agent import ShoonyaAgent
from shoonya.tools.voice import listen_speech
from shoonya.tools.device import get_battery_status, set_torch
from shoonya.config import HISTORY_FILE

app = Flask(__name__, static_folder="static", template_folder="templates")
agent = ShoonyaAgent()

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def read_history(limit: int = 20):
    """Past conversation history parse karta hai."""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    entries = []
    current_entry = None
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            
        for line in lines[-100:]:
            line = line.strip()
            if not line:
                continue
            # Format: [2026-09-29 14:20:00] Vikash: message
            m = re.match(r'^\[(.*?)\] (Vikash|ShoonyaOne): (.*)$', line)
            if m:
                timestamp, sender, text = m.groups()
                entries.append({
                    "time": timestamp,
                    "sender": "user" if sender == "Vikash" else "agent",
                    "text": text
                })
        return entries[-limit:]
    except Exception:
        return []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

@app.route("/api/history", methods=["GET"])
def get_history_api():
    history = read_history(30)
    return jsonify({"history": history})

@app.route("/api/clear", methods=["POST"])
def clear_history_api():
    # Re-initialize agent session
    agent._create_chat_session(agent.model)
    return jsonify({"success": True, "message": "Chat context reset successfully."})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"reply": "Kuch toh bolein Vikash!", "reasoning": ""})

    # Capture stdout to extract Think/Plan/Execute/Verify steps for UI
    stdout_capture = io.StringIO()
    with contextlib.redirect_stdout(stdout_capture):
        reply = agent.process(user_msg)
    
    captured_logs = stdout_capture.getvalue()
    
    # Format reasoning lines for nice display in HTML
    reasoning_lines = []
    for line in captured_logs.splitlines():
        clean_line = ansi_escape.sub('', line).strip()
        if any(tag in clean_line for tag in ["[THINK]", "[PLAN]", "[EXECUTE]", "[VERIFY"]):
            reasoning_lines.append(clean_line)
            
    reasoning_html = "<br>".join(reasoning_lines) if reasoning_lines else "Autonomous direct execution"

    return jsonify({
        "reply": reply,
        "reasoning": reasoning_html,
        "success": True
    })

@app.route("/api/voice_listen", methods=["GET"])
def voice_listen():
    text = listen_speech()
    return jsonify({"text": text})

@app.route("/api/battery", methods=["GET"])
def battery_api():
    return jsonify(get_battery_status())

@app.route("/api/torch", methods=["POST"])
def torch_api():
    data = request.get_json() or {}
    state = data.get("state", False)
    res = set_torch(state)
    return jsonify(res)

def open_browser():
    try:
        subprocess.Popen(["termux-open-url", "http://localhost:5000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 ShoonyaOne Mobile App Server Starting...")
    print("📍 URL: http://localhost:5000")
    print("📲 Tip: Browser me 'Install App' ya 'Add to Home Screen' dabayein")
    print("="*50 + "\n")
    
    if "--no-browser" not in sys.argv:
        open_browser()
        
    app.run(host="0.0.0.0", port=5000, debug=False)
