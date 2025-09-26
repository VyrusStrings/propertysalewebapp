from django import template
from django.utils.translation import get_language
from django.conf import settings
import json, os

register = template.Library()
_CACHE = {}

def _load(lang: str) -> dict:
    if lang in _CACHE:
        return _CACHE[lang]
    path = os.path.join(settings.BASE_DIR, "translations", f"{lang}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            _CACHE[lang] = json.load(f)
    except FileNotFoundError:
        _CACHE[lang] = {}
    return _CACHE[lang]

def _get(d: dict, key: str):
    cur = d
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur

@register.simple_tag(takes_context=True)
def t(context, key: str, default: str = ""):
    lang = (context.get("LANGUAGE_CODE") or get_language() or "en").split("-")[0]
    val = _get(_load(lang), key)
    if val is None and lang != "en":
        val = _get(_load("en"), key)
    return val if val is not None else default
