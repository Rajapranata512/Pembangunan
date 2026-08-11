"""
data/__init__.py — Menggabungkan seluruh data 119 wilayah dari 6 provinsi.
"""
from data.jakarta import REGIONS as _jkt
from data.banten import REGIONS as _btn
from data.jawa_barat import REGIONS as _jbr
from data.jawa_tengah import REGIONS as _jtg
from data.yogyakarta import REGIONS as _diy
from data.jawa_timur import REGIONS as _jtm

ALL_REGIONS: list[dict] = _jkt + _btn + _jbr + _jtg + _diy + _jtm
