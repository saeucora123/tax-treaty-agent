from __future__ import annotations

import shutil
import subprocess
import time
import urllib.error
import urllib.request
from ctypes import WINFUNCTYPE, create_unicode_buffer, windll
from ctypes.wintypes import BOOL, HWND, LPARAM
from contextlib import contextmanager
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterator

import imageio_ffmpeg
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_URL = "http://127.0.0.1:4173/"
BACKEND_HEALTH_URL = "http://127.0.0.1:8000/guided-facts"
LOG_DIR = ROOT / "docs" / "site-assets" / "build-logs"

WINDOW_WIDTH = 1480
WINDOW_HEIGHT = 1040
VIEWPORT_TOP_CROP = 72
DEVICE_SCALE_FACTOR = 2
TARGET_FPS = 30
REALTIME_ANIMATION_FPS = 60
APP_WINDOW_X = 160
APP_WINDOW_Y = 80
CAPTURE_WINDOW_TITLE = "Tax Treaty Agent Walkthrough Capture"
SW_RESTORE = 9


@dataclass
class ManagedProcess:
    process: subprocess.Popen[str]
    started_here: bool
    log_path: Path


def _url_ready(url: str, timeout_seconds: int = 3) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            return 200 <= response.status < 500
    except (urllib.error.URLError, TimeoutError, ValueError):
        return False


def _wait_for_url(url: str, timeout_seconds: int = 45) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if _url_ready(url):
            return
        time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {url}")


def _start_backend() -> ManagedProcess:
    if _url_ready(BACKEND_HEALTH_URL):
        return ManagedProcess(process=None, started_here=False, log_path=LOG_DIR / "backend.log")  # type: ignore[arg-type]

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "backend.log"
    python_path = ROOT / ".venv" / "Scripts" / "python.exe"
    if not python_path.exists():
        raise FileNotFoundError(f"Backend interpreter not found: {python_path}")

    backend_log = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            str(python_path),
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--app-dir",
            "backend",
        ],
        cwd=str(ROOT),
        stdout=backend_log,
        stderr=subprocess.STDOUT,
        text=True,
    )
    _wait_for_url(BACKEND_HEALTH_URL, timeout_seconds=60)
    return ManagedProcess(process=process, started_here=True, log_path=log_path)


def _start_frontend() -> ManagedProcess:
    if _url_ready(FRONTEND_URL):
        return ManagedProcess(process=None, started_here=False, log_path=LOG_DIR / "frontend.log")  # type: ignore[arg-type]

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "frontend.log"
    npm_path = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm_path:
        raise FileNotFoundError("npm not found in PATH")

    frontend_log = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [npm_path, "run", "dev", "--", "--host", "127.0.0.1", "--port", "4173"],
        cwd=str(FRONTEND_DIR),
        stdout=frontend_log,
        stderr=subprocess.STDOUT,
        text=True,
    )
    _wait_for_url(FRONTEND_URL, timeout_seconds=90)
    return ManagedProcess(process=process, started_here=True, log_path=log_path)


@contextmanager
def ensure_local_app_stack() -> Iterator[None]:
    backend = _start_backend()
    frontend = _start_frontend()
    try:
        yield
    finally:
        for managed in (frontend, backend):
            if managed.started_here and managed.process is not None:
                managed.process.terminate()
                try:
                    managed.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    managed.process.kill()


