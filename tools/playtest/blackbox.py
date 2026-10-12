"""Black-box eyes and hands for the Claude playtester (docs/process/05_CLAUDE_PLAYTESTER.md).

The playtester plays REBEL_CELL the way a person does: it looks at the screen and uses the
mouse and keyboard. This tool is the only thing it touches. It knows nothing about the
game's code or scenes: it launches the game quietly (through tools/run_windowed.py, so the
window never takes the desktop's focus, plays no sound and sits off the screen), grabs the
game window's pixels, and posts mouse and keyboard messages to that window.

    python tools/playtest/blackbox.py --session <dir> start --project <worktree or copy>
    python tools/playtest/blackbox.py --session <dir> shot [--name n] [--grid]
    python tools/playtest/blackbox.py --session <dir> click X Y [--right] [--double]
    python tools/playtest/blackbox.py --session <dir> move X Y          (hover)
    python tools/playtest/blackbox.py --session <dir> drag X1 Y1 X2 Y2
    python tools/playtest/blackbox.py --session <dir> scroll X Y N      (N > 0 up, < 0 down)
    python tools/playtest/blackbox.py --session <dir> key NAME [NAME ...] (e.g. space, esc, ctrl+z, q)
    python tools/playtest/blackbox.py --session <dir> type "text"
    python tools/playtest/blackbox.py --session <dir> wait SECONDS
    python tools/playtest/blackbox.py --session <dir> status
    python tools/playtest/blackbox.py --session <dir> stop

Coordinates are pixels of the last screenshot (the game's client area, 1280x720 by
default). Every action but `wait`/`status` ends with a fresh screenshot (shots/NNNN.png)
unless --no-shot is given, and appends one line to <session>/actions.log, so a session can
be replayed by hand and a finding has its exact steps.

Windows only (ctypes, user32/gdi32). Written as a file on purpose: never run Python from
stdin on this machine.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GAME_W, GAME_H = 1280, 720  # client size the playtester sees and clicks in

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32
user32.SetProcessDPIAware()

WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0200, 0x0201, 0x0202
WM_RBUTTONDOWN, WM_RBUTTONUP, WM_LBUTTONDBLCLK = 0x0204, 0x0205, 0x0203
WM_MOUSEWHEEL = 0x020A
WM_KEYDOWN, WM_KEYUP, WM_CHAR = 0x0100, 0x0101, 0x0102
MK_LBUTTON, MK_RBUTTON = 0x0001, 0x0002

VK = {
    "enter": 0x0D, "return": 0x0D, "esc": 0x1B, "escape": 0x1B, "space": 0x20, "tab": 0x09,
    "backspace": 0x08, "delete": 0x2E, "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
    "shift": 0x10, "ctrl": 0x11, "alt": 0x12, "home": 0x24, "end": 0x23,
    "pageup": 0x21, "pagedown": 0x22,
}
for _i in range(1, 13):
    VK["f%d" % _i] = 0x6F + _i


# ---------------------------------------------------------------- processes and windows

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long), ("dwFlags", wt.DWORD),
                ("szExeFile", ctypes.c_char * 260)]


def _children() -> dict[int, list[int]]:
    snap = kernel32.CreateToolhelp32Snapshot(0x2, 0)
    entry = PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
    out: dict[int, list[int]] = {}
    ok = kernel32.Process32First(snap, ctypes.byref(entry))
    while ok:
        out.setdefault(entry.th32ParentProcessID, []).append(entry.th32ProcessID)
        ok = kernel32.Process32Next(snap, ctypes.byref(entry))
    kernel32.CloseHandle(snap)
    return out


def _descendants(pid: int) -> set[int]:
    tree = _children()
    seen, todo = set(), [pid]
    while todo:
        p = todo.pop()
        for c in tree.get(p, []):
            if c not in seen:
                seen.add(c)
                todo.append(c)
    return seen


def _alive(pid: int) -> bool:
    h = kernel32.OpenProcess(0x1000, False, pid)
    if not h:
        return False
    code = wt.DWORD()
    kernel32.GetExitCodeProcess(h, ctypes.byref(code))
    kernel32.CloseHandle(h)
    return code.value == 259


def _find_window(pids: set[int]) -> int:
    found: list[int] = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids and user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
            rect = wt.RECT()
            user32.GetClientRect(hwnd, ctypes.byref(rect))
            if rect.right > 200 and rect.bottom > 200:
                found.append(hwnd)
        return True

    user32.EnumWindows(cb, 0)
    return found[0] if found else 0


# ---------------------------------------------------------------- session

class Session:
    def __init__(self, path: Path):
        self.path = path
        self.state_file = path / "session.json"
        self.state = json.loads(self.state_file.read_text()) if self.state_file.exists() else {}

    def save(self) -> None:
        self.path.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=1))

    def log(self, line: str) -> None:
        with open(self.path / "actions.log", "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (time.strftime("%H:%M:%S"), line))

    def hwnd(self) -> int:
        launcher = self.state.get("launcher_pid", 0)
        if not launcher or not _alive(launcher):
            sys.exit("blackbox: the game is not running (start it, or it crashed: see %s)"
                     % (self.path / "godot.log"))
        hwnd = _find_window(_descendants(launcher))
        if not hwnd:
            sys.exit("blackbox: the game window is not up yet; `wait 2` and retry")
        return hwnd

    def next_shot(self, name: str | None) -> Path:
        shots = self.path / "shots"
        shots.mkdir(parents=True, exist_ok=True)
        n = int(self.state.get("shot_n", 0)) + 1
        self.state["shot_n"] = n
        self.save()
        return shots / ("%04d%s.png" % (n, "_" + name if name else ""))


# ---------------------------------------------------------------- pixels

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wt.DWORD), ("biWidth", ctypes.c_long), ("biHeight", ctypes.c_long),
                ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", ctypes.c_long),
                ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", wt.DWORD),
                ("biClrImportant", wt.DWORD)]


def _client_size(hwnd: int) -> tuple[int, int]:
    r = wt.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    return r.right, r.bottom


def capture(hwnd: int, out: Path, grid: bool) -> Path:
    from PIL import ImageDraw

    img = grab(hwnd)
    if grid:
        d = ImageDraw.Draw(img)
        for x in range(0, GAME_W, 80):
            d.line([(x, 0), (x, GAME_H)], fill=(255, 0, 255), width=1)
            d.text((x + 2, 2), str(x), fill=(255, 0, 255))
        for y in range(0, GAME_H, 80):
            d.line([(0, y), (GAME_W, y)], fill=(255, 0, 255), width=1)
            d.text((2, y + 2), str(y), fill=(255, 0, 255))
    img.save(out)
    return out


def grab(hwnd: int):
    """The game's client area as a GAME_W x GAME_H RGB PIL image."""
    from PIL import Image

    w, h = _client_size(hwnd)
    wdc = user32.GetWindowDC(hwnd)
    mdc = gdi32.CreateCompatibleDC(wdc)
    wr = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(wr))
    ww, wh = wr.right - wr.left, wr.bottom - wr.top
    bmp = gdi32.CreateCompatibleBitmap(wdc, ww, wh)
    gdi32.SelectObject(mdc, bmp)
    # PW_CLIENTONLY | PW_RENDERFULLCONTENT: DWM's copy of the client, works off-screen and for GPU windows
    user32.PrintWindow(hwnd, mdc, 0x1 | 0x2)
    bih = BITMAPINFOHEADER()
    bih.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bih.biWidth, bih.biHeight, bih.biPlanes, bih.biBitCount = ww, -wh, 1, 32
    buf = ctypes.create_string_buffer(ww * wh * 4)
    gdi32.GetDIBits(mdc, bmp, 0, wh, buf, ctypes.byref(bih), 0)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mdc)
    user32.ReleaseDC(hwnd, wdc)
    img = Image.frombuffer("RGBA", (ww, wh), buf, "raw", "BGRA", 0, 1).convert("RGB").crop((0, 0, w, h))
    if (w, h) != (GAME_W, GAME_H):
        img = img.resize((GAME_W, GAME_H))
    return img


