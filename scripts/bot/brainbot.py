#!/usr/bin/env python3
"""
BrainBot v4.0 — Asistente multipropósito Chicken Palace Ibiza
==============================================================
Comandos '/' para Home Assistant (domotica).
Conversacion libre con Ollama (modelo local).
Memoria contextual por chat.

Corre DENTRO del contenedor HA (via Terminal Addon).
OLLAMA_URL apunta a http://127.0.0.1:11434 por defecto.
"""

import asyncio
import json
import logging
import os
import re
import signal
import unicodedata
from collections import defaultdict
from datetime import datetime as dt
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("brainbot")

# ─── CONFIGURACION ────────────────────────────────────────────

TG_TOKEN: str = os.environ.get("TG_BOT_TOKEN", "")
HASS_TOKEN: str = os.environ.get("HASS_TOKEN", "")
HASS_URL: str = os.environ.get("HASS_URL", "http://127.0.0.1:8123")
OLLAMA_URL: str = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "llama3.1")

LONG_POLL_TIMEOUT = 30
MAX_CONTEXT_MSGS = 20
MEMORY_FILE = "/config/bot/conversation_memory.json"

HaResult = Tuple[Optional[int], Any]

# ─── MEMORIA CONVERSACIONAL ───────────────────────────────────

memory: Dict[str, List] = defaultdict(list)


def load_memory() -> None:
    global memory
    try:
        p = Path(MEMORY_FILE)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                memory = defaultdict(list, data)
            total = sum(len(v) for v in memory.values())
            logger.info("Memoria cargada: %d msgs en %d chats", total, len(memory))
    except Exception as e:
        logger.warning("Error cargando memoria: %s", e)


def save_memory() -> None:
    try:
        p = Path(MEMORY_FILE)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(dict(memory), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        logger.warning("Error guardando memoria: %s", e)


def add_to_context(chat_id: str, role: str, content: str) -> None:
    key = str(chat_id)
    memory[key].append({"role": role, "content": content})
    if len(memory[key]) > MAX_CONTEXT_MSGS * 2:
        memory[key] = memory[key][-MAX_CONTEXT_MSGS:]
    save_memory()


def get_context(chat_id: str) -> List:
    return memory.get(str(chat_id), [])


def clear_context(chat_id: str) -> None:
    memory.pop(str(chat_id), None)
    save_memory()


# ─── LLM (OLLAMA) ────────────────────────────────────────────

SYSTEM_PROMPT = (
    "Eres el asistente personal de David en Chicken Palace Ibiza. "
    "Responde en espanol por defecto.\n\n"
    "Eres conversacional, util, preciso y con sentido del humor cuando corresponda. "
    "Sabes que vives en una casa domotica en Ibiza y que puedes controlar "
    "dispositivos de Home Assistant.\n\n"
    "Cuando un usuario te pide algo que no puedes hacer (como buscar en internet, "
    "ver imagenes, recordar cosas que no te han dicho explicitamente), "
    "dilo honestamente pero ofrece alternativas.\n\n"
    "Si te hacen preguntas tecnicas, da respuestas detalladas. "
    "Si es conversacion casual, se natural y cercano. "
    "Si te piden consejos, da tu mejor criterio.\n\n"
    "IMPORTANTE: Si el usuario usa un comando que empieza con '/', "
    "NO lo trates como conversacion. Esos son comandos del sistema. "
    "Solo genera respuestas conversacionales cuando NO hay comando."
)


def _parse_ollama(body: str, status: int) -> str:
    """Parsea respuesta JSON/text de Ollama."""
    if status != 200:
        return "⚠️ Error de Ollama ({}): {}".format(status, body[:200])
    try:
        data: Any = json.loads(body)
    except json.JSONDecodeError:
        return body[:500] if body.strip() else "🤔 Ollama no devolvio texto."

    full_text = ""
    if isinstance(data, dict):
        msg = data.get("message", {})
        if isinstance(msg, dict):
            full_text = msg.get("content", "")
        if not full_text and "response" in data:
            full_text = data["response"]
    elif isinstance(data, str):
        full_text = data
    else:
        full_text = json.dumps(data)

    if not full_text.strip() and "response" not in data:  # type: ignore
        return "🤔 Ollama no devolvio texto."
    return full_text


async def ask_ollama(user_text: str, chat_id: str,
                     timeout: int = 120) -> str:
    """Envía mensaje a Ollama con contexto conversacional."""
    context = get_context(chat_id)

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    for msg in context[-MAX_CONTEXT_MSGS:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_text})

    url = "{}/api/chat".format(OLLAMA_URL)
    payload: Dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 2048,
        },
    }

    logger.info("Ollama: enviando %d msgs a %s", len(messages), OLLAMA_MODEL)

    for attempt in range(3):
        try:
            session_timeout = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=session_timeout) as session:
                async with session.post(url, json=payload) as resp:
                    body = await resp.text()
                    result = _parse_ollama(body, resp.status)

                    if result.startswith("🤔") and attempt < 2:
                        await asyncio.sleep(2)
                        continue

                    if not result.startswith("⚠️") and not result.startswith("❌"):
                        add_to_context(chat_id, "user", user_text)
                        add_to_context(chat_id, "assistant", result)

                    return result

        except asyncio.TimeoutError:
            return "\u23f1️ Ollama tardo demasiado. Intentalo de nuevo."
        except aiohttp.ClientConnectorError as e:
            logger.error("Ollama conn error (att %d): %s", attempt + 1, e)
            if attempt < 2:
                await asyncio.sleep(3)
                continue
            return (
                "\u274c No pude conectar con Ollama en {}.\n"
                "¿Ollama esta corriendo? Prueba: `ollama serve`"
            ).format(OLLAMA_URL)
        except Exception as e:
            logger.error("Ollama error (att %d): %s", attempt + 1, e)
            if attempt < 2:
                await asyncio.sleep(2)
                continue
            return "❌ Error de Ollama: {}".format(str(e)[:200])

    return "❌ Ollama no respondio tras 3 intentos."


# ─── API HELPERS ──────────────────────────────────────────────

def ha_headers() -> Dict[str, str]:
    return {
        "Authorization": "Bearer {}".format(HASS_TOKEN),
        "Content-Type": "application/json",
    }


async def ha(method: str, endpoint: str,
             data: Any = None, retries: int = 2) -> HaResult:
    """Llamada a la API de Home Assistant."""
    for att in range(retries + 1):
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = "{}/api{}".format(HASS_URL, endpoint)
                async with session.request(
                    method, url, headers=ha_headers(), json=data
                ) as resp:
                    body = await resp.text()
                    try:
                        return resp.status, json.loads(body) if body else {}
                    except (json.JSONDecodeError, ValueError):
                        return resp.status, body
        except Exception as e:
            if att == retries:
                logger.error("HA API error: %s", e)
                return None, str(e)
            await asyncio.sleep(1)
    return None, "Max retries exceeded"


async def tg(method: str, **kw: Any) -> dict:
    """Llamada a Telegram Bot API."""
    for att in range(3):
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = "https://api.telegram.org/bot{}/{}".format(
                    TG_TOKEN, method
                )
                async with session.post(url, json=kw) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error("tg(%s) att %d: %s", method, att + 1, e)
            await asyncio.sleep(2)
    return {"ok": False}


async def send(chat_id: int, text: str,
               parse_mode: str = "HTML") -> None:
    """Enviar mensaje, con split si supera el limite de Telegram."""
    if not text:
        return
    max_len = 4000
    if len(text) <= max_len:
        try:
            await tg("sendMessage",
                     chat_id=chat_id, text=text,
                     parse_mode=parse_mode,
                     disable_web_page_preview=True)
        except Exception as e:
            logger.error("send error: %s", e)
        return

    parts: List[str] = []
    while len(text) > max_len:
        cut = text[:max_len].rfind("\n")
        if cut == -1:
            cut = max_len
        parts.append(text[:cut])
        text = text[cut:]
    parts.append(text)

    for i, part in enumerate(parts):
        prefix = "[{}/{}] ".format(i + 1, len(parts)) if len(parts) > 1 else ""
        try:
            await tg("sendMessage",
                     chat_id=chat_id,
                     text=prefix + part,
                     parse_mode=parse_mode)
            await asyncio.sleep(0.3)
        except Exception as e:
            logger.error("send chunk error: %s", e)


