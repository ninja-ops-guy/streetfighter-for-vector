# Street Fighter for Vector (Fightcade + wire-pod, Windows)

Launch Fightcade (FBNeo) and stream the game window to Anki Vector's screen via wire-pod. Includes helper scripts to start/stop and an optional REST trigger flow.

### What it does
- Starts Fightcade's FBNeo emulator with your Street Fighter III ROM
- Detects the emulator window and captures frames from it
- Scales/crops frames to Vector's screen (184x96), converts to RGB565
- Sends frames to wire-pod's `vector/display_image` endpoint for display on Vector
- Can be triggered by a wire-pod Custom Intent (Exec) or run manually

> Note: wire-pod custom intent Lua is only used for speaking behaviors; HTTP requests should be executed via Exec program/script, not Lua. See docs below.

---

## Folder contents

- `beam_video.py`: Main script. Launches emulator (via `launch_emulator.bat`), finds the window, captures and streams frames to Vector. Contains configurable constants at top.
- `launch_emulator.bat`: Starts FBNeo with the desired ROM.
- `start_fightcade.ps1`: Convenience PowerShell launcher for `beam_video.py`.
- `kill_listener.py` / `kill_listener.bat`: Utility to kill Python processes (e.g., a stuck listener/capture). Optional.
- `intent settings.png`: Example wire-pod Custom Intent configuration screenshot.

---

## Prerequisites

- Windows 10/11
- Python 3.10+ (tested with 3.13)
- Fightcade installed with FBNeo emulator
  - Update `EMULATOR_PATH` in `beam_video.py` to your FBNeo executable
  - Ensure the ROM you want (default: `sfiii3nr1`) exists in your emulator
- wire-pod installed and running on your network
  - Note your wire-pod IP and REST port (default UI often at `http://<ip>:8080`)
- Vector SDK credentials configured on this machine (Vector must be on same network)

### Python packages
Install with pip:

```bash
pip install mss opencv-python numpy requests pywin32 pillow anki_vector flask
```

---

## Configuration
Open `beam_video.py` and adjust the constants near the top:

```python
# wire-pod REST endpoint (adjust for your network)
WIREPOD_IP = "x.x.x.x"
WIREPOD_PORT = 8080

# The emulator window title keyword used to find/capture the window
WINDOW_TITLE_KEYWORD = "Fightcade FBNeo"

# FBNeo executable path and ROM to launch
EMULATOR_PATH = r"C:\Users\<you>\Documents\Fightcade\emulator\fbneo\fcadefbneo.exe"
ROM_NAME = "sfiii3nr1"
```

If your window title differs, change `WINDOW_TITLE_KEYWORD`. If your ROM or emulator path are different, update accordingly.

---

## Run options

### Option A: Manual (PowerShell)
Use the included PowerShell script to start everything:

```powershell
# From this folder
powershell -ExecutionPolicy Bypass -File .\start_fightcade.ps1
```

This launches `beam_video.py`, which:
- runs `launch_emulator.bat` to open FBNeo with the ROM
- finds the emulator window
- captures and streams frames to Vector via wire-pod

### Option B: Run the Python script directly

```bash
python beam_video.py
```

> The script includes a small Flask app with `/start_game` (POST) that triggers the batch file, but because the capture loop runs continuously, the REST handler is not used in the typical wire-pod Exec flow. Prefer Option A or the Custom Intent Exec below.

### Option C: Trigger from wire-pod Custom Intent (recommended)

In wire-pod's Configuration page, add a Custom Intent with your utterances (e.g., "let's play street fighter") and set Exec to run the PowerShell launcher.

- Exec (program):
  ```
  powershell
  ```
- Exec Args (comma-separated):
  ```
  -ExecutionPolicy,Bypass,-File,C:\Users\<you>\path\to\streetfighter_for_vector_github\start_fightcade.ps1
  ```

Optional: add Lua to make Vector speak when the intent fires:

```lua
assumeBehaviorControl(20)
sayText("yea but only if you play Elena. lets play street fighter!")
releaseBehaviorControl()
```

For more about Custom Intents, see the wire-pod wiki: [Custom Intents](https://github.com/kercre123/wire-pod/wiki/Custom-Intents).

---

## Troubleshooting

- Vector doesn’t speak / Lua error `attempt to call a non-function object`:
  - Ensure your Lua box contains only the three lines above; no `require` calls.
- Lua error `module socket.http not found`:
  - wire-pod’s Lua does not include HTTP libraries. Use Exec to run PowerShell/Python for HTTP or process launching.
- `python.exe: can't open file '...\beam_video.py'`:
  - The path in your script/Exec is wrong. Use the full absolute path shown above.
- `FileNotFoundError` when launching batch or emulator:
  - Update `EMULATOR_PATH` in `beam_video.py` and ensure `launch_emulator.bat` exists alongside `beam_video.py`.
- Window not found / size warning:
  - Ensure Fightcade’s FBNeo window is open and contains `Fightcade FBNeo` in the title. Warnings about size are informational.
- `anki_vector.exceptions.VectorControlTimeoutException`:
  - Ensure Vector is powered, on Wi‑Fi, on a flat surface, and fully charged. Confirm SDK pairing is valid on this PC.
- "Unable to initialize device PRN" in Exec Output:
  - Benign PowerShell message unrelated to this flow; safe to ignore.

---

## Notes
- The capture loop is continuous and will keep streaming to Vector at 5 (by default) frames per second. Use `Ctrl+C` in the terminal to stop.
- `kill_listener.py` is a blunt tool that terminates Python processes on Windows; use with caution.
- Tested with FBNeo via Fightcade; other emulators may work with adjustments to window title detection and launch command.

---

## License
Provide a license of your choice for public release (MIT recommended). Add a `LICENSE` file before publishing.

---

## Acknowledgments
- wire-pod: Custom Intents reference: [wire-pod Wiki – Custom Intents](https://github.com/kercre123/wire-pod/wiki/Custom-Intents)
- Anki Vector SDK
- Fightcade + FBNeo