# ---------------------------------------------------------------- input

def _to_client(hwnd: int, x: int, y: int) -> tuple[int, int]:
    w, h = _client_size(hwnd)
    return round(x * w / GAME_W), round(y * h / GAME_H)


def _lp(x: int, y: int) -> int:
    return ((y & 0xFFFF) << 16) | (x & 0xFFFF)


def _post(hwnd: int, msg: int, wp: int, lp: int) -> None:
    user32.PostMessageW(hwnd, msg, wp, lp)


def mouse_move(hwnd: int, x: int, y: int, buttons: int = 0) -> None:
    cx, cy = _to_client(hwnd, x, y)
    _post(hwnd, WM_MOUSEMOVE, buttons, _lp(cx, cy))


def click(hwnd: int, x: int, y: int, right: bool, double: bool) -> None:
    cx, cy = _to_client(hwnd, x, y)
    down, up, mk = (WM_RBUTTONDOWN, WM_RBUTTONUP, MK_RBUTTON) if right else (WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON)
    _post(hwnd, WM_MOUSEMOVE, 0, _lp(cx, cy))
    time.sleep(0.05)
    vk = 0x02 if right else VK_LBUTTON
    for i in range(2 if double else 1):
        # Some controls read the live button state (GetKeyState), which posted messages never set.
        with HeldKeys(hwnd, [vk]):
            _post(hwnd, WM_LBUTTONDBLCLK if (double and i == 1) else down, mk, _lp(cx, cy))
            time.sleep(0.06)
        _post(hwnd, up, 0, _lp(cx, cy))
        time.sleep(0.06)