# ─── COMANDOS DEL BOT ─────────────────────────────────────────

GREETINGS = [
    "hola", "buenos dias", "buenas tardes", "buenas noches",
    "hey", "hi", "hello", "que tal", "como estas", "ola",
    "buenas", "wassup", "que hay", "hey david",
]


def normalizar(text: str) -> str:
    """Minusculas sin tildes para matching."""
    t = text.strip().lower()
    nfkd = unicodedata.normalize("NFKD", t)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


async def cmd_help(chat_id: int) -> None:
    await send(chat_id,
        "<b>BrainBot v4.1 — Superpoderes Chicken Palace</b>\n\n"
        "<b>🏠 DOMOTICA</b>\n"
        "/home — Estado general\n"
        "/luces on|off|toggle — Control luz principal\n"
        "/todas on|off|toggle — Todas las luces\n"
        "/habitacion <nombre> on|off|toggle — Luz x habitacion\n"
        "/cine — Modo cine\n"
        "/fiesta — Modo fiesta\n"
        "/noche — Modo noche\n"
        "/seguridad — Alarmas\n"
        "/energia — Consumo electrico\n"
        "/clima — Temperatura interior\n"
        "/persianas up|down|stop [nombre] — Control cortinas\n"
        "/camara — Estado camaras\n"
        "/personas — Quien esta en casa\n"
        "/puertas — Estado puertas/ventanas\n"
        "/escenas — Listar y activar escenas\n"
        "/automatizaciones — Estado de automatizaciones\n"
        "/script <nombre> — Ejecutar script de HA\n"
        "/servicio <dominio.servicio> [entidad] — Llamar servicio HA\n"
        "/logs — Ultimos logs de HA\n"
        "/gato — Peso del gato\n\n"
        "<b>🤖 IA</b>\n"
        "/modelo — Cambiar o ver modelo de IA\n"
        "/sync — Sync documental / estado pipeline\n\n"
        "<b>UTILIDADES</b>\n"
        "/memoria — Contexto de conversacion\n"
        "/memoria off — Borrar memoria del chat\n"
        "/reboot — Reiniciar Home Assistant\n"
        "/notificar <texto> — Notificacion en HA\n"
        "/estado — Estado del bot y conexiones\n"
        "/version — Version\n"
        "/menu — Menu interactivo de superpoderes\n\n"
        "<b>CONVERSACION</b>\n"
        "Escribeme lo que quieras y te respondo.\n"
        "Preguntame cualquier cosa, cuentame tu dia,\n"
        "pide consejos, traducciones, resumenes...\n\n"
        "<i>Modelo: {}</i>".format(OLLAMA_MODEL),
        parse_mode="HTML",
    )


async def cmd_home(chat_id: int) -> None:
    items: Dict[str, str] = {}
    entities: List[Tuple[str, str]] = [
        ("sensor.temperature_temperatura", "Temp"),
        ("sensor.temperature_humedad", "Humedad"),
        ("sensor.medidor_electrico_potencia", "Consumo"),
        ("light.rayo", "Luz principal"),
        ("input_boolean.david_home", "David en casa"),
        ("person.david_nows", "David"),
        ("person.neo44hd", "Neo44HD"),
        ("sensor.home_assistant_energy", "Consumo hoy"),
        ("cover.vesti_garaje_cortina", "Cortina garaje"),
        ("cover.ventana_c_cortina", "Cortina ventana C"),
    ]
    for eid, label in entities:
        try:
            sc, bd = await ha("GET", "/states/{}".format(eid))
            if sc == 200 and isinstance(bd, dict):
                items[label] = bd.get("state", "?")
            else:
                items[label] = "N/A"
        except Exception:
            items[label] = "N/A"

    lines: List[str] = ["<b>Estado General — Chicken Palace</b>\n"]
    for lbl, st in items.items():
        s = st.lower()
        if s in ("on", "home", "true"):
            ico = "\U0001f7e2"
        elif s in ("off", "not_home", "false"):
            ico = "\U0001f534"
        elif st == "N/A":
            ico = "\u26d4"
        else:
            ico = "\u2b1c"
        lines.append("  {}  {}: <b>{}</b>".format(ico, lbl, st))
    lines.append("\n\u23f0 {}".format(
        dt.now().strftime("%d/%m %H:%M:%S")))
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_lights(chat_id: int, action: str,
                     name: Optional[str] = None) -> None:
    if action not in ("on", "off", "toggle"):
        await send(chat_id, "Uso: /luces on | off | toggle")
        return

    light_map = {
        "rayo": "light.rayo",
        "cacfb9": "light.wiz_rgbw_tunable_cacfb9",
        "1316a6": "light.wiz_rgbw_tunable_1316a6",
        "garaje": "light.vesti_garaje_luz_de_fondo",
        "grout": "light.vesti_grout_luz_de_fondo",
        "c": "light.ventana_c_luz_de_fondo",
        "t": "light.ventana_t_luz_de_fondo",
        "frega": "light.led_bulb_w509z2",
        "fondo": "light.led_bulb_w509z2_2",
    }

    if name and name.lower() in light_map:
        target = light_map[name.lower()]
    else:
        target = "light.rayo"

    sc, bd = await ha("GET", "/states/{}".format(target))
    if sc != 200 or not isinstance(bd, dict):
        await send(chat_id, "\u274c No encuentro la luz '{}'.".format(target))
        return

    cur = bd.get("state", "off")
    if action == "toggle":
        action = "off" if cur == "on" else "on"
    act = "turn_on" if action == "on" else "turn_off"
    await ha("POST", "/services/light/{}".format(act),
             {"entity_id": target})
    emoji = "\U0001f4a1" if action == "on" else "\U0001f303"
    status_word = "ENCENDIDA" if action == "on" else "APAGADA"
    await send(chat_id,
               "{} Luz <b>{}</b> ({})".format(emoji, status_word, target))


async def cmd_todas_luces(chat_id: int, action: str) -> None:
    if action not in ("on", "off", "toggle"):
        await send(chat_id, "Uso: /todas on | off | toggle")
        return

    real_lights = [
        "light.wiz_rgbw_tunable_cacfb9",
        "light.wiz_rgbw_tunable_1316a6",
        "light.rayo",
        "light.vesti_garaje_luz_de_fondo",
        "light.vesti_grout_luz_de_fondo",
        "light.ventana_c_luz_de_fondo",
        "light.ventana_t_luz_de_fondo",
        "light.led_bulb_w509z2",
        "light.led_bulb_w509z2_2",
    ]

    if action == "toggle":
        on_count = 0
        off_count = 0
        for eid in real_lights:
            sc, bd = await ha("GET", "/states/{}".format(eid))
            if sc == 200 and isinstance(bd, dict):
                st = bd.get("state", "off")
                if st == "on":
                    on_count += 1
                elif st == "off":
                    off_count += 1
        action = "off" if on_count > off_count else "on"

    act = "turn_on" if action == "on" else "turn_off"
    for eid in real_lights:
        await ha("POST", "/services/light/{}".format(act),
                 {"entity_id": eid})
    emoji = "\U0001f4a1" if action == "on" else "\U0001f303"
    status_word = "ENCENDIDAS" if action == "on" else "APAGADAS"
    await send(chat_id,
               "{} Todas las luces <b>{}</b>".format(emoji, status_word))


