# -*- coding: utf-8 -*-
"""Service quản lý kịch bản"""

import json
from typing import Optional

from ..models import Script, Action


class ScriptService:
    """Service quản lý lưu/tải kịch bản"""
    
    def save(self, script: Script, filepath: str) -> bool:
        """Lưu kịch bản ra file JSON"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(script.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            raise Exception(f"Không thể lưu file: {e}")
    
    def load(self, filepath: str) -> Script:
        """Tải kịch bản từ file JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Script.from_dict(data)
        except Exception as e:
            raise Exception(f"Không thể tải file: {e}")
