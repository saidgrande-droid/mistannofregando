#!/usr/bin/env python3
"""
telegram_bot.py
Modulo e Controller Telegram + Netlify per "Mi Stanno Fregando?" (Il Fregometro).
Connesso a @Antigravity_Gad_Bot (chat_id: 5670302778).
"""

import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path("/Users/grafica/Desktop/SITO/SITO PER TRAFFICO")
SITO_BASE = Path("/Users/grafica/Desktop/SITO")
NETLIFY_DEPLOY_DIR = SITO_BASE / "netlify_deploy"
NETLIFY_FREGOMETRO_HTML = NETLIFY_DEPLOY_DIR / "fregometro.html"
LIVE_URL = "https://musical-bavarois-380b3d.netlify.app/fregometro.html"

DATASET_JSON = ROOT / "src" / "core" / "dataset.json"
APP_TSX = ROOT / "src" / "App.tsx"
REQUESTS_LOG = ROOT / "telegram_requests.jsonl"
STANDALONE_HTML = ROOT / "Mi-Stanno-Fregando-Telegram.html"

DEFAULT_TOKEN = "8933193506:AAFoylwxkTfxBx5FZRigL0vYqCYrEnCEQq8"
DEFAULT_CHAT_ID = 5670302778
SSL_CTX = ssl._create_unverified_context()


def build_and_deploy_fregometro(deploy_live: bool = True) -> tuple[Path, str]:
    """
    1. Ricompila public/app-bundle.js
    2. Genera Mi-Stanno-Fregando-Telegram.html (file singolo autocontenuto)
    3. Copia in /Users/grafica/Desktop/SITO/netlify_deploy/fregometro.html
    4. Esegue il deploy su Netlify così il link pubblico è aggiornato in tempo reale
    """
    subprocess.run([sys.executable, str(ROOT / "build_bundle.py")], check=True)
    index_content = (ROOT / "index.html").read_text(encoding="utf-8")
    bundle_content = (ROOT / "public" / "app-bundle.js").read_text(encoding="utf-8")

    standalone = index_content.replace(
        '<script src="./public/app-bundle.js"></script>',
        f"<script>\n{bundle_content}\n</script>",
    )
    STANDALONE_HTML.write_text(standalone, encoding="utf-8")

    if NETLIFY_DEPLOY_DIR.exists():
        shutil.copyfile(STANDALONE_HTML, NETLIFY_FREGOMETRO_HTML)
        if deploy_live and (SITO_BASE / "deploy_to_netlify.py").exists():
            subprocess.run(
                [sys.executable, str(SITO_BASE / "deploy_to_netlify.py")],
                check=False,
                timeout=45,
            )

    return STANDALONE_HTML, f"{LIVE_URL}?v={int(time.time())}"


def tg_request(token: str, method: str, payload: dict = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=35, context=SSL_CTX) as resp:
        return json.loads(resp.read().decode("utf-8"))


def tg_send_document(token: str, chat_id: int, file_path: Path, caption: str = "") -> dict:
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    url = f"https://api.telegram.org/bot{token}/sendDocument"

    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(b'Content-Disposition: form-data; name="chat_id"\r\n\r\n')
    body.extend(f"{chat_id}\r\n".encode())

    if caption:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(b'Content-Disposition: form-data; name="caption"\r\n\r\n')
        body.extend(f"{caption}\r\n".encode("utf-8"))

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        f'Content-Disposition: form-data; name="document"; filename="{file_path.name}"\r\n'.encode("utf-8")
    )
    body.extend(b"Content-Type: text/html\r\n\r\n")
    body.extend(file_path.read_bytes())
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_html_msg(token: str, chat_id: int, text: str, reply_markup: dict = None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        tg_request(token, "sendMessage", payload)
    except Exception as e:
        print(f"[Telegram Send Error] {e}", flush=True)


def get_fregometro_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "🌐 Apri Sito Live (Mobile/Desktop)", "url": LIVE_URL},
            ],
            [
                {"text": "📲 Invia File HTML in Chat", "callback_data": "freg_send_file"},
                {"text": "✏️ Guida Modifiche", "callback_data": "freg_help"},
            ],
            [
                {"text": "🚗 Auto", "callback_data": "freg_cat_auto"},
                {"text": "🏠 Casa", "callback_data": "freg_cat_casa"},
                {"text": "🦷 Dentista", "callback_data": "freg_cat_dentista"},
            ],
            [
                {"text": "🐾 Veterinario", "callback_data": "freg_cat_veterinario"},
                {"text": "💐 Cerimonie", "callback_data": "freg_cat_cerimonie"},
                {"text": "🔑 Affitti", "callback_data": "freg_cat_affitti"},
            ],
        ]
    }


def update_site_title(new_title: str) -> tuple[bool, str]:
    content = APP_TSX.read_text(encoding="utf-8")
    pattern = r'(<h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-950 font-display leading-none">\s*)(.*?)(\s*</h1>)'
    if not re.search(pattern, content, flags=re.DOTALL):
        return False, ""
    updated = re.sub(pattern, rf"\g<1>{new_title}\g<3>", content, count=1, flags=re.DOTALL)
    APP_TSX.write_text(updated, encoding="utf-8")
    _, live_url = build_and_deploy_fregometro(deploy_live=True)
    return True, live_url