def _chrome_binary() -> str:
    candidates = [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    raise FileNotFoundError("Chrome binary not found")


def _build_driver(headless: bool = True, app_mode_url: str | None = None) -> webdriver.Chrome:
    options = ChromeOptions()
    options.binary_location = _chrome_binary()
    if headless:
        options.add_argument("--headless=new")
    else:
        options.add_argument(f"--window-position={APP_WINDOW_X},{APP_WINDOW_Y}")
    if app_mode_url:
        options.add_argument(f"--app={app_mode_url}")
    options.add_argument("--hide-scrollbars")
    options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
    options.add_argument(f"--force-device-scale-factor={DEVICE_SCALE_FACTOR}")
    options.add_argument("--disable-gpu")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-features=CalculateNativeWinOcclusion")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    if not headless:
        driver.set_window_position(APP_WINDOW_X, APP_WINDOW_Y)
    return driver


CURSOR_INSTALL_SCRIPT = r"""
(() => {
  if (window.__ttaCursorInstalled) return;

  const style = document.createElement("style");
  style.textContent = `
    #tta-cursor {
      position: fixed;
      left: 0;
      top: 0;
      width: 34px;
      height: 34px;
      pointer-events: none;
      z-index: 2147483647;
      transform: translate(-3px, -1px);
    }
    #tta-cursor svg {
      width: 100%;
      height: 100%;
      filter: drop-shadow(0 7px 14px rgba(0, 0, 0, 0.24));
    }
    #tta-cursor svg path.arrow-fill {
      fill: #171717;
    }
    #tta-cursor svg path.arrow-stroke {
      fill: none;
      stroke: rgba(255, 255, 255, 0.85);
      stroke-width: 1.4;
      stroke-linejoin: round;
    }
    #tta-cursor-ring {
      position: fixed;
      left: 0;
      top: 0;
      width: 30px;
      height: 30px;
      margin-left: -15px;
      margin-top: -15px;
      border-radius: 999px;
      border: 2px solid rgba(255, 239, 200, 0.82);
      background: rgba(255, 244, 216, 0.1);
      pointer-events: none;
      z-index: 2147483646;
      opacity: 0;
      transform: scale(0.72);
      transition: none;
      box-shadow: 0 0 0 10px rgba(255, 244, 216, 0.06);
    }
    body::-webkit-scrollbar {
      display: none;
    }
  `;
  document.head.appendChild(style);

  const cursor = document.createElement("div");
  cursor.id = "tta-cursor";
  cursor.innerHTML = `
    <svg viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path class="arrow-fill" d="M4 3L4 28L11.2 21.1L16.4 32L21.8 29.5L16.9 18.9L27.9 18.9L4 3Z"/>
      <path class="arrow-stroke" d="M4 3L4 28L11.2 21.1L16.4 32L21.8 29.5L16.9 18.9L27.9 18.9L4 3Z"/>
    </svg>
  `;

  const ring = document.createElement("div");
  ring.id = "tta-cursor-ring";

  document.body.appendChild(ring);
  document.body.appendChild(cursor);

  window.__ttaSetCursor = (x, y, clickStrength) => {
    cursor.style.left = `${x}px`;
    cursor.style.top = `${y}px`;
    ring.style.left = `${x}px`;
    ring.style.top = `${y}px`;

    if (clickStrength > 0) {
      ring.style.opacity = String(Math.min(0.92, 0.18 + clickStrength * 0.68));
      ring.style.transform = `scale(${0.74 + clickStrength * 0.42})`;
    } else {
      ring.style.opacity = "0";
      ring.style.transform = "scale(0.72)";
    }
  };

  window.__ttaCursorInstalled = true;
})();
"""


def _frames(seconds: float) -> int:
    return max(1, int(round(seconds * TARGET_FPS)))


def _realtime_steps(seconds: float) -> int:
    return max(1, int(round(seconds * REALTIME_ANIMATION_FPS)))


def _capture_frame(driver: webdriver.Chrome, cursor_pos: tuple[float, float], click_strength: float = 0.0) -> Image.Image:
    driver.execute_script(
        "window.__ttaSetCursor(arguments[0], arguments[1], arguments[2]);",
        float(cursor_pos[0]),
        float(cursor_pos[1]),
        float(click_strength),
    )
    png = driver.get_screenshot_as_png()
    image = Image.open(BytesIO(png)).convert("RGBA")
    crop_top = VIEWPORT_TOP_CROP * DEVICE_SCALE_FACTOR
    crop_box = (0, crop_top, WINDOW_WIDTH * DEVICE_SCALE_FACTOR, WINDOW_HEIGHT * DEVICE_SCALE_FACTOR)
    cropped = image.crop(crop_box)
    return cropped.resize((WINDOW_WIDTH, WINDOW_HEIGHT - VIEWPORT_TOP_CROP), Image.Resampling.LANCZOS)


def _element_center(driver: webdriver.Chrome, by: By, value: str) -> tuple[float, float]:
    element = driver.find_element(by, value)
    rect = driver.execute_script(
        """
        const r = arguments[0].getBoundingClientRect();
        return { x: r.left + (r.width / 2), y: r.top + (r.height / 2) };
        """,
        element,
    )
    return float(rect["x"]), float(rect["y"])


def _scroll_center_y(driver: webdriver.Chrome, element) -> float:
    return float(
        driver.execute_script(
            """
            const r = arguments[0].getBoundingClientRect();
            return r.top + (r.height / 2);
            """,
            element,
        )
    )


def _hold(frames: list[Image.Image], frame: Image.Image, count: int) -> None:
    for _ in range(count):
        frames.append(frame.copy())


def _ease(value: float) -> float:
    return 0.5 - 0.5 * __import__("math").cos(__import__("math").pi * value)


def _move_cursor(
    driver: webdriver.Chrome,
    frames: list[Image.Image],
    current: list[float],
    target: tuple[float, float],
    steps: int = 10,
) -> None:
    start_x, start_y = current[0], current[1]
    for index in range(steps):
        t = 0 if steps == 1 else index / (steps - 1)
        eased = _ease(t)
        x = start_x + ((target[0] - start_x) * eased)
        y = start_y + ((target[1] - start_y) * eased)
        current[0], current[1] = x, y
        frames.append(_capture_frame(driver, (x, y)))


def _click_pulse(
    driver: webdriver.Chrome,
    frames: list[Image.Image],
    current: list[float],
    strengths: tuple[float, ...] = (0.28, 0.72, 1.0, 0.55, 0.18),
) -> None:
    for strength in strengths:
        frames.append(_capture_frame(driver, (current[0], current[1]), click_strength=strength))


def _wait_for(driver: webdriver.Chrome, by: By, value: str, timeout: int = 20):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))