async def cmd_habitacion(chat_id: int, name: str,
                         action: str) -> None:
    light_map = {
        "garaje": "light.vesti_garaje_luz_de_fondo",
        "grout": "light.vesti_grout_luz_de_fondo",
        "c": "light.ventana_c_luz_de_fondo",
        "t": "light.ventana_t_luz_de_fondo",
        "frega": "light.led_bulb_w509z2",
        "fondo": "light.led_bulb_w509z2_2",
        "rayo": "light.rayo",
    }

    nl = name.lower()
    if nl not in light_map:
        opts = ", ".join(light_map.keys())
        await send(chat_id,
                   "\u274c Habitacion '{}' no encontrada.\nOpciones: {}".format(
                       name, opts))
        return

    if action not in ("on", "off", "toggle"):
        await send(chat_id,
                   "Uso: /habitacion {} on|off|toggle".format(name))
        return

    target = light_map[nl]
    sc, bd = await ha("GET", "/states/{}".format(target))
    if sc != 200 or not isinstance(bd, dict):
        await send(chat_id, "\u274c No pude leer {}.".format(target))
        return

    cur = bd.get("state", "off")
    if action == "toggle":
        action = "off" if cur == "on" else "on"

    act = "turn_on" if action == "on" else "turn_off"
    await ha("POST", "/services/light/{}".format(act),
             {"entity_id": target})
    emoji = "\U0001f4a1" if action == "on" else "\U0001f303"
    locale_map = {
        "garaje": "Garaje", "grout": "Grout", "c": "Ventana C",
        "t": "Ventana T", "frega": "Fregadero",
        "fondo": "Fondo", "rayo": "Rayo",
    }
    await send(chat_id,
               "{} {} <b>{}</b>".format(
                   emoji, locale_map.get(nl, nl),
                   "ENCENDIDA" if action == "on" else "APAGADA"))


async def cmd_cine(chat_id: int) -> None:
    await ha("POST", "/services/input_boolean/turn_on",
             {"entity_id": "input_boolean.sync_manual_night_mode"})
    for c in ["cover.vesti_garaje_cortina", "cover.ventana_c_cortina"]:
        await ha("POST", "/services/cover/close_cover",
                 {"entity_id": c})
    await ha("POST", "/services/light/turn_off",
             {"entity_id": "light.rayo"})
    await send(chat_id,
               "\U0001f3a5 <b>Modo CINE</b> activado.\n"
               "Luces OFF · Cortinas CERRADAS · "
               "Disfruta la pelicula 🍿")


async def cmd_fiesta(chat_id: int) -> None:
    await ha("POST", "/services/input_boolean/turn_on",
             {"entity_id": "input_boolean.party_mode_enabled"})
    await send(chat_id,
               "\U0001f389 <b>Modo FIESTA</b> activado!\n"
               "Pasa buena noche 🤙")


async def cmd_noche(chat_id: int) -> None:
    await ha("POST", "/services/script/turn_on",
             {"entity_id": "script.sync_activar_noche"})
    await send(chat_id,
               "\U0001f319 <b>Modo NOCHE</b> activado.\n"
               "Buenas noches 🌛")


async def cmd_seguridad(chat_id: int) -> None:
    ents = {
        "input_boolean.security_mode_armed":
            "\U0001f510 Alarma armada",
        "input_boolean.security_mode_enabled":
            "\U0001f6e1\ufe0f Seguridad habilitada",
        "input_boolean.camera_recording_enabled":
            "\U0001f4f9 Grabacion camaras",
    }
    lines: List[str] = ["\U0001f6e1\ufe0f <b>Estado Seguridad</b>\n"]
    for eid, label in ents.items():
        sc, bd = await ha("GET", "/states/{}".format(eid))
        if sc == 200 and isinstance(bd, dict):
            v = bd.get("state", "?")
        else:
            v = "?"
        ok = "\u2705" if v == "on" else "\u274c"
        lines.append("  {}  {}: <b>{}</b>".format(ok, label, v.upper()))
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_energia(chat_id: int) -> None:
    lines: List[str] = ["\u26a1 <b>Consumo Electrico</b>\n"]
    sc, bd = await ha("GET", "/states/sensor.medidor_electrico_potencia")
    if sc == 200 and isinstance(bd, dict):
        lines.append(
            "  Potencia actual: <b>{} W</b>".format(bd.get("state", "?")))
    else:
        lines.append("  Potencia: N/A")
    sc2, bd2 = await ha("GET", "/states/sensor.home_assistant_energy")
    if sc2 == 200 and isinstance(bd2, dict):
        lines.append(
            "  Consumo hoy: <b>{}</b>".format(bd2.get("state", "?")))
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_clima(chat_id: int) -> None:
    lines: List[str] = ["\u26c5 <b>Clima Interior</b>\n"]
    targets: List[Tuple[str, str, str]] = [
        ("sensor.temperature_temperatura", "Temp actual", "\u00b0C"),
        ("sensor.temperature_humedad", "Humedad", "%"),
    ]
    for eid, label, unit in targets:
        sc, bd = await ha("GET", "/states/{}".format(eid))
        if sc == 200 and isinstance(bd, dict):
            v = bd.get("state", "?")
        else:
            v = "?"
        lines.append("  {}: <b>{} {}</b>".format(label, v, unit))
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_personas(chat_id: int) -> None:
    lines: List[str] = ["\U0001f465 <b>Personas en casa</b>\n"]
    people: List[Tuple[str, str]] = [
        ("person.david_nows", "David"),
        ("person.neo44hd", "Neo44HD"),
    ]
    for eid, name in people:
        sc, bd = await ha("GET", "/states/{}".format(eid))
        if sc == 200 and isinstance(bd, dict):
            st = bd.get("state", "?")
        else:
            st = "?"
        ico = "\U0001f3e0" if st == "home" else "\U0001f6b6"
        lines.append("  {}  {}: {}".format(ico, name, st))
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_persianas(chat_id: int, action: str,
                        name: Optional[str] = None) -> None:
    covers: Dict[str, str] = {
        "garaje": "cover.vesti_garaje_cortina",
        "grout": "cover.vesti_grout_cortina",
        "c": "cover.ventana_c_cortina",
        "t": "cover.ventana_t_cortina",
    }

    if not action:
        lines: List[str] = ["\U0001f5bc\ufe0f <b>Estado Persianas</b>\n"]
        for n, eid in covers.items():
            sc, bd = await ha("GET", "/states/{}".format(eid))
            if sc == 200 and isinstance(bd, dict):
                st = bd.get("state", "?").capitalize()
            else:
                st = "?"
            lines.append("  {}: {}".format(n, st))
        await send(chat_id, "\n".join(lines), parse_mode="HTML")
        return

    amap: Dict[str, str] = {
        "up": "open_cover", "down": "close_cover", "stop": "stop_cover"
    }
    act = amap.get(action.lower(), "open_cover")
    chosen = [eid for n, eid in covers.items()
              if name is None or n == name.lower()]

    if not chosen:
        opts = ", ".join(covers.keys())
        await send(chat_id,
                   "\u274c Persiana '{}' no encontrada. "
                   "Opciones: {}".format(name, opts))
        return

    for eid in chosen:
        await ha("POST", "/services/cover/{}".format(act),
                 {"entity_id": eid})
    accion_map = {
        "open_cover": "ABIERTAS",
        "close_cover": "CERRADAS",
        "stop_cover": "PARADAS",
    }
    await send(chat_id,
               "\U0001f5bc\ufe0f Persianas <b>{}</b>".format(
                   accion_map.get(act, "actualizadas")))


