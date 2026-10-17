import base64
import html
import json
import os
import re
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import parse, request
from urllib.parse import parse_qs, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS = {
    "admin@flutu.com": "123456",
    "user@gmail.com": "senha123",
}

GOOGLE_CLIENT_ID = os.environ.get("FLUTU_GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("FLUTU_GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.environ.get("FLUTU_GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/auth/google/callback")


def google_login_url():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + parse.urlencode(params)


def decode_jwt_payload(raw_token):
    try:
        parts = raw_token.split(".")
        if len(parts) != 3:
            return {}
        payload = parts[1]
        padded = payload + "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return {}


def extract_session_email(cookie_header):
    if not cookie_header:
        return None
    jar = cookies.SimpleCookie()
    try:
        jar.load(cookie_header)
    except Exception:
        return None
    session = jar.get("session")
    if not session:
        return None
    value = session.value.strip()
    return value if value else None


def set_session_cookie(email):
    return f"session={email}; Path=/; HttpOnly; SameSite=Lax"


def fetch_random_direction():
    page_request = request.Request(
        "https://qrng.anu.edu.au/random-permutations/",
        headers={"User-Agent": "Flutu/1.0"},
    )
    with request.urlopen(page_request, timeout=20) as response:
        page = response.read().decode("utf-8")

    nonce_match = re.search(
        r'name="permutation_nonce_field"\s+value="([^"]+)"', page
    )
    if not nonce_match:
        raise ValueError("Não foi possível obter o nonce do gerador aleatório.")

    form_data = parse.urlencode(
        {
            "set_num": "1",
            "max_num": "2",
            "action": "permutation_action",
            "permutation_nonce_field": nonce_match.group(1),
            "_wp_http_referer": "/random-permutations/",
        }
    ).encode("utf-8")
    api_request = request.Request(
        "https://qrng.anu.edu.au/wp-admin/admin-ajax.php",
        data=form_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://qrng.anu.edu.au/random-permutations/",
            "User-Agent": "Flutu/1.0",
        },
    )
    with request.urlopen(api_request, timeout=20) as response:
        result = json.loads(response.read().decode("utf-8"))

    if isinstance(result, str):
        result = json.loads(result)
    if not isinstance(result, dict):
        raise ValueError("O gerador retornou uma resposta inválida.")

    permutations = result.get("output") if result.get("type") == "success" else None
    if not isinstance(permutations, list) or not permutations:
        raise ValueError("O gerador não retornou uma permutação.")
    values = permutations[0]
    if not isinstance(values, list) or not values or values[-1] not in (1, 2):
        raise ValueError("O gerador retornou uma permutação inválida.")
    return values[-1] > 1


