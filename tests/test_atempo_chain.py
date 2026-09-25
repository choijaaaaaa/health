# 도입 클립을 2배 넘게 늘릴 때 atempo 범위(0.5~100)를 넘지 않게 여러 단으로 나누는지.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from xray_splice import _atempo_chain  # noqa: E402


def _product(chain: str) -> float:
    out = 1.0
    for part in filter(None, chain.split(",")):
        out *= float(part.split("=")[1])
    return out


def test_below_half_is_split_into_stages():
    chain = _atempo_chain(0.4878)
    assert all(float(p.split("=")[1]) >= 0.5 for p in filter(None, chain.split(",")))
    assert abs(_product(chain) - 0.4878) < 1e-3


def test_normal_and_identity():
    assert _atempo_chain(0.8) == "atempo=0.8000,"
    assert _atempo_chain(1.0) == ""
