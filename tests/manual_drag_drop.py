"""Manual probe: does a file drag over a child widget reach MainWindow?

Qt propagates drag/drop events that a child ignores up the parent chain, so
this checks that the window really ends up handling drags over the canvas, the
texture list, the tool panel, the toolbar and the status bar.

Run from this folder:
    python tests/manual_drag_drop.py

MainWindow.load_ytd is stubbed, so the throwaway .ytd files this creates are
never parsed and no dialog can block the run.
"""

import importlib
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(PKG_DIR))

from PySide6.QtCore import QMimeData, Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import QApplication, QListWidget, QWidget

main_window = importlib.import_module(
    "%s.gui.main_window" % os.path.basename(PKG_DIR))
MainWindow = main_window.MainWindow

TMP = os.path.join(tempfile.gettempdir(), "ytd_drag_probe")
os.makedirs(TMP, exist_ok=True)
FAKE1 = os.path.join(TMP, "probe1.ytd")
FAKE2 = os.path.join(TMP, "probe2.ytd")
TXT = os.path.join(TMP, "notes.txt")
for path in (FAKE1, FAKE2, TXT):
    with open(path, "wb") as handle:
        handle.write(b"not a resource")


KEPT_ALIVE = []          # drag events only hold a raw pointer to their payload


def mime_data(*paths):
    data = QMimeData()
    data.setUrls([QUrl.fromLocalFile(p) for p in paths])
    KEPT_ALIVE.append(data)
    return data


def drag(cls, widget, data):
    """Build the event a real drag would deliver to `widget`."""
    pos = widget.mapToGlobal(widget.rect().center())
    return cls(pos, Qt.CopyAction | Qt.MoveAction, data,
               Qt.LeftButton, Qt.KeyboardModifier())   # no modifiers pressed


def deliver(cls, widget, data):
    """Send one drag event to `widget`, the way the drag pipeline would."""
    event = drag(cls, widget, data)
    QApplication.sendEvent(widget, event)
    return event


def drop_on(widget, data):
    """Deliver a full drag: Qt only routes a drop that an enter announced."""
    deliver(QDragEnterEvent, widget, data)
    return deliver(QDropEvent, widget, data)


failures = []
checked = []


def expect(condition, label):
    checked.append(label)
    if not condition:
        print("FAIL %s" % label)
        failures.append(label)


app = QApplication(sys.argv)
win = MainWindow()
win.resize(1500, 940)
win.show()
app.processEvents()

opened = []
win.load_ytd = opened.append

targets = [win, win.canvas, win.sidebar, win.tools, win.toolbar, win.statusBar()]
targets += [w for w in win.findChildren(QWidget) if w.isVisible()]

print("--- drag enter over the window's widgets offers a drop ---")
seen = set()
for widget in targets:
    label = "the window itself" if widget is win else type(widget).__name__
    if not widget.isVisible() or label in seen:
        continue                      # one probe per widget class is enough
    seen.add(label)
    win.statusBar().clearMessage()
    expect(deliver(QDragEnterEvent, widget, mime_data(FAKE1)).isAccepted()
           and win.statusBar().currentMessage().startswith("Drop to open"),
           "drag enter accepted over %s" % label)

print("--- the rest of the drag/drop paths ---")
expect(deliver(QDragMoveEvent, win.canvas, mime_data(FAKE1)).isAccepted(),
       "drag move keeps the drop armed")

armed = deliver(QDragEnterEvent, win.canvas, mime_data(FAKE1))
expect(armed.dropAction() == Qt.CopyAction,
       "the answer to the source is Copy, so a same-drive drag cannot move "
       "the file out of its folder")

bad = deliver(QDragEnterEvent, win.canvas, mime_data(TXT))
expect(not bad.isAccepted() and not win.statusBar().currentMessage(),
       "a non-.ytd file is refused")
expect(not deliver(QDropEvent, win.canvas, mime_data(TXT)).isAccepted(),
       "and dropping it opens nothing")

ghost = deliver(QDragEnterEvent, win.canvas,
                mime_data(os.path.join(TMP, "gone.ytd")))
expect(not ghost.isAccepted(), "a .ytd path that does not exist is refused")

listing = win.sidebar.findChildren(QListWidget)[0]
dropped = drop_on(listing, mime_data(FAKE1, FAKE2))
expect(dropped.isAccepted() and opened == [FAKE1],
       "dropping two files on the texture list opens only the first")
expect("ignored 1 other" in win.statusBar().currentMessage(),
       "the extra file is reported instead of silently opened")

quoted = mime_data()
quoted.setText('"%s"' % FAKE2)
opened.clear()
expect(drop_on(win.canvas, quoted).isAccepted() and opened == [FAKE2],
       "a quoted path carried as plain text also opens")

print("drag entered over: %s" % ", ".join(sorted(seen)))

print("\n%d checks, %d failed" % (len(checked), len(failures)))
sys.exit(1 if failures else 0)