def render_login_page(error_message=""):
    google_button = ""
    if GOOGLE_CLIENT_ID:
        google_button = f'<a class="google-btn" href="{google_login_url()}">Entrar com Google</a>'
    else:
        google_button = '<div class="google-disabled">Configure FLUTU_GOOGLE_CLIENT_ID para ativar o Login do Google.</div>'

    error_html = "" if not error_message else f'<div class="error">{html.escape(error_message)}</div>'
    return f"""<!DOCTYPE html>
<html lang=\"pt-BR\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Flutu | Entrar</title>
    <style>
      :root {{
        --bg: #f3f7ff;
        --bg-2: #eaf3ff;
        --card: rgba(255, 255, 255, 0.92);
        --text: #14213d;
        --muted: #53627b;
        --line: #dfe8ff;
        --primary: #4f6fff;
        --primary-strong: #2d4ed0;
        --accent: #56d0ff;
        --success: #16a34a;
        --error: #d93025;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle at top left, #f9fbff 0%, var(--bg-2) 28%, var(--bg) 100%); font-family: Arial, Helvetica, sans-serif; color: var(--text);
      }}
      .login-shell {{ width: min(100%, 460px); background: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.7); backdrop-filter: blur(10px); border-radius: 32px; overflow: hidden; box-shadow: 0 24px 70px rgba(69, 91, 157, 0.18); }}
      .form-side {{ display: flex; align-items: center; justify-content: center; padding: 36px 32px; }}
      .login-box {{ width: 100%; background: var(--card); border: 1px solid rgba(17, 24, 39, 0.06); border-radius: 28px; box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08); padding: 30px 28px 20px; }}
      .brand-row {{ display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 16px; }}
      .brand-logo {{ width: 54px; height: 54px; border-radius: 18px; background: linear-gradient(135deg, #3dd9ff, #6d7cff, #8b5cf6); box-shadow: inset 0 2px 12px rgba(255,255,255,0.35); display: grid; place-items: center; color: white; font-weight: 800; font-size: 1.5rem; }}
      .brand-name {{ font-size: 1.9rem; font-weight: 800; letter-spacing: -0.06em; background: linear-gradient(90deg, #2f5de6, #4ca6ff, #7f61ff); -webkit-background-clip: text; background-clip: text; color: transparent; }}
      h1 {{ margin: 0; text-align: center; font-size: 2rem; font-weight: 600; letter-spacing: -0.04em; }}
      .subtitle {{ margin-top: 8px; margin-bottom: 24px; text-align: center; color: var(--muted); font-size: 0.96rem; }}
      .field {{ margin-bottom: 18px; }}
      label {{ display: block; margin-bottom: 8px; font-size: 0.87rem; font-weight: 600; color: var(--muted); }}
      input {{ width: 100%; padding: 14px 16px; border: 1px solid var(--line); border-radius: 12px; font-size: 1rem; background: #fff; outline: none; transition: border-color 0.2s ease, box-shadow 0.2s ease; }}
      input:focus {{ border-color: var(--primary); box-shadow: 0 0 0 4px rgba(91, 108, 255, 0.12); }}
      button {{ width: 100%; padding: 14px 18px; border: none; border-radius: 14px; background: linear-gradient(135deg, var(--primary), #6a8dff); color: white; font-size: 1rem; font-weight: 700; cursor: pointer; box-shadow: 0 10px 22px rgba(79, 111, 255, 0.28); }}
      button:hover {{ background: linear-gradient(135deg, var(--primary-strong), #5671ea); }}
      .google-btn, .google-disabled {{ display: block; width: 100%; margin-top: 12px; padding: 12px 16px; border-radius: 14px; text-align: center; text-decoration: none; font-weight: 700; }}
      .google-btn {{ background: #ffffff; border: 1px solid #d6e0ff; color: #1f2d3d; }}
      .google-disabled {{ background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }}
      .error {{ margin-top: 10px; color: var(--error); font-size: 0.85rem; min-height: 20px; }}
      @media (max-width: 520px) {{ .login-shell {{ border-radius: 24px; }} .form-side {{ padding: 20px 16px; }} .login-box {{ padding: 26px 20px 18px; }} }}
    </style>
  </head>
  <body>
    <div class=\"login-shell\">
      <section class=\"form-side\">
        <div class=\"login-box\">
          <div class=\"brand-row\">
            <div class=\"brand-logo\">F</div>
            <div class=\"brand-name\">flutu</div>
          </div>

          <h1>Entrar</h1>
          <div class=\"subtitle\">Acesse sua conta Flutu</div>

          <form method=\"POST\" action=\"/login\">
            <div class=\"field\">
              <label for=\"email\">E-mail</label>
              <input id=\"email\" name=\"email\" type=\"email\" placeholder=\"voce@flutu.com\" required />
            </div>

            <div class=\"field\">
              <label for=\"password\">Senha</label>
              <input id=\"password\" name=\"password\" type=\"password\" placeholder=\"Digite sua senha\" required />
            </div>

            <button type=\"submit\">Entrar</button>
            {error_html}
          </form>

          {google_button}
        </div>
      </section>
    </div>
  </body>
</html>
"""


