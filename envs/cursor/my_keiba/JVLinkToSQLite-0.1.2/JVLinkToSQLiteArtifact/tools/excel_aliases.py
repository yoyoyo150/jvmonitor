from __future__ import annotations

import json
import os
import re
import unicodedata
from typing import Dict, List, Optional, Tuple


HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ALIAS_PATH = os.path.join(HERE, "alias_config.json")


def _nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", s).strip()


def load_alias_config(path: Optional[str] = None) -> Dict[str, List[str]]:
    cfg_path = path or DEFAULT_ALIAS_PATH
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        m = data.get("logical_to_aliases", {})
        # Normalize aliases
        return {k: [_nfkc(x) for x in v] for k, v in m.items()}
    # Minimal fallback
    return {
        "race_id": ["レースID(新)", "レースID", "race_id"],
        "place_r": ["場 R", "場R"],
        "race_name": ["レース名"],
        "surface": ["芝ダ", "馬場"],
        "distance": ["距離"],
        "race_mark_zi": ["R印1", "レース印1"],
        "race_mark_zm": ["レース印2", "R印2"],
        "race_mark_takeuchi": ["レース印3", "R印3"],
        "horse_number": ["番", "馬番"],
        "prev_fin": ["AR", "前着順"],
        "prev_pass_1": ["AX", "前通過1"],
        "prev_pass_2": ["AY", "前通過2"],
        "prev_pass_3": ["AZ", "前通過3"],
        "prev_pass_4": ["BA", "前通過4"],
        "father_type": ["BG", "血統父"],
        "damsire_type": ["CE", "母父"],
        "prev_race_hint": ["CX", "前走レース"],
    }


def build_header_map(df_columns: List[str], aliases: Dict[str, List[str]]) -> Dict[str, Optional[str]]:
    cols_nfkc = [_nfkc(c) for c in map(str, df_columns)]
    result: Dict[str, Optional[str]] = {}
    for logical, names in aliases.items():
        found = None
        # strict match
        for cand in names:
            if cand in cols_nfkc:
                found = df_columns[cols_nfkc.index(cand)]
                break
        # case-insensitive / contains
        if not found:
            for cand in names:
                for i, c in enumerate(cols_nfkc):
                    if c.lower() == cand.lower():
                        found = df_columns[i]
                        break
                if found:
                    break
        if not found:
            for cand in names:
                for i, c in enumerate(cols_nfkc):
                    if c.startswith(cand) or cand in c:
                        found = df_columns[i]
                        break
                if found:
                    break
        result[logical] = found
    return result


# Track (place) mapping: JRA codes
TRACK_ABBR_TO_CODE = {
    "札": "01",  # 札幌
    "函": "02",  # 函館
    "福": "03",  # 福島
    "新": "04",  # 新潟
    "東": "05",  # 東京
    "中": "06",  # 中山（中京は別途『名』）
    "名": "07",  # 中京（名古屋の略と明示あり）
    "京": "08",  # 京都
    "阪": "09",  # 阪神
    "小": "10",  # 小倉
}


def parse_place_r(text: str) -> Tuple[Optional[str], Optional[int]]:
    """Parse "場略+R番号" like "中1", "名11", "中1R", "新 01R" -> (idJyoCD, raceNum).
    Returns (None, None) if not parseable.
    """
    if text is None:
        return None, None
    s = _nfkc(str(text))
    s = s.replace("Ｒ", "R").replace("レース", "R")
    s = s.replace(" ", "")
    m = re.match(r"^([札函福新東中名京阪小])\s*(\d{1,2})(?:R)?$", s)
    if not m:
        return None, None
    abbr, r = m.group(1), int(m.group(2))
    return TRACK_ABBR_TO_CODE.get(abbr), r


def parse_surface(text: str) -> Optional[str]:
    if text is None:
        return None
    s = _nfkc(str(text))
    if s.startswith("芝"):
        return "芝"
    if s.startswith("ダ") or s.lower().startswith("dirt"):
        return "ダ"
    return None


def to_int_or_none(v) -> Optional[int]:
    if v is None:
        return None
    try:
        s = _nfkc(str(v))
        if s.endswith("R"):
            s = s[:-1]
        return int(s)
    except Exception:
        return None


RACE_TIGHTNESS_MAP = {
    "堅い": 0,
    "注意": 1,
    "ﾁｪｯｸ": 2,
    "チェック": 2,
    "注目": 3,
    "大荒": 4,
}


def to_tightness_level(v: Optional[str]) -> Optional[int]:
    if v is None:
        return None
    s = _nfkc(str(v))
    return RACE_TIGHTNESS_MAP.get(s)


def excel_scientific_to_str(v) -> Optional[str]:
    if v is None:
        return None
    s = str(v)
    # Keep as string to avoid loss (e.g., 2.02509E+17)
    return _nfkc(s)