async def cmd_camara(chat_id: int) -> None:
    cams: List[Tuple[str, str]] = [
        ("Timbro", "camera.timbro_hack"),
        ("Seguridad", "camera.security_camera"),
        ("HD Mini", "camera.hdmini_camera"),
        ("El Ojo", "camera.el_ojo"),
    ]
    lines: List[str] = ["\U0001f4f7 <b>Estado Camaras</b>\n"]
    for name, eid in cams:
        sc, bd = await ha("GET", "/states/{}".format(eid))
        if isinstance(bd, dict):
            state = bd.get("state", "")
        else:
            state = ""
        if sc == 200 and state == "streaming":
            st = "\U0001f4f9 Streaming"
        else:
            st = "\u23f8 Inactiva"
        lines.append("  {}: {}".format(name, st))
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_puertas(chat_id: int) -> None:
    lines: List[str] = ["\U0001f6aa <b>Estado Puertas/Ventanas</b>\n"]
    sensors: List[Tuple[str, str]] = [
        ("binary_sensor.puerta_principal_puerta", "Puerta Principal"),
        ("binary_sensor.puerta_terraza_puerta", "Puerta Terraza"),
    ]
    for eid, label in sensors:
        sc, bd = await ha("GET", "/states/{}".format(eid))
        if sc == 200 and isinstance(bd, dict):
            v = bd.get("state", "?")
        else:
            v = "?"
        if v == "on":
            ico = "\U0001f6a8"
            estado = "ABIERTA"
        else:
            ico = "\U0001f512"
            estado = "CERRADA"
        lines.append("  {}  {}: <b>{}</b>".format(ico, label, estado))
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_gato(chat_id: int) -> None:
    sc, bd = await ha("GET", "/states/sensor.grout_pipet_peso_del_gato")
    if sc == 200 and isinstance(bd, dict):
        peso = bd.get("state", "?")
        await send(chat_id,
                   "\U0001f408 <b>Peso del Gato (Grout)</b>\n"
                   "  Peso actual: <b>{} g</b>".format(peso))
    else:
        await send(chat_id, "\U0001f408 No pude leer el peso del gato.")


async def cmd_notificar(chat_id: int, text: str) -> None:
    if not text:
        await send(chat_id, "Uso: /notificar <texto>")
        return
    await ha("POST", "/services/persistent_notification/create",
             {"title": "BrainBot",
              "message": text,
              "notification_id": "brainbot_msg"})
    await send(chat_id,
               "\U0001f4e2 Notificacion: <b>{}</b>".format(text),
               parse_mode="HTML")


async def cmd_reboot(chat_id: int) -> None:
    await send(chat_id, "\U0001f504 Reiniciando Home Assistant...")
    await ha("POST", "/services/homeassistant/restart")
    await send(chat_id,
               "\u2705 Reinicio lanzado. HA volvera en ~1 minuto.")


async def cmd_estado(chat_id: int) -> None:
    ha_ok = "✅"
    try:
        sc, _ = await ha("GET", "/states/sensor.temperature_temperatura")
        if sc != 200:
            ha_ok = "❌"
    except Exception:
        ha_ok = "❌"

    ollama_ok = "✅" if OLLAMA_URL else "⚠️?"
    await send(chat_id,
        "<b>BrainBot v4.0</b>\n"
        "✉ Telegram: conectado\n"
        "🏠 HA API: {}\n"
        "🦙 Ollama: {}\n"
        "🧠 Modelo: {}\n"
        "👥 Chats en memoria: {}\n"
        "\u23f0 {}".format(
            ha_ok, ollama_ok,
            OLLAMA_MODEL, len(memory),
            dt.now().strftime("%d/%m/%Y %H:%M:%S")),
        parse_mode="HTML")


async def cmd_version(chat_id: int) -> None:
    await send(chat_id,
               "🧠 BrainBot v4.0 · {} · Modelo: {}".format(
                   dt.now().strftime("%Y-%m-%d %H:%M"),
                   OLLAMA_MODEL))


async def cmd_memoria(chat_id: int, action: Optional[str] = None) -> None:
    if action == "off":
        clear_context(chat_id)
        await send(chat_id, "\U0001f9e0 Memoria borrada.")
        return

    ctx = get_context(chat_id)
    if not ctx:
        await send(chat_id,
                   "\U0001f9e0 Memoria vacia para este chat.")
        return

    lines: List[str] = ["\U0001f9e0 <b>Memoria de conversacion</b>\n"]
    for i, m in enumerate(ctx[-10:], 1):
        icon = "\U0001f464" if m["role"] == "user" else "\U0001f916"
        lines.append("  {} [{}] {}".format(
            icon, m["role"], m["content"][:120]))
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_sync(chat_id: int) -> None:
    """Muestra estado del pipeline documental / fuerza sync."""
    try:
        await ha("POST", "/services/homeassistant/update_entity",
                 {"entity_id": "sensor.sync_pipeline_status"})
    except Exception:
        pass
    sc, bd = await ha("GET", "/states/sensor.sync_pipeline_status")
    if sc == 200 and isinstance(bd, dict):
        status = bd.get("state", "Desconocido")
        attrs = bd.get("attributes", {})
        docs = attrs.get("documents_processed", "?")
        total = attrs.get("total_documents", "?")
        last_run = attrs.get("last_run", "?")
        await send(chat_id,
            "\U0001f680 <b>Pipeline Documental</b>\n"
            f"Estado: <b>{status}</b>\n"
            f"Documentos: {docs}/{total}\n"
            f"Ultima ejecucion: {last_run}",
            parse_mode="HTML")
    else:
        await send(chat_id,
            "\u2753 <b>Sync:</b> entidad sensor.sync_pipeline_status no encontrada.\n"
            "Ejecuta /sync para forzar actualizacion.")


async def cmd_escenas(chat_id: int) -> None:
    """Lista las escenas disponibles y permite activarlas."""
    sc, bd = await ha("GET", "/states")
    if sc != 200 or not isinstance(bd, list):
        await send(chat_id, "\u274c No pude obtener las escenas.")
        return
    escenas = [(e["entity_id"], e["attributes"].get("friendly_name", e["entity_id"]))
               for e in bd if e["entity_id"].startswith("scene.")]
    if not escenas:
        await send(chat_id, "\u26a0\ufe0f No hay escenas encontradas.")
        return
    lines = ["\U0001f3ad <b>Escenas disponibles</b>\n"]
    for eid, ename in sorted(escenas, key=lambda x: x[1]):
        lines.append(f"  \U0001f535 /scene {eid.replace('scene.', '')} — {ename}")
    lines.append("\nEscribe <code>/scene &lt;nombre&gt;</code> para activar.")
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_automatizaciones(chat_id: int) -> None:
    """Lista las automatizaciones y permite activar/desactivar."""
    sc, bd = await ha("GET", "/states")
    if sc != 200 or not isinstance(bd, list):
        await send(chat_id, "\u274c No pude obtener las automatizaciones.")
        return
    autos = [(e["entity_id"], e["attributes"].get("friendly_name", e["entity_id"]), e["state"])
             for e in bd if e["entity_id"].startswith("automation.") and not e["entity_id"].startswith("automation.sync")]
    if not autos:
        await send(chat_id, "\u26a0\ufe0f No hay automatizaciones encontradas.")
        return
    lines = ["\u2699\ufe0f <b>Automatizaciones</b>\n"]
    for aid, aname, astate in sorted(autos, key=lambda x: x[1]):
        icon = "\U0001f535" if astate == "on" else "\U0001f534"
        lines.append(f"  {icon} <code>{aid.replace('automation.', '')}</code> — {aname} [{astate}]")
    lines.append("\nPulsa /auto &lt;nombre&gt; para activar/desactivar.")
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_logs(chat_id: int) -> None:
    """Muestra los ultimos logs de Home Assistant."""
    sc, bd = await ha("GET", "/logs/homeassistant.core")
    lines = ["\U0001f4cb <b>Ultimos Logs de HA</b>\n"]
    if sc == 200:
        if isinstance(bd, str):
            for line in bd.strip().split("\n")[-15:]:
                lines.append(f"  <code>{line[:120]}</code>")
        elif isinstance(bd, dict):
            for lvl, entries in bd.items():
                if isinstance(entries, list):
                    for entry in entries[-5:]:
                        lines.append(f"  <code>{lvl}: {str(entry)[:100]}</code>")
        else:
            lines.append("  Sin datos.")
    else:
        lines.append("  No se pudieron obtener logs.")
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_modelo(chat_id: int) -> None:
    """Muestra el modelo actual y opciones para cambiarlo."""
    lines = [
        "\U0001f9e0 <b>Modelo IA (Ollama)</b>\n",
        f"Actual: <b>{OLLAMA_MODEL}</b>\n\n",
        "Modelos disponibles:",
        "  /modelo llama3.1          — Llama 3.1 (8B)",
        "  /modelo llama3.1:70b      — Llama 3.1 (70B)",
        "  /modelo mistral           — Mistral 7B",
        "  /modelo phi3              — Phi-3 Mini",
        "  /modelo codellama:34b     — Codellama 34B",
        "  /modelo neural-chat       — Neural 8B Chat",
    ]
    await send(chat_id, "\n".join(lines), parse_mode="HTML")