def _set_capture_title(driver: webdriver.Chrome) -> None:
    driver.execute_script("document.title = arguments[0];", CAPTURE_WINDOW_TITLE)


def _desktop_scale_factor() -> float:
    return max(1.0, float(windll.shcore.GetScaleFactorForDevice(0)) / 100.0)


def _focus_capture_window() -> None:
    enum_windows = windll.user32.EnumWindows
    get_window_text_length = windll.user32.GetWindowTextLengthW
    get_window_text = windll.user32.GetWindowTextW
    is_window_visible = windll.user32.IsWindowVisible

    matches: list[int] = []

    @WINFUNCTYPE(BOOL, HWND, LPARAM)
    def foreach_window(hwnd, _lparam):
        if not is_window_visible(hwnd):
            return True
        length = get_window_text_length(hwnd)
        if length == 0:
            return True
        buffer = create_unicode_buffer(length + 1)
        get_window_text(hwnd, buffer, length + 1)
        title = buffer.value
        if CAPTURE_WINDOW_TITLE in title:
            matches.append(hwnd)
        return True

    enum_windows(foreach_window, 0)
    hwnd = matches[0] if matches else 0
    if hwnd == 0:
        raise RuntimeError(f"Could not find capture window containing '{CAPTURE_WINDOW_TITLE}'")
    windll.user32.ShowWindow(hwnd, SW_RESTORE)
    windll.user32.BringWindowToTop(hwnd)
    windll.user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)


def _window_capture_metrics(driver: webdriver.Chrome) -> dict[str, int]:
    metrics = driver.execute_script(
        """
        return {
          screenX: Math.round(window.screenX),
          screenY: Math.round(window.screenY),
          outerWidth: Math.round(window.outerWidth),
          outerHeight: Math.round(window.outerHeight),
          innerWidth: Math.round(window.innerWidth),
          innerHeight: Math.round(window.innerHeight),
          devicePixelRatio: window.devicePixelRatio || 1
        };
        """
    )

    border_x = max(0, int(round((metrics["outerWidth"] - metrics["innerWidth"]) / 2)))
    border_bottom = border_x
    border_top = max(0, int(round(metrics["outerHeight"] - metrics["innerHeight"] - border_bottom)))

    desktop_scale = _desktop_scale_factor()
    capture_x = int(round((int(metrics["screenX"]) + border_x) * desktop_scale))
    capture_y = int(round((int(metrics["screenY"]) + border_top) * desktop_scale))
    capture_width = int(round(int(metrics["innerWidth"]) * desktop_scale))
    capture_height = int(round(int(metrics["innerHeight"]) * desktop_scale))

    return {
        "capture_x": capture_x,
        "capture_y": capture_y,
        "width": capture_width,
        "height": capture_height,
    }


