"""
YTD Texture Editor - application entry point.

Run with:
    python main.py            (from inside this folder)
    python -m <folder>.main   (from the parent folder)
"""

from __future__ import annotations

import importlib
import os
import sys

# Allow `python main.py` to work without installing the package: put the
# folder that *contains* this one on the import path, so the package can be
# imported by its real directory name (the checkout is named ytd_edtior).
_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
_PKG_NAME = os.path.basename(_PKG_DIR)
_PARENT = os.path.dirname(_PKG_DIR)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)


def load(submodule: str):
    """Import a module of this package whatever the folder is called."""
    last_error = None
    for name in dict.fromkeys((_PKG_NAME, "ytd_editor")):
        try:
            return importlib.import_module("%s.%s" % (name, submodule))
        except ImportError as exc:
            last_error = exc
    raise last_error


REQUIREMENTS = [
    ("PySide6", "PySide6", "the Qt user interface"),
    ("numpy", "numpy", "texture encoding and decoding"),
    ("PIL", "Pillow", "PNG import/export and BC7 decoding"),
]


def check_dependencies():
    """Fail loudly and usefully instead of with a bare ImportError."""
    missing = []
    for module, package, purpose in REQUIREMENTS:
        try:
            __import__(module)
        except ImportError:
            missing.append((package, purpose))
    if not missing:
        return

    lines = ["YTD Texture Editor cannot start - missing dependencies:", ""]
    for package, purpose in missing:
        lines.append("  - %s   (needed for %s)" % (package, purpose))
    lines += ["", "Install everything with:", "",
              "    pip install -r requirements.txt", ""]
    message = "\n".join(lines)

    print(message, file=sys.stderr)
    # If Qt itself is available, show the message in a dialog too.
    if all(p != "PySide6" for p, _ in missing):
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox
            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(None, "Missing dependencies", message)
        except Exception:
            pass
    sys.exit(1)


def main():
    check_dependencies()

    from PySide6.QtWidgets import QApplication

    main_window = load("gui.main_window")
    style = load("gui.style")
    MainWindow = main_window.MainWindow
    DARK_QSS = style.DARK_QSS

    # Qt 6 scales pixmaps for high DPI displays by default.
    app = QApplication(sys.argv)
    app.setApplicationName("YTD Texture Editor")
    app.setOrganizationName("YTD Texture Editor")
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_QSS)

    window = MainWindow()
    window.show()

    # Optional: open a .ytd passed on the command line / dropped on the exe.
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if args and os.path.isfile(args[0]):
        window.load_ytd(args[0])

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
