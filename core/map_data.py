"""Static map geometry metadata (viewBox size) used by the home page."""
import json
from functools import lru_cache

from django.conf import settings


@lru_cache(maxsize=1)
def meta():
    with open(settings.BASE_DIR / "seed" / "data" / "iran_provinces.json", encoding="utf-8") as f:
        d = json.load(f)
    return {"width": d["width"], "height": d["height"]}
