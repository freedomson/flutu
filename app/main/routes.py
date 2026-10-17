import json

import requests
from flask import Blueprint, current_app, jsonify, render_template, request, session

from app.auth.decorators import login_required
from app.services.quantum_random import choose_direction


main_bp = Blueprint("main", __name__)


@main_bp.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=session["user"])


@main_bp.get("/decision")
@login_required
def decision():
    return render_template("decision.html")


@main_bp.get("/decision/info")
@login_required
def quantum_info():
    return render_template("quantum_info.html")


@main_bp.post("/api/decision")
@login_required
def api_decision():
    try:
        return jsonify(go_right=choose_direction())
    except (requests.RequestException, ValueError, json.JSONDecodeError):
        current_app.logger.exception("Could not retrieve a quantum-random decision")
        return jsonify(error="Could not get a new decision right now."), 502


