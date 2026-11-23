"""Единая точка запуска Taskich: python main.py"""
import sys
from pathlib import Path

# Позволяет запускать приложение из корня проекта без предварительной установки пакета.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from taskich.main import main  # noqa: E402

if __name__ == "__main__":
    main()