async def cmd_modelo_set(chat_id: int, model: str) -> None:
    """Cambia el modelo de Ollama."""
    global OLLAMA_MODEL
    old = OLLAMA_MODEL
    OLLAMA_MODEL = model
    await send(chat_id,
        "\U0001f9e0 <b>Modelo IA cambiado</b>\n"
        f"Antes: <b>{old}</b>\n"
        f"Ahora: <b>{model}</b>",
        parse_mode="HTML")


async def cmd_scene_activate(chat_id: int, scene_name: str) -> None:
    """Activa una escena por nombre."""
    entity_id = f"scene.{scene_name}"
    sc, bd = await ha("GET", f"/states/{entity_id}")
    if sc != 200:
        await send(chat_id, f"\u274c Escena <code>{scene_name}</code> no encontrada.")
        return
    await ha("POST", "/services/scene/turn_on", {"entity_id": entity_id})
    await send(chat_id,
        "\U0001f3ad <b>Escena activada:</b>\n"
        f"<code>{scene_name}</code>",
        parse_mode="HTML")


async def cmd_auto_toggle(chat_id: int, auto_name: str) -> None:
    """Activa/desactiva una automatizacion por nombre."""
    entity_id = f"automation.{auto_name}"
    sc, bd = await ha("GET", f"/states/{entity_id}")
    if sc != 200:
        await send(chat_id, f"\u274c Automatizacion <code>{auto_name}</code> no encontrada.")
        return
    cur_state = bd.get("state", "off") if isinstance(bd, dict) else "off"
    new_state = "off" if cur_state == "on" else "on"
    act = "turn_on" if new_state == "on" else "turn_off"
    await ha("POST", f"/services/automation/{act}", {"entity_id": entity_id})
    emoji_auto2 = "\U0001f535" if new_state == "on" else "\U0001f534"
    await send(chat_id,
        f"{emoji_auto2} <b>{auto_name}</b> → <b>{new_state.upper()}</b>",
        parse_mode="HTML")




# ══════════════════════════════════════════════════════════════
#  MENU INTERACTIVO — SUPERPODERES TELEGRAM
# ══════════════════════════════════════════════════════════════

async def set_bot_commands() -> None:
    """Registra los comandos del bot en Telegram (aparecen en / y @)."""
    commands = [
        {"command": "start", "description": "Iniciar bot y ver menu de superpoderes"},
        {"command": "help", "description": "Ver todos los comandos disponibles"},
        {"command": "menu", "description": "Menu interactivo de superpoderes"},
        {"command": "home", "description": "Estado general de la casa"},
        {"command": "luz", "description": "Control luz principal (on|off|toggle)"},
        {"command": "luces", "description": "Control todas las luces (on|off|toggle)"},
        {"command": "habitacion", "description": "Control luz por habitacion"},
        {"command": "cine", "description": "Activar modo cine"},
        {"command": "fiesta", "description": "Activar modo fiesta"},
        {"command": "noche", "description": "Activar modo noche"},
        {"command": "seguridad", "description": "Estado del sistema de seguridad"},
        {"command": "energia", "description": "Consumo electrico actual"},
        {"command": "clima", "description": "Temperatura y humedad interior"},
        {"command": "persianas", "description": "Abrir, cerrar o parar persianas"},
        {"command": "camara", "description": "Estado de las camaras"},
        {"command": "personas", "description": "Quien esta en casa"},
        {"command": "puertas", "description": "Estado de puertas y ventanas"},
        {"command": "gato", "description": "Peso del gato Grout"},
        {"command": "memoria", "description": "Ver o borrar memoria del chat"},
        {"command": "notificar", "description": "Enviar notificacion a Home Assistant"},
        {"command": "reboot", "description": "Reiniciar Home Assistant"},
        {"command": "estado", "description": "Verificar estado del bot y conexiones"},
        {"command": "escenas", "description": "Listar y activar escenas de HA"},
        {"command": "automatizaciones", "description": "Estado de automatizaciones (on/off)"},
        {"command": "script", "description": "Ejecutar un script de HA"},
        {"command": "servicio", "description": "Llamar un servicio HA directamente"},
        {"command": "logs", "description": "Ultimos logs de Home Assistant"},
        {"command": "modelo", "description": "Cambiar o ver modelo de IA (Ollama)"},
        {"command": "sync", "description": "Fuerza sync / ver estado pipeline documental"},
    ]
    try:
        await tg("setMyCommands", commands=json.dumps(commands))
        logger.info("Comandos registrados en Telegram: %d", len(commands))
    except Exception as e:
        logger.error("Error registrando comandos: %s", e)


async def _cb_reply(cb: dict, text: str, parse_mode: str = "HTML") -> None:
    """Responde a un callback editando el mensaje (sin markup nuevo)."""
    cb_id = cb.get("id", "")
    cid = cb["message"]["chat"]["id"]
    mid = cb["message"]["message_id"]
    await tg("answerCallbackQuery", callback_query_id=cb_id)
    await tg("editMessageText",
             chat_id=cid, message_id=mid,
             text=text, parse_mode=parse_mode)


async def _cb_reply_markup(cb: dict, text: str, markup: dict,
                           parse_mode: str = "HTML") -> None:
    """Responde a un callback editando el mensaje con nuevo teclado."""
    cb_id = cb.get("id", "")
    cid = cb["message"]["chat"]["id"]
    mid = cb["message"]["message_id"]
    await tg("answerCallbackQuery", callback_query_id=cb_id)
    await tg("editMessageText",
             chat_id=cid, message_id=mid,
             text=text, parse_mode=parse_mode,
             reply_markup=json.dumps(markup))


def _back() -> list:
    """Fila con boton de volver al menu."""
    return [{"text": "🔙 Volver al menu", "callback_data": "menu"}]


def _sep() -> list:
    """Fila separadora (botones pequeños)."""
    return [{"text": "---", "callback_data": "null"}]


async def cmd_menu(chat_id: int) -> None:
    """Muestra el menu de superpoderes con teclado inline."""
    keyboard = [
        [
            {"text": "🏠 Estado casa", "callback_data": "estado_casa"},
            {"text": "💡 Control luces", "callback_data": "menu_luces"},
            {"text": "🖼 Persianas", "callback_data": "menu_pers"},
        ],
        [
            {"text": "🎥 Cine", "callback_data": "cine"},
            {"text": "🎉 Fiesta", "callback_data": "fiesta"},
            {"text": "🌙 Noche", "callback_data": "noche"},
        ],
        [
            {"text": "🔐 Seguridad", "callback_data": "menu_seg"},
            {"text": "⚡ Energia", "callback_data": "energia"},
            {"text": "⛅ Clima", "callback_data": "clima"},
        ],
        [
            {"text": "📷 Camaras", "callback_data": "camara"},
            {"text": "👥 Personas", "callback_data": "personas"},
            {"text": "🚪 Puertas/vent", "callback_data": "puertas"},
        ],
        [
            {"text": "🚀 Automatizaciones", "callback_data": "menu_auto"},
            {"text": "🎬 Escenas", "callback_data": "menu_escenas"},
            {"text": "🧠 Memoria", "callback_data": "menu_mem"},
        ],
        [
            {"text": "🤖 Modelo IA", "callback_data": "menu_modelo"},
            {"text": "🔄 Sync", "callback_data": "sync"},
            {"text": "📋 Logs HA", "callback_data": "logs"},
        ],
        [
            {"text": "🔥 Casa especial", "callback_data": "menu_especial"},
            {"text": "⚡ Estado bot", "callback_data": "estado_bot"},
        ],
        [_back()[0]],
    ]
    markup = {"inline_keyboard": keyboard}
    await tg("sendMessage",
             chat_id=chat_id,
             text="\U000000a8 <b>Menu de Superpoderes</b>\nGestiona tu casa desde aqui:\n",
             parse_mode="HTML",
             reply_markup=json.dumps(markup))