@dataclass
class RecordingProcess:
    process: subprocess.Popen[bytes]
    log_path: Path


def _start_window_recording(output_path: Path, metrics: dict[str, int]) -> RecordingProcess:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "walkthrough-ffmpeg.log"
    log_handle = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            ffmpeg_exe,
            "-y",
            "-f",
            "gdigrab",
            "-framerate",
            str(TARGET_FPS),
            "-offset_x",
            str(metrics["capture_x"]),
            "-offset_y",
            str(metrics["capture_y"]),
            "-video_size",
            f"{metrics['width']}x{metrics['height']}",
            "-draw_mouse",
            "0",
            "-i",
            "desktop",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_path),
        ],
        stdin=subprocess.PIPE,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )
    time.sleep(0.6)
    return RecordingProcess(process=process, log_path=log_path)


def _stop_window_recording(recording: RecordingProcess) -> None:
    if recording.process.stdin:
        recording.process.stdin.write(b"q\n")
        recording.process.stdin.flush()
    try:
        recording.process.wait(timeout=20)
    except subprocess.TimeoutExpired:
        recording.process.kill()
        recording.process.wait(timeout=5)
    if recording.process.returncode not in (0, 255):
        raise RuntimeError(f"ffmpeg screen recording failed; see {recording.log_path}")


def _set_cursor_live(driver: webdriver.Chrome, cursor_pos: tuple[float, float], click_strength: float = 0.0) -> None:
    driver.execute_script(
        "window.__ttaSetCursor(arguments[0], arguments[1], arguments[2]);",
        float(cursor_pos[0]),
        float(cursor_pos[1]),
        float(click_strength),
    )


def _sleep_frame() -> None:
    time.sleep(1 / REALTIME_ANIMATION_FPS)


def _hold_live(
    driver: webdriver.Chrome,
    current: list[float],
    seconds: float,
    click_strength: float = 0.0,
) -> None:
    for _ in range(_realtime_steps(seconds)):
        _set_cursor_live(driver, (current[0], current[1]), click_strength=click_strength)
        _sleep_frame()


def _move_cursor_live(
    driver: webdriver.Chrome,
    current: list[float],
    target: tuple[float, float],
    seconds: float,
) -> None:
    start_x, start_y = current[0], current[1]
    steps = _realtime_steps(seconds)
    for index in range(steps):
        t = 0 if steps == 1 else index / (steps - 1)
        eased = _ease(t)
        x = start_x + ((target[0] - start_x) * eased)
        y = start_y + ((target[1] - start_y) * eased)
        current[0], current[1] = x, y
        _set_cursor_live(driver, (x, y))
        _sleep_frame()


def _click_pulse_live(
    driver: webdriver.Chrome,
    current: list[float],
    strengths: tuple[float, ...] = (0.28, 0.72, 1.0, 0.55, 0.18),
) -> None:
    for strength in strengths:
        _set_cursor_live(driver, (current[0], current[1]), click_strength=strength)
        _sleep_frame()


def _set_select_value_live(
    driver: webdriver.Chrome,
    current: list[float],
    element_id: str,
    visible_text: str,
    move_seconds: float = 0.3,
) -> None:
    target = _element_center(driver, By.ID, element_id)
    _move_cursor_live(driver, current, target, seconds=move_seconds)
    _hold_live(driver, current, 0.12)
    element = driver.find_element(By.ID, element_id)
    element.click()
    _click_pulse_live(driver, current, strengths=(0.3, 0.82, 0.46))
    Select(element).select_by_visible_text(visible_text)
    _hold_live(driver, current, 0.2)


def _set_text_input_live(
    driver: webdriver.Chrome,
    current: list[float],
    input_id: str,
    value: str,
    chunks: list[str],
    move_seconds: float = 0.36,
) -> None:
    target = _element_center(driver, By.ID, input_id)
    _move_cursor_live(driver, current, target, seconds=move_seconds)
    _hold_live(driver, current, 0.14)
    element = driver.find_element(By.ID, input_id)
    element.click()
    _click_pulse_live(driver, current)
    _hold_live(driver, current, 0.12)
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.DELETE)
    for chunk in chunks:
        element.send_keys(chunk)
        _hold_live(driver, current, 0.14)
    _hold_live(driver, current, 0.18)