class HeldKeys:
    """Makes the game thread's GetKeyState() report keys as held while posting messages.

    Godot reads the mouse-button mask and modifier keys with GetKeyState(), which posted
    messages never update. Attaching to the game's input thread shares its key-state table
    (focus and the real cursor are untouched), so a posted drag carries the left button and
    a posted ctrl+z carries ctrl.
    """

    def __init__(self, hwnd: int, vks: list[int]):
        self.tid = user32.GetWindowThreadProcessId(hwnd, None)
        self.me = kernel32.GetCurrentThreadId()
        self.vks = vks

    def _set(self, down: bool) -> None:
        state = (ctypes.c_ubyte * 256)()
        user32.GetKeyboardState(state)
        for vk in self.vks:
            state[vk] = 0x80 if down else 0
        user32.SetKeyboardState(state)

    def __enter__(self):
        if not user32.AttachThreadInput(self.me, self.tid, True):
            print("blackbox: AttachThreadInput failed (%d)" % kernel32.GetLastError(), file=sys.stderr)
        self._set(True)
        return self

    def __exit__(self, *_):
        self._set(False)
        user32.AttachThreadInput(self.me, self.tid, False)


VK_LBUTTON = 0x01


def drag(hwnd: int, x1: int, y1: int, x2: int, y2: int) -> None:
    mouse_move(hwnd, x1, y1)
    time.sleep(0.05)
    cx, cy = _to_client(hwnd, x1, y1)
    with HeldKeys(hwnd, [VK_LBUTTON]):
        _post(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, _lp(cx, cy))
        time.sleep(0.15)  # a person holds before moving
        steps = 30
        for i in range(1, steps + 1):
            time.sleep(0.025)
            mouse_move(hwnd, x1 + (x2 - x1) * i // steps, y1 + (y2 - y1) * i // steps, MK_LBUTTON)
        time.sleep(0.2)
        cx, cy = _to_client(hwnd, x2, y2)
        _post(hwnd, WM_LBUTTONUP, 0, _lp(cx, cy))
        time.sleep(0.1)


def scroll(hwnd: int, x: int, y: int, notches: int) -> None:
    mouse_move(hwnd, x, y)
    # WM_MOUSEWHEEL carries screen coordinates
    cx, cy = _to_client(hwnd, x, y)
    pt = wt.POINT(cx, cy)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    step = 120 if notches > 0 else -120
    for _ in range(abs(notches)):
        _post(hwnd, WM_MOUSEWHEEL, (step & 0xFFFF) << 16, _lp(pt.x, pt.y))
        time.sleep(0.05)


def _vk(name: str) -> int:
    name = name.lower()
    if name in VK:
        return VK[name]
    if len(name) == 1:
        return user32.VkKeyScanW(ord(name)) & 0xFF
    sys.exit("blackbox: unknown key %r" % name)


def key(hwnd: int, chord: str) -> None:
    parts = chord.lower().split("+")
    mods, main = parts[:-1], parts[-1]
    vk = _vk(main)
    scan = user32.MapVirtualKeyW(vk, 0)
    with HeldKeys(hwnd, [_vk(m) for m in mods]):
        for m in mods:
            _post(hwnd, WM_KEYDOWN, _vk(m), 1)
        _post(hwnd, WM_KEYDOWN, vk, 1 | (scan << 16))
        if len(main) == 1 and not mods:
            _post(hwnd, WM_CHAR, ord(main), 1 | (scan << 16))
        time.sleep(0.06)
        _post(hwnd, WM_KEYUP, vk, 1 | (scan << 16) | (0xC0 << 24))
        for m in reversed(mods):
            _post(hwnd, WM_KEYUP, _vk(m), 1 | (0xC0 << 24))
        time.sleep(0.1)


def type_text(hwnd: int, text: str) -> None:
    for ch in text:
        _post(hwnd, WM_CHAR, ord(ch), 1)
        time.sleep(0.02)


# ---------------------------------------------------------------- commands

COPY_SKIP = {"saves", ".quiet_runs", ".git", "override.cfg", "import.log"}


def private_copy(build: Path, dest: Path) -> Path:
    """A tester's own copy of the game: hard links to the build's files (no disk cost), real
    copies of .godot/ (the engine may rewrite caches), and no saves/.

    A run from source keeps its saves in the project folder (res://saves), not in user://, so
    testers sharing one folder would share one save. The copy is kept between starts so a
    resumed tester finds its campaign; it is rebuilt only when the build's commit changes.
    """
    import shutil

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=build, capture_output=True, text=True).stdout.strip()
    marker = dest / ".playtest_copy"
    if marker.exists() and marker.read_text().strip() == sha:
        return dest
    if dest.exists():
        keep = dest / "saves"
        if keep.exists() and any(keep.iterdir()):
            sys.exit("blackbox: %s holds saves from build %s; delete it to start over on %s"
                     % (dest, marker.read_text().strip()[:8] if marker.exists() else "?", sha[:8]))
        shutil.rmtree(dest)
    for src_dir, dirs, files in os.walk(build):
        rel = Path(src_dir).relative_to(build)
        dirs[:] = [d for d in dirs if not (rel == Path(".") and d in COPY_SKIP)]
        out_dir = dest / rel
        out_dir.mkdir(parents=True, exist_ok=True)
        real_copy = rel.parts[:1] == (".godot",)
        for f in files:
            if rel == Path(".") and f in COPY_SKIP:
                continue
            src, dst = Path(src_dir) / f, out_dir / f
            if real_copy:
                shutil.copy2(src, dst)
            else:
                try:
                    os.link(src, dst)
                except OSError:
                    shutil.copy2(src, dst)
    marker.write_text(sha)
    return dest


