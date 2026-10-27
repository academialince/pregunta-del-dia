"""
Pregunta del día · Prolince → canal de Telegram
Publica una encuesta tipo «quiz» por ejecución, alternando los bancos de
conocimientos, inglés, gramática y ortografía (CSV de la web, separador ;).

Bancos en la carpeta bancos/ (si hay varias versiones, usa la más reciente):
  banco-unificado_Acceso-GC*.csv  -> conocimientos
  Banco_Ingles_GC*.csv            -> inglés
  Banco_Gramatica_GC*.csv         -> gramática
  Banco_Ortografia_GC*.csv        -> ortografía

Variables de entorno:
  TELEGRAM_TOKEN  token del bot (@BotFather)
  TELEGRAM_CHAT   @canal o id numérico (-100...)
  ROTACION        orden de bancos, una entrada por publicación (opcional)
  BANCO           fuerza un banco concreto en esta ejecución (opcional)
"""
import csv, glob, json, os, random, re, sys, urllib.request

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT = os.environ["TELEGRAM_CHAT"]
CARPETA = os.environ.get("CARPETA_BANCOS", "bancos")
ESTADO = "estado.json"

BANCOS = {
    "conocimientos": ("banco-unificado_Acceso-GC*.csv", "📚 CONOCIMIENTOS"),
    "ingles":        ("Banco_Ingles_GC*.csv",           "🇬🇧 INGLÉS"),
    "gramatica":     ("Banco_Gramatica_GC*.csv",        "✍️ GRAMÁTICA"),
    "ortografia":    ("Banco_Ortografia_GC*.csv",       "🔤 ORTOGRAFÍA"),
}
# Con 2 publicaciones al día: mañana siempre conocimientos y tarde rota
# inglés → gramática → ortografía. Se cambia con la variable ROTACION.
ROTACION = os.environ.get(
    "ROTACION",
    "conocimientos,ingles,conocimientos,gramatica,conocimientos,ortografia").split(",")

LETRAS = "ABCD"
MAX_PREGUNTA, MAX_OPCION, MAX_EXPLICACION = 300, 100, 200   # límites de Telegram


def api(metodo, datos):
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TOKEN}/{metodo}",
        data=json.dumps(datos).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def limpiar(t):
    return " ".join((t or "").split())


def recortar(t, n):
    t = limpiar(t)
    return t if len(t) <= n else t[: n - 1] + "…"


def ruta_banco(patron):
    fs = glob.glob(os.path.join(CARPETA, patron))
    if not fs:
        return None
    version = lambda p: int((re.findall(r"_(\d+)\.csv$", p) or [0])[0])
    return max(fs, key=lambda p: (version(p), os.path.getmtime(p)))


def opciones(p):
    return [(l, limpiar(p.get(f"opcion_{l.lower()}"))) for l in LETRAS
            if limpiar(p.get(f"opcion_{l.lower()}"))]


def valida(p, cabecera):
    ops = opciones(p)
    letra = limpiar(p.get("respuesta_correcta")).upper()
    return (len(ops) >= 2 and letra in [l for l, _ in ops]
            and len(cabecera) + len(limpiar(p["enunciado"])) <= MAX_PREGUNTA
            and all(len(o) <= MAX_OPCION for _, o in ops))


def main():
    estado = json.load(open(ESTADO, encoding="utf-8")) if os.path.exists(ESTADO) \
        else {"turno": 0, "publicadas": {}}

    # banco de este turno (si falta el archivo, salta al siguiente de la rotación)
    forzado = os.environ.get("BANCO", "").strip().lower()
    orden = [forzado] if forzado in BANCOS else \
        [ROTACION[(estado["turno"] + i) % len(ROTACION)] for i in range(len(ROTACION))]
    for nombre in orden:
        ruta = ruta_banco(BANCOS[nombre][0])
        if ruta:
            break
    else:
        sys.exit(f"No encuentro ningún banco en {CARPETA}/")

    titulo = BANCOS[nombre][1]
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        filas = [{(k or "").lstrip("\ufeff").strip().lower(): v for k, v in p.items()}
                 for p in csv.DictReader(f, delimiter=";")]
    filas = [p for p in filas if limpiar(p.get("enunciado"))]

    hechas = set(estado["publicadas"].get(nombre, []))
    cab_max = f"{titulo} · Tema 00 · 🎯 Ha caído en examen\n"
    candidatas = [p for p in filas if valida(p, cab_max)]
    pendientes = [p for p in candidatas if limpiar(p["enunciado"]) not in hechas]
    if not pendientes:                      # banco agotado: vuelve a empezar
        hechas.clear()
        pendientes = candidatas
    if not pendientes:
        sys.exit(f"Ninguna pregunta de {ruta} cabe en una encuesta de Telegram.")

    p = random.choice(pendientes)
    extra = ""
    if nombre == "conocimientos" and limpiar(p.get("tema")):
        tema = limpiar(p["tema"])
        extra += f" · {tema if tema.lower().startswith('tema') else 'Tema ' + tema}"
    if "examen oficial" in (p["enunciado"] + p.get("explicacion", "")).lower():
        extra += " · 🎯 Ha caído en examen"
    cabecera = f"{titulo}{extra}\n"
    pregunta = cabecera + recortar(p["enunciado"], MAX_PREGUNTA - len(cabecera))

    ops = opciones(p)
    letra = limpiar(p["respuesta_correcta"]).upper()
    r = api("sendPoll", {
        "chat_id": CHAT,
        "question": pregunta,
        "options": [o for _, o in ops],
        "type": "quiz",
        "correct_option_id": [l for l, _ in ops].index(letra),
        "explanation": recortar(p.get("explicacion"), MAX_EXPLICACION) or None,
        "is_anonymous": True,
    })
    if not r.get("ok"):
        sys.exit(f"Error de Telegram: {r}")

    hechas.add(limpiar(p["enunciado"]))
    estado["publicadas"][nombre] = sorted(hechas)
    estado["turno"] += 1
    json.dump(estado, open(ESTADO, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[{nombre}] {os.path.basename(ruta)} → {p['enunciado'][:90]}")


if __name__ == "__main__":
    main()