def _smooth_scroll_to_live(
    driver: webdriver.Chrome,
    current: list[float],
    element,
    seconds: float = 0.36,
) -> None:
    target_y = driver.execute_script(
        """
        const rect = arguments[0].getBoundingClientRect();
        const target = window.scrollY + rect.top - 120;
        return Math.max(0, target);
        """,
        element,
    )
    start_y = driver.execute_script("return window.scrollY;")
    steps = _realtime_steps(seconds)
    for index in range(steps):
        t = 0 if steps == 1 else index / (steps - 1)
        eased = _ease(t)
        next_y = start_y + ((target_y - start_y) * eased)
        driver.execute_script("window.scrollTo(0, arguments[0]);", float(next_y))
        _set_cursor_live(driver, (current[0], current[1]))
        _sleep_frame()


def _run_live_walkthrough_sequence(driver: webdriver.Chrome) -> tuple[float, float]:
    current = [220.0, 180.0]
    _hold_live(driver, current, 0.9)

    _set_select_value_live(driver, current, "guided-payer", "CN", move_seconds=0.34)
    _set_select_value_live(driver, current, "guided-payee", "NL", move_seconds=0.3)
    _set_select_value_live(driver, current, "guided-income-type", "dividends", move_seconds=0.3)

    _set_text_input_live(driver, current, "guided-fact-direct_holding_percentage", "30", ["3", "0"], move_seconds=0.42)
    _set_text_input_live(driver, current, "guided-fact-payment_date", "2026-03-01", ["2026", "-03", "-01"], move_seconds=0.34)
    _set_text_input_live(driver, current, "guided-fact-holding_period_months", "14", ["1", "4"], move_seconds=0.3)
    _set_select_value_live(driver, current, "guided-fact-beneficial_owner_confirmed", "yes", move_seconds=0.26)
    _set_select_value_live(driver, current, "guided-fact-pe_effectively_connected", "no", move_seconds=0.26)
    _set_select_value_live(driver, current, "guided-fact-holding_structure_is_direct", "yes", move_seconds=0.26)

    run_button = _wait_for(driver, By.XPATH, "//button[normalize-space()='Run Guided Review']")
    run_target = _element_center(driver, By.XPATH, "//button[normalize-space()='Run Guided Review']")
    _move_cursor_live(driver, current, run_target, seconds=0.38)
    _hold_live(driver, current, 0.18)
    run_button.click()
    _click_pulse_live(driver, current, strengths=(0.32, 0.76, 1.0, 0.5))
    _hold_live(driver, current, 0.75)

    treaty_row = _row_container(driver, "Treaty Provision")
    _smooth_scroll_to_live(driver, current, treaty_row, seconds=0.38)
    treaty_focus = _element_center(driver, By.XPATH, "//div[@class='row-label' and normalize-space()='Treaty Provision']")
    _move_cursor_live(driver, current, treaty_focus, seconds=0.22)
    _hold_live(driver, current, 1.0)

    source_row = _row_container(driver, "Source Chain")
    _smooth_scroll_to_live(driver, current, source_row, seconds=0.34)
    source_focus = _element_center(driver, By.XPATH, "//div[@class='row-label' and normalize-space()='Source Chain']")
    _move_cursor_live(driver, current, source_focus, seconds=0.2)
    _hold_live(driver, current, 1.15)

    handoff_row = _row_container(driver, "Workflow Handoff")
    _smooth_scroll_to_live(driver, current, handoff_row, seconds=0.34)
    handoff_focus = _element_center(driver, By.XPATH, "//div[@class='row-label' and normalize-space()='Workflow Handoff']")
    _move_cursor_live(driver, current, handoff_focus, seconds=0.2)
    _hold_live(driver, current, 1.15)

    boundary_row = _row_container(driver, "What This Review Means")
    _smooth_scroll_to_live(driver, current, boundary_row, seconds=0.34)
    boundary_focus = _element_center(driver, By.XPATH, "//div[@class='row-label' and normalize-space()='What This Review Means']")
    _move_cursor_live(driver, current, boundary_focus, seconds=0.2)
    _hold_live(driver, current, 1.4)
    return current[0], current[1]