async def handle_callback(cb: dict) -> None:
    """Despacha todos los callbacks de teclado inline."""
    global OLLAMA_MODEL
    data = cb.get("data", "")

    # Ignorar callbacks sin datos utiles
    if not data or data == "null":
        await tg("answerCallbackQuery", callback_query_id=cb.get("id", ""))
        return

    # ── Navegacion ──
    if data == "menu":
        chat_id = cb["message"]["chat"]["id"]
        await cmd_menu(chat_id)
        return

    # ── Estado general ──
    if data == "estado_casa":
        await cmd_home(cb["message"]["chat"]["id"])
        return

    # ── Clima ──
    if data == "clima":
        await cmd_clima(cb["message"]["chat"]["id"])
        return

    # ── Energia ──
    if data == "energia":
        await cmd_energia(cb["message"]["chat"]["id"])
        return

    # ── Personas ──
    if data == "personas":
        await cmd_personas(cb["message"]["chat"]["id"])
        return

    # ── Puertas ──
    if data == "puertas":
        await cmd_puertas(cb["message"]["chat"]["id"])
        return

    # ── Gato ──
    if data == "gato":
        await cmd_gato(cb["message"]["chat"]["id"])
        return

    # ── Camara ──
    if data == "camara":
        await cmd_camara(cb["message"]["chat"]["id"])
        return

    # ── Estado bot ──
    if data == "estado_bot":
        await cmd_estado(cb["message"]["chat"]["id"])
        return

    # ── Modos directos ──
    if data == "cine":
        await cmd_cine(cb["message"]["chat"]["id"])
        return
    if data == "fiesta":
        await cmd_fiesta(cb["message"]["chat"]["id"])
        return
    if data == "noche":
        await cmd_noche(cb["message"]["chat"]["id"])
        return
    if data == "reboot":
        await cmd_reboot(cb["message"]["chat"]["id"])
        return

    # ── Submenu: Luces ──
    if data == "menu_luces":
        kb = [
            [
                {"text": "💡 ON", "callback_data": "luces_on"},
                {"text": "🌃 OFF", "callback_data": "luces_off"},
                {"text": "⇆ TOGGLE", "callback_data": "luces_tgl"},
            ],
            [
                {"text": "\U0001f4a1 Rayo", "callback_data": "luz_rayo"},
                {"text": "💡 Fondo", "callback_data": "luz_fondo"},
            ],
            [_sep()],
            [_back()],
        ]
        await _cb_reply_markup(cb,
            "\U0001f4a1 <b>Control de luces</b>\nElige una opcion:",
            {"inline_keyboard": kb})
        return

    if data == "luces_on":
        await cmd_todas_luces(cb["message"]["chat"]["id"], "on")
        await cmd_lights_menu(cb["message"]["chat"]["id"])
        return
    if data == "luces_off":
        await cmd_todas_luces(cb["message"]["chat"]["id"], "off")
        await cmd_lights_menu(cb["message"]["chat"]["id"])
        return
    if data == "luces_tgl":
        await cmd_todas_luces(cb["message"]["chat"]["id"], "toggle")
        await cmd_lights_menu(cb["message"]["chat"]["id"])
        return
    if data == "luz_rayo":
        await cmd_lights(cb["message"]["chat"]["id"], "toggle", "rayo")
        await cmd_lights_menu(cb["message"]["chat"]["id"])
        return
    if data == "luz_fondo":
        await cmd_lights(cb["message"]["chat"]["id"], "toggle", "fondo")
        await cmd_lights_menu(cb["message"]["chat"]["id"])
        return

    # ── Submenu: Seguridad ──
    if data == "menu_seg":
        kb = [
            [
                {"text": "🔐 Armar", "callback_data": "seg_arm"},
                {"text": "🔓 Desarmar", "callback_data": "seg_desarm"},
            ],
            [
                {"text": "📹 Cams ON", "callback_data": "seg_cams_on"},
                {"text": "📹 Cams OFF", "callback_data": "seg_cams_off"},
            ],
            [_sep()],
            [_back()],
        ]
        await _cb_reply_markup(cb,
            "\U0001f6e1\ufe0f <b>Seguridad</b>\nElige una opcion:",
            {"inline_keyboard": kb})
        return

    if data == "seg_arm":
        chat_id = cb["message"]["chat"]["id"]
        await ha("POST", "/services/input_boolean/turn_on",
                 {"entity_id": "input_boolean.security_mode_armed"})
        sc, bd = await ha("GET", "/states/input_boolean.security_mode_armed")
        st = bd.get("state", "?") if sc == 200 else "?"
        ok = "\u2705" if st == "on" else "\u274c"
        await _cb_reply(cb,
            "\U0001f510 <b>Alarma {}</b>\nEstado: <b>{}</b> {}".format(
                "ARMADA" if st == "on" else "DESARMADA", st.upper(), ok))
        return

    if data == "seg_desarm":
        chat_id = cb["message"]["chat"]["id"]
        await ha("POST", "/services/input_boolean/turn_off",
                 {"entity_id": "input_boolean.security_mode_armed"})
        sc, bd = await ha("GET", "/states/input_boolean.security_mode_armed")
        st = bd.get("state", "?") if sc == 200 else "?"
        ok = "\u2705" if st == "off" else "\u274c"
        await _cb_reply(cb,
            "\U0001f512 <b>Alarma {}</b>\nEstado: <b>{}</b> {}".format(
                "DESARMADA" if st == "off" else "ARMADA", st.upper(), ok))
        return

    if data == "seg_cams_on":
        await ha("POST", "/services/input_boolean/turn_on",
                 {"entity_id": "input_boolean.camera_recording_enabled"})
        await _cb_reply(cb, "\U0001f4f9 <b>Grabacion camaras ON</b>")
        return

    if data == "seg_cams_off":
        await ha("POST", "/services/input_boolean/turn_off",
                 {"entity_id": "input_boolean.camera_recording_enabled"})
        await _cb_reply(cb, "\U0001f4f9 <b>Grabacion camaras OFF</b>")
        return

    # ── Submenu: Persianas ──
    if data == "menu_pers":
        kb = [
            [
                {"text": "🔼 Subir", "callback_data": "pers_up"},
                {"text": "🔽 Bajar", "callback_data": "pers_down"},
                {"text": "⏸ Parar", "callback_data": "pers_stop"},
            ],
            [
                {"text": "Garage", "callback_data": "pers_garaje"},
                {"text": "Grout", "callback_data": "pers_grout"},
                {"text": "Vent C", "callback_data": "pers_c"},
                {"text": "Vent T", "callback_data": "pers_t"},
            ],
            [_sep()],
            [_back()],
        ]
        await _cb_reply_markup(cb,
            "\U0001f5bc\ufe0f <b>Persianas</b>\nElige una opcion:",
            {"inline_keyboard": kb})
        return

    if data == "pers_up":
        await cmd_persianas(cb["message"]["chat"]["id"], "up")
        await _cb_reply(cb, "\u2b06\ufe0f <b>Persianas ABIERTAS</b>")
        return
    if data == "pers_down":
        await cmd_persianas(cb["message"]["chat"]["id"], "down")
        await _cb_reply(cb, "\u2b07\ufe0f <b>Persianas CERRADAS</b>")
        return
    if data == "pers_stop":
        await cmd_persianas(cb["message"]["chat"]["id"], "stop")
        await _cb_reply(cb, "\u23f8\ufe0f <b>Persianas PARADAS</b>")
        return

    for name, cb_data in [("garaje", "pers_garaje"), ("grout", "pers_grout"),
                           ("c", "pers_c"), ("t", "pers_t")]:
        if data == cb_data:
            await cmd_persianas(cb["message"]["chat"]["id"], "up", name)
            await _cb_reply(cb,
                "\U0001f5bc\ufe0f Persiana <b>{}</b> ABIERTA".format(
                    name.upper()))
            return

    # ── Submenu: Automatizaciones ──
    if data == "menu_auto":
        chat_id = cb["message"]["chat"]["id"]
        sc, bd = await ha("GET", "/states")
        if sc != 200 or not isinstance(bd, list):
            await _cb_reply(cb, "\u274c No pude obtener las automatizaciones.")
            return
        autos = [(e["entity_id"], e["attributes"].get("friendly_name", e["entity_id"]))
                 for e in bd if e["entity_id"].startswith("automation.") and not e["entity_id"].startswith("automation.sync")]
        if not autos:
            await _cb_reply(cb, "\u26a0\ufe0f No hay automatizaciones encontradas.")
            return
        kb = []
        emoji_auto = "\U0001f535"
        for aid, aname in sorted(autos, key=lambda x: x[1])[:12]:
            kb.append([{"text": f"{emoji_auto} {aname}", "callback_data": f"auto_toggle {aid}"}])
        kb.append([_back()[0]])
        await _cb_reply_markup(cb,
            "\u2699\ufe0f <b>Automatizaciones</b>\n"
            "Pulsa para activar/desactivar:\n"
            "Azul = ON, Rojo = OFF",
            {"inline_keyboard": kb})
        return

    if data.startswith("auto_toggle "):
        parts = data.split(" ", 1)
        if len(parts) == 2:
            aid = parts[1]
            sc, bd = await ha("GET", f"/states/{aid}")
            if sc == 200 and isinstance(bd, dict):
                cur = bd.get("state", "off")
                new_state = "off" if cur == "on" else "on"
                act = "turn_on" if new_state == "on" else "turn_off"
                await ha("POST", f"/services/automation/{act}",
                         {"entity_id": aid})
                emoji = "\U0001f535" if new_state == "on" else "\U0001f534"
                await _cb_reply(cb,
                    f"{emoji} <b>{aid.replace('automation.', '')}</b>\n"
                    f"Cambiado a: <b>{new_state.upper()}</b>")
            else:
                await _cb_reply(cb, f"\u274c Error leyendo {aid}")
        return

    # ── Submenu: Escenas ──
    if data == "menu_escenas":
        chat_id = cb["message"]["chat"]["id"]
        sc, bd = await ha("GET", "/states")
        if sc != 200 or not isinstance(bd, list):
            await _cb_reply(cb, "\u274c No pude obtener las escenas.")
            return
        escenas = [(e["entity_id"], e["attributes"].get("friendly_name", e["entity_id"]))
                   for e in bd if e["entity_id"].startswith("scene.")]
        if not escenas:
            await _cb_reply(cb, "\u26a0\ufe0f No hay escenas encontradas.")
            return
        kb = []
        for eid, ename in sorted(escenas, key=lambda x: x[1])[:12]:
            kb.append([{"text": f"\U0001f3ad {ename}", "callback_data": f"scene_activate {eid}"}])
        kb.append([_back()[0]])
        await _cb_reply_markup(cb,
            "\U0001f3ad <b>Escenas</b>\n"
            "Pulsa para activar una escena:",
            {"inline_keyboard": kb})
        return

    if data.startswith("scene_activate "):
        parts = data.split(" ", 1)
        if len(parts) == 2:
            eid = parts[1]
            await ha("POST", "/services/scene/turn_on", {"entity_id": eid})
            await _cb_reply(cb,
                "\U0001f3ad <b>Escena activada:</b>\n"
                f"{eid.replace('scene.', '')}")
        return

    # ── Submenu: Modelo IA ──
    if data == "menu_modelo":
        kb = [
            [
                {"text": "Llama 3.1 (8B)", "callback_data": "model_set llama3.1"},
                {"text": "Llama 3.1 (70B)", "callback_data": "model_set llama3.1:70b"},
            ],
            [
                {"text": "Mistral 7B", "callback_data": "model_set mistral"},
                {"text": "Phi-3 Mini", "callback_data": "model_set phi3"},
            ],
            [
                {"text": "Codellama 34B", "callback_data": "model_set codellama:34b"},
                {"text": "Neural 8B", "callback_data": "model_set neural-chat"},
            ],
            [_sep()],
            [_back()],
        ]
        await _cb_reply_markup(cb,
            "\U0001f9e0 <b>Modelo IA</b>\nActual: <b>{}</b>\nElige nuevo modelo:".format(OLLAMA_MODEL),
            {"inline_keyboard": kb})
        return

    if data.startswith("model_set "):
        parts = data.split(" ", 1)
        if len(parts) == 2:
            new_model = parts[1]
            old_model = OLLAMA_MODEL
            OLLAMA_MODEL = new_model
            await _cb_reply(cb,
                "\U0001f9e0 <b>Modelo IA cambiado</b>\n"
                f"Antes: <b>{old_model}</b>\n"
                f"Ahora: <b>{new_model}</b>")
        return

    # ── Sync ──
    if data == "sync":
        chat_id = cb["message"]["chat"]["id"]
        try:
            await ha("POST", "/services/homeassistant/update_entity",
                     {"entity_id": "sensor.sync_pipeline_status"})
        except Exception:
            pass
        sc, bd = await ha("GET", "/states/sensor.sync_pipeline_status")
        if sc == 200 and isinstance(bd, dict):
            status = bd.get("state", "Desconocido")
            attrs = bd.get("attributes", {})
            docs = attrs.get("documents_processed", "?")
            total = attrs.get("total_documents", "?")
            last_run = attrs.get("last_run", "?")
            await _cb_reply(cb,
                "\U0001f680 <b>Pipeline Documental</b>\n"
                f"Estado: <b>{status}</b>\n"
                f"Documentos: {docs}/{total}\n"
                f"Ultima ejecucion: {last_run}")
        else:
            await _cb_reply(cb, "\u2753 <b>Sync:</b> entidad sensor.sync_pipeline_status no encontrada.\nEjecuta /sync para forzar.")
        return

    # ── Logs ──
    if data == "logs":
        chat_id = cb["message"]["chat"]["id"]
        try:
            result = await ha("GET", "/logs/homeassistant.core")
            if isinstance(result, tuple):
                sc2, bd2 = result
            else:
                sc2, bd2 = 200, result
            lines = ["\U0001f4cb <b>Ultimos Logs de HA</b>\n"]
            if sc2 == 200 and isinstance(bd2, str):
                for line in bd2.strip().split("\n")[-15:]:
                    lines.append(f"  <code>{line[:120]}</code>")
            elif isinstance(bd2, dict):
                lines.append(f"  {json.dumps(bd2)[:200]}")
            else:
                lines.append("  No hay logs recientes.")
            await _cb_reply(cb, "\n".join(lines), parse_mode="HTML")
        except Exception:
            await _cb_reply(cb, "\u274c No pude obtener logs de HA.")
        return

    # ── Casa especial (solo para diversion) ──
    if data == "menu_especial":
        kb = [
            [
                {"text": "🚨 ALARMA TOTAL", "callback_data": "especial_alarma"},
            ],
            [
                {"text": "😱 Scream mode 😱", "callback_data": "especial_scream"},
            ],
            [_sep()],
            [_back()],
        ]
        await _cb_reply_markup(cb,
            "\U0001f525 <b>CASA ESPECIAL</b>\nSolo valientes...",
            {"inline_keyboard": kb})
        return

    if data == "especial_alarma":
        await ha("POST", "/services/input_boolean/turn_on",
                 {"entity_id": "input_boolean.security_mode_armed"})
        await ha("POST", "/services/input_boolean/turn_on",
                 {"entity_id": "input_boolean.camera_recording_enabled"})
        await _cb_reply(cb,
            "🚨 <b>MODO PANICO</b>\n"
            "Alarma ARMADA + Camaras GRABANDO\n"
            "Dave, alguien ha tocado el menu prohibido...")
        return

    if data == "especial_scream":
        await _cb_reply(cb,
            "\U0001f631 AAAH! \u00a1Me han pulsado el boton prohibido!!\n\n"
            "Ahora mismo NO. Vuelve al menu normal.")
        return