def update_site_tagline(new_tagline: str) -> tuple[bool, str]:
    content = APP_TSX.read_text(encoding="utf-8")
    pattern = r'(<p className="text-xs text-slate-600 font-bold mt-0\.5">\s*)(.*?)(\s*</p>)'
    if not re.search(pattern, content, flags=re.DOTALL):
        return False, ""
    updated = re.sub(pattern, rf"\g<1>{new_tagline}\g<3>", content, count=1, flags=re.DOTALL)
    APP_TSX.write_text(updated, encoding="utf-8")
    _, live_url = build_and_deploy_fregometro(deploy_live=True)
    return True, live_url


def update_service_price(prest_id: str, new_price: float) -> tuple[bool, str]:
    data = json.loads(DATASET_JSON.read_text(encoding="utf-8"))
    for p in data.get("prestations", []):
        if p["id"] == prest_id:
            old_price = p["basePrice"]
            p["basePrice"] = round(new_price)
            p["realisticRange"] = [round(new_price * 0.65), round(new_price * 1.45)]
            p["antiSpamBounds"] = [max(5, round(new_price * 0.2)), round(new_price * 3.5)]
            DATASET_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            _, live_url = build_and_deploy_fregometro(deploy_live=True)
            return (
                True,
                f"✅ Prezzo di <b>{p['name']}</b> aggiornato da {old_price}€ a <b>{round(new_price)}€</b>!\n🌐 Live: {live_url}",
            )
    return False, f"❌ Servizio con ID <code>{prest_id}</code> non trovato."


def add_new_service(cat_id: str, name: str, base_price: float) -> tuple[bool, str]:
    cat_id = cat_id.strip().lower()
    data = json.loads(DATASET_JSON.read_text(encoding="utf-8"))
    valid_cats = [c["id"] for c in data.get("categories", [])]
    if cat_id not in valid_cats:
        return False, f"❌ Categoria non valida. Usa una tra: {', '.join(valid_cats)}"

    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:24]
    new_id = f"{cat_id}_{slug}"
    price_int = round(base_price)
    new_prest = {
        "id": new_id,
        "categoryId": cat_id,
        "name": name.strip(),
        "description": f"{name.strip()} (aggiunto da Telegram)",
        "unit": "intervento",
        "basePrice": price_int,
        "realisticRange": [round(price_int * 0.7), round(price_int * 1.4)],
        "antiSpamBounds": [max(5, round(price_int * 0.2)), round(price_int * 3.5)],
    }
    data["prestations"].append(new_prest)
    DATASET_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    _, live_url = build_and_deploy_fregometro(deploy_live=True)
    return (
        True,
        f"🎉 Nuovo servizio <b>{name}</b> ({price_int}€) aggiunto nella categoria <b>{cat_id}</b>!\n🌐 Live: {live_url}",
    )


def format_category_services(cat_id: str) -> str:
    data = json.loads(DATASET_JSON.read_text(encoding="utf-8"))
    items = [p for p in data.get("prestations", []) if p["categoryId"] == cat_id]
    if not items:
        return f"Nessun servizio trovato per {cat_id}."
    lines = [f"📋 <b>Servizi categoria {cat_id.upper()}</b>:\n"]
    for p in items:
        lines.append(f"• <b>{p['name']}</b>: <code>{p['basePrice']} €</code>\n  ID: <code>{p['id']}</code>")
    lines.append("\n💡 <i>Per modificare un prezzo scrivi:</i>\n<code>/prezzo ID_SERVIZIO NUOVO_PREZZO</code>")
    return "\n".join(lines)


def send_initial_fregometro_package(token: str = DEFAULT_TOKEN, chat_id: int = DEFAULT_CHAT_ID):
    html_file, live_url = build_and_deploy_fregometro(deploy_live=True)
    intro = (
        "🕵️‍♂️ <b>MI STANNO FREGANDO? (Il Fregometro™) è online e collegato a Telegram!</b>\n\n"
        f"🌐 <b>Link Diretto Live (Mobile & PC):</b>\n{live_url}\n\n"
        "🛠 <b>Come modificare il sito direttamente da questa chat Telegram:</b>\n"
        "• <code>/fregometro</code> — Mostra questo pannello e il link live\n"
        "• <code>/titolo Nuovo Titolo</code> — Modifica il titolo del sito e pubblica online\n"
        "• <code>/sottotitolo Nuovo Testo</code> — Modifica il sottotitolo sotto il logo\n"
        "• <code>/prezzo auto_tagliando 260</code> — Cambia il prezzo medio di un servizio\n"
        "• <code>/nuovo casa | Riparazione Tapparella | 90</code> — Aggiunge un nuovo servizio nel sito\n"
        "• Oppure scrivi <code>modifica fregometro: ...</code> con qualsiasi richiesta grafica e la applico in tempo reale!"
    )
    send_html_msg(token, chat_id, intro, get_fregometro_keyboard())
    tg_send_document(
        token,
        chat_id,
        html_file,
        caption="📦 Ecco anche il file HTML completo di 'Mi Stanno Fregando?' (apribile anche offline).",
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "send_now":
        send_initial_fregometro_package()