def record_live_walkthrough_video(output_path: Path) -> dict[str, float | int | str]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics: dict[str, int] | None = None

    with ensure_local_app_stack():
        driver = _build_driver(headless=False)
        try:
            driver.get(FRONTEND_URL)
            _wait_for(driver, By.ID, "guided-payer")
            driver.execute_script(CURSOR_INSTALL_SCRIPT)
            _set_capture_title(driver)
            time.sleep(0.8)
            _focus_capture_window()
            metrics = _window_capture_metrics(driver)
            recording = _start_window_recording(output_path, metrics)
            try:
                _focus_capture_window()
                final_cursor = _run_live_walkthrough_sequence(driver)
                _hold_live(driver, [final_cursor[0], final_cursor[1]], 0.4)
            finally:
                _stop_window_recording(recording)
        finally:
            driver.quit()

    if metrics is None:
        raise RuntimeError("Failed to compute recording metrics for live walkthrough video")

    return {
        "source": "screen_recording",
        "fps": TARGET_FPS,
        "width": metrics["width"],
        "height": metrics["height"],
    }


def _set_text_input(
    driver: webdriver.Chrome,
    frames: list[Image.Image],
    current: list[float],
    input_id: str,
    value: str,
    chunks: list[str],
    move_steps: int = 12,
) -> None:
    target = _element_center(driver, By.ID, input_id)
    _move_cursor(driver, frames, current, target, steps=move_steps)
    element = driver.find_element(By.ID, input_id)
    pre_click = _capture_frame(driver, (current[0], current[1]))
    _hold(frames, pre_click, _frames(0.16))
    element.click()
    _click_pulse(driver, frames, current)
    clicked = _capture_frame(driver, (current[0], current[1]))
    _hold(frames, clicked, _frames(0.14))
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.DELETE)
    for chunk in chunks:
        element.send_keys(chunk)
        frame = _capture_frame(driver, (current[0], current[1]))
        _hold(frames, frame, _frames(0.12))
    frame = _capture_frame(driver, (current[0], current[1]))
    _hold(frames, frame, _frames(0.28))


def _set_select_value(
    driver: webdriver.Chrome,
    frames: list[Image.Image],
    current: list[float],
    element_id: str,
    visible_text: str,
    move_steps: int = 10,
) -> None:
    target = _element_center(driver, By.ID, element_id)
    _move_cursor(driver, frames, current, target, steps=move_steps)
    element = driver.find_element(By.ID, element_id)
    pre_click = _capture_frame(driver, (current[0], current[1]))
    _hold(frames, pre_click, _frames(0.12))
    element.click()
    _click_pulse(driver, frames, current, strengths=(0.3, 0.82, 0.46))
    Select(element).select_by_visible_text(visible_text)
    frame = _capture_frame(driver, (current[0], current[1]))
    _hold(frames, frame, _frames(0.26))


def _smooth_scroll_to(
    driver: webdriver.Chrome,
    frames: list[Image.Image],
    current: list[float],
    element,
    steps: int = 12,
) -> None:
    target_y = driver.execute_script(
        """
        const rect = arguments[0].getBoundingClientRect();
        const target = window.scrollY + rect.top - 120;
        return Math.max(0, target);
        """,
        element,
    )
    start_y = driver.execute_script("return window.scrollY;")
    for index in range(steps):
        t = 0 if steps == 1 else index / (steps - 1)
        eased = _ease(t)
        next_y = start_y + ((target_y - start_y) * eased)
        driver.execute_script("window.scrollTo(0, arguments[0]);", float(next_y))
        frames.append(_capture_frame(driver, (current[0], current[1])))


def _row_container(driver: webdriver.Chrome, label: str):
    xpath = f"//div[@class='row-label' and normalize-space()='{label}']/.."
    return _wait_for(driver, By.XPATH, xpath)


def _row_label(driver: webdriver.Chrome, label: str):
    xpath = f"//div[@class='row-label' and normalize-space()='{label}']"
    return _wait_for(driver, By.XPATH, xpath)


