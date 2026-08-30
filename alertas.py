import requests
import os
from datetime import date, timedelta

# --- Configuración (se leen de "Secrets" de GitHub, nunca escritas aquí) ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]
CORREO_DESTINO = os.environ["CORREO_DESTINO"]

# --- Paso 1: Traer todos los medicamentos de Supabase ---
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}
response = requests.get(f"{SUPABASE_URL}/rest/v1/Medicamentos?select=*", headers=headers)
medicamentos = response.json()

# --- Paso 2: Revisar cuáles están por vencer o con stock bajo ---
hoy = date.today()
alertas = []

for m in medicamentos:
    vencimiento = date.fromisoformat(m["Fecha_vencimiento"])
    dias_para_vencer = (vencimiento - hoy).days

    if dias_para_vencer < 0:
        alertas.append(f"🔴 {m['Nombre']} — VENCIDO (venció el {vencimiento})")
    elif dias_para_vencer <= 30:
        alertas.append(f"🟠 {m['Nombre']} — vence en {dias_para_vencer} días ({vencimiento})")

    if m["Cantidad"] <= m["Stock_minimo"]:
        alertas.append(f"📦 {m['Nombre']} — stock bajo ({m['Cantidad']} unidades, mínimo {m['Stock_minimo']})")

# --- Paso 3: Si hay alertas, mandar el correo ---
if alertas:
    cuerpo = "<h2>Alertas de inventario - Farmacia</h2><ul>"
    for a in alertas:
        cuerpo += f"<li>{a}</li>"
    cuerpo += "</ul>"

    email_data = {
        "from": "onboarding@resend.dev",
        "to": CORREO_DESTINO,
        "subject": f"⚠️ {len(alertas)} alertas de inventario",
        "html": cuerpo
    }
    resend_headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    r = requests.post("https://api.resend.com/emails", headers=resend_headers, json=email_data)
    print("Correo enviado:", r.status_code, r.text)
else:
    print("Sin alertas por ahora.")
