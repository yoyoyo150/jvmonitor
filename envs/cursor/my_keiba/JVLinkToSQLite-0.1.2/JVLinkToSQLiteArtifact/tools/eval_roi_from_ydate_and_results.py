#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import glob
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd  # type: ignore

# Ensure local imports work when executed from elsewhere
import sys, os as _os
_here = _os.path.dirname(_os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.append(_here)

from excel_aliases import (
    build_header_map,
    load_alias_config,
    parse_place_r,
)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Evaluate ROI using yDate Excel (features) + results_YYYYMMDD.csv (payouts)")
    ap.add_argument("--ydate-dir", required=True)
    ap.add_argument("--results-dir", required=True)
    ap.add_argument("--dates", required=True, help="Comma-separated YYYYMMDD")
    ap.add_argument("--out", required=True)
    return ap.parse_args()


def list_excels(ydate_dir: str, d: str) -> List[str]:
    pat = os.path.join(ydate_dir, f"*{d[-4:]}*.xls*")
    files = sorted(glob.glob(pat))
    return files


def normalize_series_rank(s: pd.Series, higher_better: bool = True) -> pd.Series:
    sn = pd.to_numeric(s, errors="coerce")
    if sn.notna().sum() == 0:
        return pd.Series([0.0] * len(s))
    if higher_better:
        r = sn.rank(ascending=False, method="min")
    else:
        r = sn.rank(ascending=True, method="min")
    rmin, rmax = r.min(), r.max()
    if rmin == rmax:
        return pd.Series([1.0] * len(s))
    return 1.0 - (r - rmin) / (rmax - rmin)


def three_pairs(nums: Sequence[int]) -> List[Tuple[int, int]]:
    a, b, c = sorted(nums)
    return [(a, b), (a, c), (b, c)]


def parse_kumi_digits(s: Optional[str]) -> List[int]:
    if not s:
        return []
    parts = re.findall(r"\d+", s)
    return [int(p) for p in parts]


def pairs_equal(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    return sorted(a) == sorted(b)


def triple_equal(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> bool:
    return sorted(a) == sorted(b)


@dataclass
class Totals:
    bets: int = 0
    payout: int = 0
    hits: int = 0


def read_results(results_dir: str, d: str) -> Dict[Tuple[str, str], Dict[str, str]]:
    path = os.path.join(results_dir, f"results_{d}.csv")
    if not os.path.exists(path):
        return {}
    out: Dict[Tuple[str, str], Dict[str, str]] = {}
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            key = (row["track"], row["race"])  # strings
            out[key] = row
    return out


def main() -> int:
    args = parse_args()
    dates = [d.strip() for d in args.dates.split(',') if d.strip()]
    aliases_map = load_alias_config()

    totals = {"umaren": Totals(), "wide": Totals(), "sanrenpuku": Totals()}
    S = {"tot": 0, "win": 0, "pl": 0}
    A = {"tot": 0, "win": 0, "pl": 0}

    for d in dates:
        res_map = read_results(args.results_dir, d)
        excels = list_excels(args.ydate_dir, d)
        for xf in excels:
            df = pd.read_excel(xf)
            hmap = build_header_map(list(map(str, df.columns)), aliases_map)
            pr = hmap.get("place_r")
            hn = hmap.get("horse_number")
            if not pr or not hn:
                continue
            for key, g in df.groupby(pr):
                idJyoCD, raceNum = parse_place_r(str(key))
                if not idJyoCD or not raceNum:
                    continue
                key1 = (idJyoCD, str(raceNum))
                key2 = (idJyoCD, f"{int(raceNum):02d}")
                res = res_map.get(key1) or res_map.get(key2)
                if not res:
                    continue
                # build score from available signals
                score = pd.Series([0.0] * len(g))
                # Prefer ZM(AI) popularity ascending (lower is better)
                zm_col = hmap.get("mark7_zm")
                if zm_col and zm_col in g.columns:
                    score += normalize_series_rank(g[zm_col], higher_better=False).fillna(0) * 0.4
                zi_col = hmap.get("race_mark_zi")
                if zi_col and zi_col in g.columns:
                    score += normalize_series_rank(g[zi_col], higher_better=True).fillna(0) * 0.2
                sp_col = hmap.get("mark2_speed")
                if sp_col and sp_col in g.columns:
                    score += normalize_series_rank(g[sp_col], higher_better=True).fillna(0) * 0.2
                t5 = hmap.get("mark5")
                if t5 and t5 in g.columns:
                    score += normalize_series_rank(g[t5], higher_better=True).fillna(0) * 0.1
                t6 = hmap.get("mark6")
                if t6 and t6 in g.columns:
                    score += normalize_series_rank(g[t6], higher_better=True).fillna(0) * 0.1

                horses = pd.DataFrame({
                    "horse": pd.to_numeric(g[hn], errors="coerce"),
                    "score": score,
                }).dropna(subset=["horse"]).astype({"horse": int})
                if len(horses) < 3:
                    continue
                horses = horses.sort_values(["score", "horse"], ascending=[False, True])
                top6 = horses.head(6)["horse"].tolist()
                top3 = top6[:3]
                pair3 = three_pairs(top3)

                # payouts from results
                # umaren
                uk = parse_kumi_digits(res.get("umaren_kumi")) if res else []
                up = int(res.get("umaren_pay") or 0) if res else 0
                # wide
                wk = [parse_kumi_digits(res.get(f"wide_kumi{i}")) for i in (1, 2, 3)] if res else []
                wp = [int(res.get(f"wide_pay{i}") or 0) for i in (1, 2, 3)] if res else []
                # sanrenpuku
                sk = parse_kumi_digits(res.get("sanrenpuku_kumi")) if res else []
                sp = int(res.get("sanrenpuku_pay") or 0) if res else 0

                # settle
                for pr_ in pair3:
                    totals["umaren"].bets += 100
                    if len(uk) == 2 and pairs_equal(pr_, (uk[0], uk[1])):
                        totals["umaren"].payout += up
                        totals["umaren"].hits += 1
                for pr_ in pair3:
                    totals["wide"].bets += 100
                    for i in range(3):
                        if i < len(wk) and len(wk[i]) == 2 and pairs_equal(pr_, (wk[i][0], wk[i][1])):
                            totals["wide"].payout += wp[i] if i < len(wp) else 0
                            totals["wide"].hits += 1
                            break
                totals["sanrenpuku"].bets += 100
                if len(sk) == 3 and triple_equal((top3[0], top3[1], top3[2]), (sk[0], sk[1], sk[2])):
                    totals["sanrenpuku"].payout += sp
                    totals["sanrenpuku"].hits += 1

                # S/A single/place
                w1 = int(res.get("winner1") or 0) if res else 0
                wset = {int(res.get("winner1") or 0), int(res.get("winner2") or 0), int(res.get("winner3") or 0)} if res else set()
                if top6:
                    S["tot"] += 1
                    if w1 and top6[0] == w1:
                        S["win"] += 1
                    if wset and top6[0] in wset:
                        S["pl"] += 1
                if len(top6) > 1:
                    A["tot"] += 1
                    if w1 and top6[1] == w1:
                        A["win"] += 1
                    if wset and top6[1] in wset:
                        A["pl"] += 1

    # write out
    def roi(t: Totals) -> float:
        return (t.payout / t.bets * 100.0) if t.bets else 0.0

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["type", "bets", "payout", "hits", "ROI(%)"])
        for k in ("umaren", "wide", "sanrenpuku"):
            t = totals[k]
            w.writerow([k, t.bets, t.payout, t.hits, f"{roi(t):.1f}"])
        w.writerow(["S_tan", S["tot"], S["win"], "-", f"{(S['win']/S['tot']*100.0 if S['tot'] else 0):.1f}"])
        w.writerow(["S_fuku", S["tot"], S["pl"], "-", f"{(S['pl']/S['tot']*100.0 if S['tot'] else 0):.1f}"])
        w.writerow(["A_tan", A["tot"], A["win"], "-", f"{(A['win']/A['tot']*100.0 if A['tot'] else 0):.1f}"])
        w.writerow(["A_fuku", A["tot"], A["pl"], "-", f"{(A['pl']/A['tot']*100.0 if A['tot'] else 0):.1f}"])
    print("wrote", os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