def render_dashboard(email):
    return f"""<!DOCTYPE html>
<html lang=\"pt-BR\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Flutu | Dashboard</title>
    <style>
      :root {{ --bg: #edf5ff; --card: rgba(255,255,255,0.95); --text: #132238; --muted: #52637d; --primary: #4f6fff; --primary-soft: #dfe8ff; --shadow: rgba(61, 87, 164, 0.15); }}
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle at top left, #f8fbff, #edf3ff 40%, #e7efff 100%); font-family: Arial, Helvetica, sans-serif; color: var(--text); }}
      .panel {{ width: min(100%, 700px); background: var(--card); border: 1px solid rgba(95, 119, 184, 0.12); border-radius: 28px; box-shadow: 0 18px 48px var(--shadow); padding: 32px 28px; }}
      .topbar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 24px; }}
      .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 800; font-size: 1.7rem; letter-spacing: -0.05em; background: linear-gradient(90deg, #3b82f6, #7c3aed); -webkit-background-clip: text; background-clip: text; color: transparent; }}
      .mark {{ width: 42px; height: 42px; border-radius: 14px; background: linear-gradient(135deg, #3dd9ff, #5a67ff, #8b5cf6); display: grid; place-items: center; color: white; font-weight: 800; }}
      .logout {{ text-decoration: none; color: var(--primary); font-weight: 700; background: var(--primary-soft); padding: 10px 16px; border-radius: 12px; }}
            .decision-link {{ display: inline-block; margin-top: 20px; text-decoration: none; color: white; font-weight: 700; background: var(--primary); padding: 12px 18px; border-radius: 12px; }}
            .decision-link:hover {{ background: #2d4ed0; }}
      .badge {{ display: inline-block; background: #e8f8f1; color: #0f7c5d; padding: 8px 12px; border-radius: 999px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }}
      h1 {{ margin: 18px 0 12px; font-size: clamp(2rem, 3vw, 3rem); letter-spacing: -0.05em; }}
      .email {{ font-size: 1.05rem; color: var(--muted); }}
        @media (max-width: 620px) {{ .panel {{ margin: 18px; padding: 24px 18px; }} .topbar {{ flex-direction: column; align-items: flex-start; }} }}
    </style>
  </head>
  <body>
    <div class=\"panel\">
      <div class=\"topbar\">
        <div class=\"brand\"><span class=\"mark\">F</span> flutu</div>
        <a class=\"logout\" href=\"/logout\">Sair</a>
      </div>
      <div class=\"badge\">Sessão ativa</div>
      <h1>Bem-vindo ao Flutu</h1>
      <div class=\"email\">Você entrou como: <strong>{html.escape(email)}</strong></div>
            <a class=\"decision-link\" href=\"/decision\">Escolher um caminho</a>
    </div>
  </body>
</html>
"""


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/logout":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header(
                "Set-Cookie",
                "session=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0; Path=/; HttpOnly; SameSite=Lax",
            )
            self.end_headers()
            self.wfile.write(
                b"<!doctype html><html><head><meta charset=\"utf-8\"><meta http-equiv=\"refresh\" content=\"0;url=/\"></head><body><script>window.location.href='/'</script><p>Saindo...</p></body></html>"
            )
            return

        if path == "/auth/google":
            if not GOOGLE_CLIENT_ID:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(render_login_page("Google OAuth não configurado. Defina FLUTU_GOOGLE_CLIENT_ID e FLUTU_GOOGLE_CLIENT_SECRET.").encode("utf-8"))
                return
            self.send_response(302)
            self.send_header("Location", google_login_url())
            self.end_headers()
            return

        if path == "/auth/google/callback":
            query = parse.parse_qs(parsed.query)
            code = query.get("code", [""])[0]
            if not code:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(render_login_page("Falha ao autenticar com Google. Código ausente.").encode("utf-8"))
                return

            token_payload = {
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            token_data = parse.urlencode(token_payload).encode("utf-8")
            req = request.Request(
                "https://oauth2.googleapis.com/token",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            try:
                with request.urlopen(req, timeout=20) as response:
                    token_json = json.loads(response.read().decode("utf-8"))
            except Exception:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(render_login_page("Não foi possível trocar o código do Google por um token de sessão.").encode("utf-8"))
                return

            id_token = token_json.get("id_token")
            if not id_token:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(render_login_page("Google não devolveu um id_token válido.").encode("utf-8"))
                return

            claims = decode_jwt_payload(id_token)
            email = (claims.get("email") or "").strip().lower()
            if not email:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(render_login_page("Google não devolveu um e-mail válido.").encode("utf-8"))
                return

            self.send_response(302)
            self.send_header("Location", "/dashboard")
            self.send_header("Set-Cookie", set_session_cookie(email))
            self.end_headers()
            return

        if path == "/dashboard":
            session_email = extract_session_email(self.headers.get("Cookie", ""))
            if not session_email:
                self.send_response(302)
                self.send_header("Location", "/")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(render_dashboard(session_email).encode("utf-8"))
            return

        if path == "/logo.svg":
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.end_headers()
            with open(os.path.join(BASE_DIR, "logo.svg"), "rb") as f:
                self.wfile.write(f.read())
            return

        if path == "/permutation-checker":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with open(os.path.join(BASE_DIR, "permutation-checker.html"), "rb") as f:
                self.wfile.write(f.read())
            return

        if path == "/decision/info":
            if not extract_session_email(self.headers.get("Cookie", "")):
                self.send_response(302)
                self.send_header("Location", "/")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with open(os.path.join(BASE_DIR, "quantum-info.html"), "rb") as f:
                self.wfile.write(f.read())
            return

        if path == "/decision":
            if not extract_session_email(self.headers.get("Cookie", "")):
                self.send_response(302)
                self.send_header("Location", "/")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with open(os.path.join(BASE_DIR, "decision.html"), "rb") as f:
                self.wfile.write(f.read())
            return

        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(render_login_page().encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/decision":
            if not extract_session_email(self.headers.get("Cookie", "")):
                self.send_response(401)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "Autenticação necessária."}).encode("utf-8")
                )
                return
            self.handle_decision()
            return

        if parsed.path == "/api/check-last-number":
            self.handle_check_last_number()
            return

        if parsed.path != "/login":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        data = parse_qs(body, keep_blank_values=True)
        email = data.get("email", [""])[0].strip().lower()
        password = data.get("password", [""])[0].strip()

        if email in USERS and USERS[email] == password:
            self.send_response(302)
            self.send_header("Location", "/dashboard")
            self.send_header("Set-Cookie", set_session_cookie(email))
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(render_login_page("E-mail ou senha inválidos.").encode("utf-8"))

    def handle_check_last_number(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(400, "Corpo deve ser um JSON válido.")
            return

        values = payload.get("set") if isinstance(payload, dict) else None
        if not isinstance(values, list) or not values:
            self.send_error(400, "Envie um array não vazio na propriedade 'set'.")
            return

        last_number = values[-1]
        if isinstance(last_number, bool) or not isinstance(last_number, (int, float)):
            self.send_error(400, "O último item do conjunto deve ser um número.")
            return

        result = last_number > 1
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def handle_decision(self):
        try:
            go_right = fetch_random_direction()
        except (OSError, ValueError, json.JSONDecodeError):
            self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Não foi possível obter uma nova decisão agora."}).encode("utf-8")
            )
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps({"go_right": go_right}).encode("utf-8"))

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8000), AppHandler)
    print("Servidor de login ativo em http://127.0.0.1:8000")
    server.serve_forever()