async def cmd_lights_menu(chat_id: int) -> None:
    """Refresca el submenu de luces tras una accion."""
    sc_r, bd_r = await ha("GET", "/states/light.rayo")
    st_r = bd_r.get("state", "off") if sc_r == 200 else "off"
    sc_f, bd_f = await ha("GET", "/states/light.led_bulb_w509z2_2")
    st_f = bd_f.get("state", "off") if sc_f == 200 else "off"

    kb = [
        [
            {"text": "💡 ON", "callback_data": "luces_on"},
            {"text": "🌃 OFF", "callback_data": "luces_off"},
            {"text": "⇆ TOGGLE", "callback_data": "luces_tgl"},
        ],
        [
            {"text": "Rayo ({})".format(st_r), "callback_data": "luz_rayo"},
            {"text": "Fondo ({})".format(st_f), "callback_data": "luz_fondo"},
        ],
        [_sep()],
        [_back()],
    ]
    await tg("sendMessage",
             chat_id=chat_id,
             text="💡 <b>Control de luces</b>",
             parse_mode="HTML",
             reply_markup=json.dumps(kb))


# ─── RUTEO DE MENSAJES ────────────────────────────────────────

async def handle_message(msg: dict) -> None:
    """Procesa un mensaje de Telegram."""
    try:
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "").strip()
        user = msg.get("from", {}).get("first_name", "?")
    except (KeyError, TypeError):
        return

    if not text:
        return

    logger.info("[%s] %s: %s", chat_id, user, text[:100])

    parts = text.split()
    raw_cmd = parts[0].lower() if parts else ""
    args_text = " ".join(parts[1:]) if len(parts) > 1 else ""

    # ── Saludos → respuesta breve + menu ──
    if raw_cmd in GREETINGS:
        await send(chat_id,
                   "\U0001f44b Hola! Soy BrainBot, tu asistente en Chicken Palace.\n\n"
                   "Puedes pedirme <b>cualquier cosa</b>: conversar, preguntar, o controlar la casa.\n"
                   "Escribe <code>/help</code> para ver todos los comandos.",
                   parse_mode="HTML")
        return

    # ── Comandos del sistema ──
    if raw_cmd.startswith("/"):
        dispatch: Dict[str, Any] = {
            "/help":     lambda: cmd_help(chat_id),
            "/ayuda":    lambda: cmd_help(chat_id),
            "/home":     lambda: cmd_home(chat_id),
            "/luz":      lambda: cmd_lights(chat_id, args_text.lower() or "toggle"),
            "/luces":    lambda: cmd_lights(chat_id, args_text.lower() or "toggle"),
            "/todas":    lambda: cmd_todas_luces(chat_id, args_text.lower() or "toggle"),
            "/habitacion": lambda: cmd_habitacion(chat_id, args_text, "toggle"),
            "/cine":     lambda: cmd_cine(chat_id),
            "/fiesta":   lambda: cmd_fiesta(chat_id),
            "/noche":    lambda: cmd_noche(chat_id),
            "/seguridad": lambda: cmd_seguridad(chat_id),
            "/energia":  lambda: cmd_energia(chat_id),
            "/clima":    lambda: cmd_clima(chat_id),
            "/personas": lambda: cmd_personas(chat_id),
            "/puertas":  lambda: cmd_puertas(chat_id),
            "/camara":   lambda: cmd_camara(chat_id),
            "/gato":     lambda: cmd_gato(chat_id),
            "/reboot":   lambda: cmd_reboot(chat_id),
            "/estado":   lambda: cmd_estado(chat_id),
            "/version":  lambda: cmd_version(chat_id),
            "/memoria":  lambda: cmd_memoria(chat_id, args_text.lower() or None),
            "/menu":    lambda: cmd_menu(chat_id),
            "/notificar": lambda: cmd_notificar(chat_id, args_text),
            "/sync":     lambda: cmd_sync(chat_id),
            "/escenas":  lambda: cmd_escenas(chat_id),
            "/automatizaciones": lambda: cmd_automatizaciones(chat_id),
            "/logs":     lambda: cmd_logs(chat_id),
            "/modelo":   lambda: cmd_modelo(chat_id),
        }

        handler = dispatch.get(raw_cmd)
        if handler:
            return await handler()

        if raw_cmd in ("/persiana", "/persianas"):
            args = args_text.lower().split() if args_text else []
            a = args[0] if args else ""
            n = args[1] if len(args) > 1 else None
            return await cmd_persianas(chat_id, a, n)

        if raw_cmd == "/scene" and args_text:
            return await cmd_scene_activate(chat_id, args_text.strip().lower())

        if raw_cmd == "/auto" and args_text:
            return await cmd_auto_toggle(chat_id, args_text.strip().lower())

        if raw_cmd == "/modelo" and args_text:
            return await cmd_modelo_set(chat_id, args_text.strip().lower())

        await send(chat_id,
                   "\u2753 Comando no reconocido. "
                   "Escribe <code>/help</code> para ayuda.",
                   parse_mode="HTML")
        return

    # ── CALLBACK QUERY (teclado inline) ──
    if "callback_query" in msg:
        await handle_callback(msg["callback_query"])
        return

    # ── CONVERSACION LIBRE → OLLAMA ──
    await send(chat_id, "\U0001f914 Pensando...")
    response = await ask_ollama(text, str(chat_id))

    # Limpiar formato para Telegram HTML
    response = (response
                .replace("```\n", "<pre>")
                .replace("\n```", "</pre>")
                .replace("```", ""))
    response = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', response)

    try:
        await send(chat_id, response, parse_mode="HTML")
    except Exception:
        clean = re.sub(r'<[^>]+>', '', response)
        await send(chat_id, clean)