def capture_live_walkthrough_frames() -> list[Image.Image]:
    frames: list[Image.Image] = []
    current = [220.0, 180.0]

    with ensure_local_app_stack():
        driver = _build_driver()
        try:
            driver.get(FRONTEND_URL)
            _wait_for(driver, By.ID, "guided-payer")
            driver.execute_script(CURSOR_INSTALL_SCRIPT)

            initial = _capture_frame(driver, (current[0], current[1]))
            _hold(frames, initial, _frames(0.9))

            _set_select_value(driver, frames, current, "guided-payer", "CN", move_steps=_frames(0.32))
            _set_select_value(driver, frames, current, "guided-payee", "NL", move_steps=_frames(0.3))
            _set_select_value(driver, frames, current, "guided-income-type", "dividends", move_steps=_frames(0.3))

            _set_text_input(
                driver,
                frames,
                current,
                "guided-fact-direct_holding_percentage",
                "30",
                chunks=["3", "0"],
                move_steps=_frames(0.42),
            )
            _set_text_input(
                driver,
                frames,
                current,
                "guided-fact-payment_date",
                "2026-03-01",
                chunks=["2026", "-03", "-01"],
                move_steps=_frames(0.36),
            )
            _set_text_input(
                driver,
                frames,
                current,
                "guided-fact-holding_period_months",
                "14",
                chunks=["1", "4"],
                move_steps=_frames(0.34),
            )
            _set_select_value(driver, frames, current, "guided-fact-beneficial_owner_confirmed", "yes", move_steps=_frames(0.28))
            _set_select_value(driver, frames, current, "guided-fact-pe_effectively_connected", "no", move_steps=_frames(0.28))
            _set_select_value(driver, frames, current, "guided-fact-holding_structure_is_direct", "yes", move_steps=_frames(0.28))

            run_button = _wait_for(driver, By.XPATH, "//button[normalize-space()='Run Guided Review']")
            run_target = _element_center(driver, By.XPATH, "//button[normalize-space()='Run Guided Review']")
            _move_cursor(driver, frames, current, run_target, steps=_frames(0.42))
            before_run = _capture_frame(driver, (current[0], current[1]))
            _hold(frames, before_run, _frames(0.18))
            run_button.click()
            _click_pulse(driver, frames, current, strengths=(0.32, 0.76, 1.0, 0.5))
            loading_frame = _capture_frame(driver, (current[0], current[1]))
            _hold(frames, loading_frame, _frames(0.82))

            treaty_row = _row_container(driver, "Treaty Provision")
            _smooth_scroll_to(driver, frames, current, treaty_row, steps=_frames(0.36))
            treaty_focus = _element_center(
                driver,
                By.XPATH,
                "//div[@class='row-label' and normalize-space()='Treaty Provision']",
            )
            _move_cursor(driver, frames, current, treaty_focus, steps=_frames(0.26))
            treaty_frame = _capture_frame(driver, (current[0], current[1]))
            _hold(frames, treaty_frame, _frames(1.08))

            source_row = _row_container(driver, "Source Chain")
            _smooth_scroll_to(driver, frames, current, source_row, steps=_frames(0.34))
            source_focus = _element_center(
                driver,
                By.XPATH,
                "//div[@class='row-label' and normalize-space()='Source Chain']",
            )
            _move_cursor(driver, frames, current, source_focus, steps=_frames(0.24))
            source_frame = _capture_frame(driver, (current[0], current[1]))
            _hold(frames, source_frame, _frames(1.28))

            handoff_row = _row_container(driver, "Workflow Handoff")
            _smooth_scroll_to(driver, frames, current, handoff_row, steps=_frames(0.34))
            handoff_focus = _element_center(
                driver,
                By.XPATH,
                "//div[@class='row-label' and normalize-space()='Workflow Handoff']",
            )
            _move_cursor(driver, frames, current, handoff_focus, steps=_frames(0.24))
            handoff_frame = _capture_frame(driver, (current[0], current[1]))
            _hold(frames, handoff_frame, _frames(1.2))

            boundary_row = _row_container(driver, "What This Review Means")
            _smooth_scroll_to(driver, frames, current, boundary_row, steps=_frames(0.34))
            boundary_focus = _element_center(
                driver,
                By.XPATH,
                "//div[@class='row-label' and normalize-space()='What This Review Means']",
            )
            _move_cursor(driver, frames, current, boundary_focus, steps=_frames(0.24))
            boundary_frame = _capture_frame(driver, (current[0], current[1]))
            _hold(frames, boundary_frame, _frames(1.68))
        finally:
            driver.quit()

    if not frames:
        raise RuntimeError("No live walkthrough frames were captured")

    return frames