def cmd_start(s: Session, a) -> None:
    project = Path(a.project).resolve()
    if a.private_copy:
        project = private_copy(project, s.path / "game")
    if s.state.get("launcher_pid") and _alive(s.state["launcher_pid"]):
        sys.exit("blackbox: already running (pid %d)" % s.state["launcher_pid"])
    s.path.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(ROOT / "tools" / "run_windowed.py"), "--project", str(project),
           "--log", str(s.path / "godot.log"), "--timeout", str(a.timeout)]
    if a.allow_main_checkout:
        cmd.append("--allow-main-checkout")
    cmd += ["--"] + a.godot_args
    # Each session gets its own user:// (saves, settings, profile): Godot on Windows puts
    # user data under %APPDATA%, so parallel playtesters never share or clobber a save.
    env = dict(os.environ)
    appdata = s.path / "appdata"
    appdata.mkdir(parents=True, exist_ok=True)
    env["APPDATA"] = str(appdata)
    flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    p = subprocess.Popen(cmd, cwd=str(project), creationflags=flags, env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    s.state.update({"launcher_pid": p.pid, "project": str(project), "started": time.time()})
    s.save()
    s.log("start %s" % project)
    deadline = time.time() + 60
    while time.time() < deadline:
        time.sleep(1)
        if not _alive(p.pid):
            sys.exit("blackbox: the game exited during start; see %s" % (s.path / "godot.log"))
        if _find_window(_descendants(p.pid)):
            break
    time.sleep(a.settle)
    print(capture(s.hwnd(), s.next_shot("start"), False))


def cmd_stop(s: Session, _a) -> None:
    launcher = s.state.get("launcher_pid", 0)
    if launcher and _alive(launcher):
        for pid in sorted(_descendants(launcher), reverse=True):  # only this session's own processes
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
        deadline = time.time() + 10
        while _alive(launcher) and time.time() < deadline:
            time.sleep(0.5)
    s.log("stop")
    s.state["launcher_pid"] = 0
    s.save()
    print("stopped")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", required=True, help="folder for this playtest session (shots, logs)")
    ap.add_argument("--no-shot", action="store_true", help="skip the screenshot after an action")
    ap.add_argument("--settle", type=float, default=0.6, help="seconds to let the game react before the shot")
    sub = ap.add_subparsers(dest="cmd", required=True)
    st = sub.add_parser("start")
    st.add_argument("--project", required=True)
    st.add_argument("--timeout", type=float, default=6 * 3600)
    st.add_argument("--allow-main-checkout", action="store_true")
    st.add_argument("--private-copy", action="store_true",
                    help="play a private copy of --project in <session>/game (own saves; use for parallel testers)")
    st.add_argument("godot_args", nargs=argparse.REMAINDER)
    sh = sub.add_parser("shot")
    sh.add_argument("--name")
    sh.add_argument("--grid", action="store_true", help="overlay an 80 px coordinate grid")
    c = sub.add_parser("click")
    c.add_argument("x", type=int)
    c.add_argument("y", type=int)
    c.add_argument("--right", action="store_true")
    c.add_argument("--double", action="store_true")
    m = sub.add_parser("move")
    m.add_argument("x", type=int)
    m.add_argument("y", type=int)
    d = sub.add_parser("drag")
    for n in ("x1", "y1", "x2", "y2"):
        d.add_argument(n, type=int)
    sc = sub.add_parser("scroll")
    sc.add_argument("x", type=int)
    sc.add_argument("y", type=int)
    sc.add_argument("n", type=int)
    k = sub.add_parser("key")
    k.add_argument("names", nargs="+")
    t = sub.add_parser("type")
    t.add_argument("text")
    w = sub.add_parser("wait")
    w.add_argument("seconds", type=float)
    sub.add_parser("status")
    sub.add_parser("stop")
    a = ap.parse_args()
    s = Session(Path(a.session).resolve())

    if a.cmd == "start":
        a.godot_args = a.godot_args[1:] if a.godot_args[:1] == ["--"] else a.godot_args
        cmd_start(s, a)
        return 0
    if a.cmd == "stop":
        cmd_stop(s, a)
        return 0
    if a.cmd == "status":
        launcher = s.state.get("launcher_pid", 0)
        up = bool(launcher and _alive(launcher))
        mins = (time.time() - s.state.get("started", time.time())) / 60
        print("running" if up else "not running", "| shots %d | %.1f min since start" % (s.state.get("shot_n", 0), mins))
        return 0
    if a.cmd == "wait":
        time.sleep(min(a.seconds, 30))
        s.log("wait %.1f" % a.seconds)
        print(capture(s.hwnd(), s.next_shot(None), False))
        return 0

    hwnd = s.hwnd()
    if a.cmd == "shot":
        s.log("shot")
        print(capture(hwnd, s.next_shot(a.name), a.grid))
        return 0
    if a.cmd == "click":
        click(hwnd, a.x, a.y, a.right, a.double)
        s.log("click %d %d%s%s" % (a.x, a.y, " right" if a.right else "", " double" if a.double else ""))
    elif a.cmd == "move":
        mouse_move(hwnd, a.x, a.y)
        s.log("move %d %d" % (a.x, a.y))
    elif a.cmd == "drag":
        drag(hwnd, a.x1, a.y1, a.x2, a.y2)
        s.log("drag %d %d %d %d" % (a.x1, a.y1, a.x2, a.y2))
    elif a.cmd == "scroll":
        scroll(hwnd, a.x, a.y, a.n)
        s.log("scroll %d %d %d" % (a.x, a.y, a.n))
    elif a.cmd == "key":
        for name in a.names:
            key(hwnd, name)
            time.sleep(0.08)
        s.log("key %s" % " ".join(a.names))
    elif a.cmd == "type":
        type_text(hwnd, a.text)
        s.log("type %r" % a.text)
    if not a.no_shot:
        time.sleep(a.settle)
        print(capture(hwnd, s.next_shot(None), False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