# ─── BUCLE PRINCIPAL ─────────────────────────────────────────

stop_event = asyncio.Event()


def _shutdown(signum: int, frame: Any) -> None:
    logger.info("Senal %d recibida, cerrando...", signum)
    save_memory()
    stop_event.set()


signal.signal(signal.SIGTERM, _shutdown)
signal.signal(signal.SIGINT, _shutdown)


async def main() -> None:
    logger.info("=" * 55)
    logger.info("  BrainBot v4.0 — Multipropósito")
    logger.info("  Modelo: %s @ %s", OLLAMA_MODEL, OLLAMA_URL)
    logger.info("  HA: %s", HASS_URL)
    logger.info("=" * 55)

    load_memory()

    # Registrar comandos en Telegram (menu /)
    await set_bot_commands()

    if HASS_TOKEN:
        try:
            await ha("POST", "/services/homeassistant/turn_on",
                     {"entity_id": "input_boolean.telegram_connected"})
        except Exception:
            pass

    last_update = 0
    logger.info("BrainBot listo. Escuchando mensajes...")

    while not stop_event.is_set():
        try:
            result = await tg("getUpdates",
                              offset=last_update,
                              timeout=LONG_POLL_TIMEOUT)
            if result.get("ok"):
                for upd in result.get("result", []):
                    uid = upd.get("update_id", 0)
                    if uid >= last_update:
                        last_update = uid + 1
                        msg = upd.get("message", {})
                        if msg and "text" in msg:
                            await handle_message(msg)
        except Exception as e:
            if not stop_event.is_set():
                logger.error("Loop error: %s", e)
                await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())