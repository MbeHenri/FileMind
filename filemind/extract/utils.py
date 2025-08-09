from typing import Optional, List
from datetime import datetime


# ---------- Utilitaires ----------
def format_duration(seconds: Optional[float]) -> Optional[str]:
    if not seconds or seconds <= 0:
        return None
    secs = int(round(seconds))
    h, m = divmod(secs, 3600)
    m, s = divmod(m, 60)
    if h:
        return f"{h} h {m:02d} min {s:02d} s"
    return f"{m} min {s:02d} s"


def format_filesize(bytes_: Optional[int]) -> Optional[str]:
    if bytes_ is None or bytes_ < 0:
        return None
    units = ["octets", "Ko", "Mo", "Go", "To"]
    size = float(bytes_)
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    if i == 0:
        return f"{int(size)} {units[i]}"
    return f"{size:.1f} {units[i]}"


def format_channels(n: Optional[int]) -> Optional[str]:
    if not n:
        return None
    if n == 1:
        return "mono (1 canal)"
    if n == 2:
        return "stéréo (2 canaux)"
    return f"{n} canaux"


def format_bitrate(bps: Optional[int]) -> Optional[str]:
    if not bps or bps <= 0:
        return None
    kbps = bps / 1000 if bps > 10000 else bps
    return f"{int(round(kbps))} kb/s"


def format_samplerate(hz: Optional[int]) -> Optional[str]:
    if not hz or hz <= 0:
        return None
    if hz % 1000 == 0:
        return f"{hz // 1000} kHz"
    return f"{hz/1000:.1f} kHz"


def format_list(values: Optional[List[str]]) -> Optional[str]:
    if not values:
        return None
    seen = set()
    cleaned: List[str] = []
    for v in values:
        if v is None:
            continue
        vv = v.strip()
        if vv and vv.lower() not in seen:
            seen.add(vv.lower())
            cleaned.append(vv)
    if not cleaned:
        return None
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} et {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f" et {cleaned[-1]}"


def join_sentences(parts: List[Optional[str]]) -> str:
    return " ".join(p.strip() for p in parts if p and p.strip())


def shorten(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    cut = max_chars - 1
    space = text.rfind(" ", 0, cut)
    if space >= 50:
        return text[:space] + "…"
    return text[:cut] + "…"


def format_timestamp(ts: Optional[int]) -> Optional[str]:
    if not ts or ts <= 0:
        return None
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")


def readContentFile(pathfile: str):
    with open(pathfile, "r") as file:
        content = file.read()

    return content
