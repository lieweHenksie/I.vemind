#!/usr/bin/env python3
"""THE BENCH EAR — prove a song's instruments before you trust them.

    python3 tools/song/check.py id/nice_ron           # one song
    python3 tools/song/check.py --all                 # every song with a song.json
    python3 tools/song/check.py id/nice_ron --static  # no browser: static + drift only

Why this exists. A palette entry is RAW STRUDEL — that is the whole point, it is how a song
gets its own sound — but raw Strudel has three failure modes that the build cannot see, and
two of them are silent:

  1. ONE BAD INSTRUMENT KILLS THE WHOLE SCORE. Every instrument is emitted into one evaluated
     block, so a syntax error in any single `let` makes evaluate() throw and the song plays
     NOTHING. The page shows no error worth reading. You get silence and no idea which of the
     thirty-five entries did it. This bisects that for you.

  2. AN INSTRUMENT CAN RENDER SILENT WITH NO ERROR AT ALL. The known one:
     `s("x").freq(…).decay(…).sustain(0)` with no explicit attack/release is silent in 1.0.3,
     while `note(…).s("x")` with the same envelope is fine. Nothing throws. The layer is simply
     not there, and you only find out by listening hard to a mix that already has ten things in
     it. So we LISTEN to each instrument alone, through the same analyser the stage uses.

  3. ENRICHING AN INSTRUMENT CAN MOVE THE FILM. gen_cues() reads instrument code with a regex —
     the FIRST `s("…")`, plus `.slow(n)` and `.slice(`. Wrap an instrument in a stack() with a
     second sample, or add a .slow(), and the video cues silently change. We recompute every
     generated region and show you the blast radius BEFORE you build.

The rule this serves is the project's iron rule — fix where broken, leave what works. You
cannot honour that if a change breaks something you can't hear yet.

NB: the browser pass always runs with --mute-audio. A checker that plays thirty-five
instruments at you through the speakers is not a checker, it is an ambush.
"""
import argparse, http.server, json, pathlib, re, socketserver, subprocess, sys, threading, time, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build  # the compiler itself — never duplicate its logic, import it

STRUDEL = "https://unpkg.com/@strudel/web@1.0.3"

# The silent-envelope shape from the cookbook's hard-won note. Matches `s("…")` carrying a
# freq()+sustain(0) envelope with no explicit attack/release — the form that renders silent.
SILENT_SHAPE = re.compile(r's\("[^"]+"\)(?![^;]*\.note\()(?=[^;]*\.freq\()(?=[^;]*\.sustain\(0\))'
                          r'(?![^;]*\.attack\()(?![^;]*\.release\()')


# ── findings ────────────────────────────────────────────────────────────────────────────────
ERR, WARN, INFO = "ERROR", "WARN", "INFO"


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, what, detail=""):
        self.items.append((level, what, detail))

    def has_errors(self):
        return any(l == ERR for l, *_ in self.items)

    def show(self, title):
        mark = {ERR: "✗", WARN: "!", INFO: "·"}
        print(f"\n── {title} " + "─" * max(0, 76 - len(title)))
        if not self.items:
            print("  clean.")
            return
        for level, what, detail in self.items:
            print(f"  {mark[level]} {what}")
            for line in str(detail).splitlines():
                if line.strip():
                    print(f"      {line}")


# ── loading ─────────────────────────────────────────────────────────────────────────────────
def load(song_dir):
    """The exact merge build.py does: cookbook default, then the song's own palette over it.

    We also keep the song's OWN key set. An unused cookbook default is just an inherited recipe
    the song never reached for — every song has ten of those and saying so is noise. An unused
    entry the song AUTHORED is worth a line: either it is staged on purpose, or it is a layer
    you meant to wire into a section and didn't."""
    spec = json.loads((song_dir / "song.json").read_text())
    palette = json.loads(build.PALETTE.read_text())
    own_keys = set()
    own = song_dir / "palette.json"
    if own.exists():
        own_palette = json.loads(own.read_text())
        own_keys = {k for k in own_palette if not k.startswith("_")}
        palette = {**palette, **own_palette}
    return spec, palette, own_keys


def used_names(spec):
    """Every instrument the shape actually reaches for — layers, split layers and fills."""
    used = set()
    for s in spec["sections"]:
        used.update(build._lname(e) for e in s.get("layers", []))
        for part in s.get("split", []):
            used.update(build._lname(e) for e in part[1])
        if s.get("fill"):
            used.add(s["fill"])
    return used


def instruments(palette):
    return [(n, v) for n, v in palette.items() if not n.startswith("_") and isinstance(v, str)]


# ── static pass ─────────────────────────────────────────────────────────────────────────────
def static_checks(song_dir, spec, palette, own_keys, rep):
    used = used_names(spec)
    names = {n for n, _ in instruments(palette)}

    unknown = sorted(used - names)
    if unknown:
        rep.add(ERR, f"{len(unknown)} layer(s) named in song.json have no palette entry",
                "\n".join(unknown) + "\n(build.py will refuse this)")

    # Unused entries are FREE — gen_instruments only emits what's used. That is the safe way to
    # stage a new sound: add it, build, nothing moves. Only mention the song's OWN unused entries;
    # unused cookbook defaults are just inherited recipes and every song has a pile of them.
    staged = sorted((names - used) & own_keys)
    if staged:
        rep.add(INFO, f"{len(staged)} of this song's own entr(ies) are unused — they emit nothing",
                ", ".join(staged) + "\n(staged for later, or a layer you forgot to wire in?)")

    for name, code in instruments(palette):
        if SILENT_SHAPE.search(code):
            rep.add(WARN, f"'{name}' matches the silent-envelope shape",
                    "s(\"…\").freq(…).sustain(0) with no attack/release renders SILENT in 1.0.3.\n"
                    "Use note(…).s(\"…\") with the same envelope instead.")

    # Deliberately NO static check for "plays a sample the crate doesn't stock". We would have to
    # vendor Strudel's entire built-in bank list to tell a missing cut from a builtin, and that
    # list would rot against the pinned runtime. The browser pass answers it authoritatively
    # instead: Strudel prints "sound X not found" and we attribute it to the instrument playing.
    return used


def region_drift(song_dir, spec, palette, rep):
    """What WOULD change in index.html if you ran build.py right now — the blast radius."""
    index = song_dir / "index.html"
    if not index.exists():
        rep.add(WARN, "no index.html — nothing to compare against (run compose first)")
        return
    txt = index.read_text()
    bpm = spec.get("bpm", 120)
    used = used_names(spec)

    want = {
        "INSTRUMENTS": build.gen_instruments(used, palette),
        "ARRANGE": build.gen_arrange(spec["sections"], bpm),
        "TIMELINE": build.gen_timeline(spec["sections"], bpm),
        "VIDEO-CUES": build.gen_cues(spec["sections"], palette, bpm),
    }
    for region, generated in want.items():
        start, end = f"// {region}-START", f"// {region}-END"
        if start not in txt:
            continue
        cur = txt.split(start, 1)[1].split(end, 1)[0]
        norm = lambda s: [l.strip() for l in s.strip().splitlines() if l.strip()]
        a, b = norm(cur), norm(generated)
        if a == b:
            continue
        added = [l for l in b if l not in a]
        gone = [l for l in a if l not in b]
        detail = "\n".join([f"+ {l[:150]}" for l in added[:6]] + [f"- {l[:150]}" for l in gone[:6]])
        more = (len(added) + len(gone)) - min(6, len(added)) - min(6, len(gone))
        if more > 0:
            detail += f"\n… and {more} more line(s)"
        level = WARN if region == "VIDEO-CUES" else INFO
        rep.add(level, f"{region} region would change on the next build "
                       f"({len(added)} new, {len(gone)} gone)", detail)


# ── the browser pass ────────────────────────────────────────────────────────────────────────
PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="%(strudel)s"></script></head><body><div id="s">checking…</div><script>
const INSTR = %(instr)s, SAMPLES = %(samples)s, WINDOW = %(window)d, THRESH = %(thresh)f;
const send = (o) => new Promise(r => { const i = new Image();
  i.onload = i.onerror = r; i.src = '/__check__?j=' + encodeURIComponent(JSON.stringify(o)) + '&_=' + Math.random(); });

// THE EAR — mirror every connection to the destination into one analyser, never in the signal
// path, kept alive by a silent gain. Identical to the stage, so "silent here" means "silent there".
let ear = null, wave = null;
(function openEar() {
  const connect = AudioNode.prototype.connect;
  AudioNode.prototype.connect = function (to, ...rest) {
    const out = connect.apply(this, [to, ...rest]);
    try {
      if (to instanceof AudioDestinationNode && this !== ear) {
        const ac = to.context;
        if (!ear) {
          ear = ac.createAnalyser(); ear.fftSize = 2048; wave = new Uint8Array(ear.fftSize);
          const mute = ac.createGain(); mute.gain.value = 0;
          connect.call(ear, mute); connect.call(mute, to);
        }
        if (ear.context === ac) connect.call(this, ear);
      }
    } catch (e) {}
    return out;
  };
})();
const rms = () => { if (!ear) return 0; ear.getByteTimeDomainData(wave);
  let q = 0; for (let i = 0; i < wave.length; i++) { const v = (wave[i] - 128) / 128; q += v * v; }
  return Math.sqrt(q / wave.length); };

// Strudel says "sound X not found" on the console and keeps going — capture it per instrument.
let log = [];
for (const k of ['warn', 'error']) { const o = console[k].bind(console);
  console[k] = (...a) => { log.push(a.map(x => (x && x.message) || String(x)).join(' ')); o(...a); }; }

const reg = async () => { if (typeof samples !== 'function') return;
  const folder = new URL('./', location.href).href;
  for (const [n, f] of Object.entries(SAMPLES)) { try { await samples({ [n]: f }, folder); } catch (e) {} } };

const ALL = INSTR.map(([n, e]) => 'let ' + n + ' = ' + e).join('\\n');
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function listen(base) {  // early-exit the moment it clears the bar; only silence costs the window
  const bar = Math.max(THRESH, base * 2);
  const began = performance.now(); let peak = 0;
  while (performance.now() - began < WINDOW) {
    await sleep(25); peak = Math.max(peak, rms());
    if (peak > bar) break;
  }
  return peak;
}
const measure = async (ms) => { const t = performance.now(); let m = 0;
  while (performance.now() - t < ms) { await sleep(25); m = Math.max(m, rms()); } return m; };

// WAIT FOR THE ROOM TO GO QUIET before measuring the next instrument. hush() stops the
// scheduler, it does not silence what is already ringing — half this cookbook runs room(0.9),
// and impact decays for 1.6s. Without this the previous instrument's tail is still in the air
// when the next one is measured, every instrument reads as "sounded", and early-exit makes it
// self-perpetuating: the tail trips the threshold instantly, we exit, and it rings on into the
// one after. A palette of pure `silence` scored 18/18 sounding before this existed.
async function settle(maxMs) {
  const began = performance.now(); let quiet = 0;
  while (performance.now() - began < maxMs) {
    await sleep(30);
    if (rms() <= THRESH * 0.4) { if (++quiet >= 3) return true; } else quiet = 0;
  }
  return false;   // still ringing — the measurement that follows is suspect, so we say so
}

(async () => {
  try { initStrudel({ prebake: reg }); }
  catch (e) { await send({ fatal: 'strudel failed to boot: ' + e.message }); return; }
  await sleep(600);

  // PASS 1 — the real-world condition: every instrument in one block, exactly as the song ships.
  let whole = null;
  try { await evaluate(ALL + '\\nsilence'); }
  catch (e) { whole = e.message; }
  try { hush(); } catch (e) {}
  await send({ whole: whole });

  // PASS 2 — THE BISECT, and only when it is needed. If the whole block compiled then every
  // instrument in it compiled, so we can listen against the full block and keep the common case
  // fast. If it did NOT compile we must find the culprit, and we cannot do that by evaluating
  // each instrument against a block that is already poisoned — every single one would report the
  // same parse error and name nothing. So each is compiled ALONE (against `silence`, so nothing
  // sounds), and the survivors become the prefix the listening pass runs against.
  let GOOD = ALL;
  const compileErr = {};
  let playable = INSTR;
  if (whole) {
    const good = [];
    for (const [name, expr] of INSTR) {
      try { await evaluate('let ' + name + ' = ' + expr + '\\nsilence'); good.push([name, expr]); }
      catch (e) { compileErr[name] = e.message; }
      try { hush(); } catch (e) {}
    }
    playable = good;
    GOOD = good.map(([n, e]) => 'let ' + n + ' = ' + e).join('\\n');
    for (const [name, msg] of Object.entries(compileErr))
      await send({ name: name, err: msg, peak: 0, log: [] });
  }

  // PASS 3 — each instrument that compiles, alone but defined against its peers so a
  // cross-reference still resolves. Does it actually reach the speakers?
  for (const [name, expr] of playable) {
    try { hush(); } catch (e) {}
    const clean = await settle(2500);
    log = [];
    let err = null, peak = 0;
    try { await evaluate(GOOD + '\\n' + name); }
    catch (e) { err = e.message; }
    if (!err) peak = await listen();
    try { hush(); } catch (e) {}
    await send({ name: name, err: err, peak: Math.round(peak * 1e4) / 1e4, dirty: !clean,
                 log: log.filter(l => /not found|error|fail/i.test(l)).slice(0, 3) });
  }
  await send({ done: true });
  document.getElementById('s').textContent = 'done';
})();
</script></body></html>"""


def find_chrome():
    import os, shutil
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for c in ("google-chrome", "chromium", "chromium-browser", "google-chrome-stable"):
        p = shutil.which(c)
        if p:
            return p
    for p in ("/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
              "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
              "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe"):
        if pathlib.Path(p).exists():
            return p
    return None


def audio_checks(song_dir, palette, rep, window_ms, thresh, quiet):
    chrome = find_chrome()
    if not chrome:
        rep.add(WARN, "no Chrome/Chromium found — skipped the listening pass",
                "set CHROME=/path/to/chrome, or pass --static to silence this")
        return

    instr = instruments(palette)
    if not instr:
        return
    crate = {n: (m["file"] if isinstance(m, dict) else m)
             for n, m in palette.get("_samples", {}).items()}

    page = song_dir / "_check.html"
    page.write_text(PAGE % dict(strudel=STRUDEL, instr=json.dumps(instr),
                                samples=json.dumps(crate), window=window_ms, thresh=thresh))

    results, done = [], threading.Event()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(ROOT), **kw)

        def do_GET(self):
            if self.path.startswith("/__check__"):
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                try:
                    o = json.loads(q.get("j", ["{}"])[0])
                except Exception:
                    o = {}
                if o.get("done") or o.get("fatal"):
                    if o.get("fatal"):
                        results.append(o)
                    done.set()
                else:
                    results.append(o)
                    if not quiet and o.get("name"):
                        print(f"    … {o['name']}", end="\r", flush=True)
                self.send_response(204); self.end_headers(); return
            super().do_GET()

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, *a):
            pass

    class Server(socketserver.ThreadingTCPServer):
        daemon_threads = True
        allow_reuse_address = True

    httpd = Server(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    url = f"http://127.0.0.1:{port}/{page.relative_to(ROOT).as_posix()}"
    # +0.6/instrument covers the bisect pass, which only runs when the block is broken.
    # per instrument: up to 2.5s settling for reverb tails, the listen window, and the bisect.
    budget = 30 + len(instr) * (window_ms / 1000 + 2.6)
    proc = subprocess.Popen(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--mute-audio",                          # never, ever play this at the human
         "--autoplay-policy=no-user-gesture-required",
         f"--user-data-dir=/tmp/cyb-check-{port}", url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        done.wait(timeout=budget)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        httpd.shutdown()
        page.unlink(missing_ok=True)
        if not quiet:
            print(" " * 40, end="\r")

    fatal = [r for r in results if r.get("fatal")]
    if fatal:
        rep.add(ERR, fatal[0]["fatal"])
        return

    whole = [r for r in results if "whole" in r]
    per = [r for r in results if r.get("name")]

    if whole and whole[0]["whole"]:
        rep.add(ERR, "THE WHOLE SCORE FAILS TO EVALUATE — this song plays nothing",
                whole[0]["whole"])
    if not per:
        rep.add(WARN, "the listening pass produced no results (browser died or timed out?)")
        return

    broken = [r for r in per if r.get("err")]
    for r in broken:
        rep.add(ERR, f"'{r['name']}' does not evaluate", r["err"])

    bar = lambda r: max(thresh, r.get("base", 0) * 2)
    silent = [r for r in per if not r.get("err") and r.get("peak", 0) <= bar(r)]
    for r in silent:
        hint = ""
        code = dict(instr).get(r["name"], "")
        if SILENT_SHAPE.search(code):
            hint = "\nmatches the silent-envelope shape — use note(…).s(\"…\")"
        rep.add(WARN, f"'{r['name']}' made NO SOUND (peak {r['peak']}"
                      + (f", room still at {r['base']}" if r.get("base", 0) > thresh else "") + ")",
                (("console: " + " | ".join(r["log"])) if r.get("log") else
                 "no error — it evaluates, it just never reaches the speakers") + hint)

    noisy_logs = [r for r in per if r.get("log") and not r.get("err") and r.get("peak", 0) > thresh]
    for r in noisy_logs:
        rep.add(WARN, f"'{r['name']}' plays, but complained", " | ".join(r["log"]))

    # A "sounded" verdict measured while the previous instrument was still ringing is not a
    # verdict at all — say so rather than quietly passing it.
    dirty = [r for r in per if not r.get("err") and r.get("base", 0) > thresh
             and thresh < r.get("peak", 0) <= r.get("base", 0) * 3]
    if dirty:
        rep.add(WARN, f"{len(dirty)} instrument(s) only just cleared a still-ringing room "
                      f"— treat 'sounded' as unproven",
                ", ".join(f"{r['name']} (peak {r['peak']} vs tail {r['base']})" for r in dirty[:10]))

    heard = len(per) - len(broken) - len(silent)
    rep.add(INFO, f"listened to {len(per)} instrument(s): {heard} sounded, "
                  f"{len(silent)} silent, {len(broken)} broken")


# ── main ────────────────────────────────────────────────────────────────────────────────────
def check_song(song_dir, args):
    rep = Report()
    try:
        spec, palette, own_keys = load(song_dir)
    except FileNotFoundError as e:
        print(f"  skip {song_dir.name}: {e}")
        return False
    static_checks(song_dir, spec, palette, own_keys, rep)
    region_drift(song_dir, spec, palette, rep)
    if not args.static:
        audio_checks(song_dir, palette, rep, args.window, args.threshold, args.quiet)
    rep.show(song_dir.name)
    return rep.has_errors()


def main():
    ap = argparse.ArgumentParser(description="check a song's Strudel instruments")
    ap.add_argument("song", nargs="?", help="id/<name>")
    ap.add_argument("--all", action="store_true", help="every song with a song.json")
    ap.add_argument("--static", action="store_true", help="skip the browser pass")
    ap.add_argument("--window", type=int, default=2600,
                    help="ms to listen before calling an instrument silent (default 2600)")
    ap.add_argument("--threshold", type=float, default=0.004, help="RMS floor for 'made a sound'")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if a.all:
        dirs = sorted(p.parent for p in (ROOT / "id").glob("*/song.json"))
    elif a.song:
        dirs = [pathlib.Path(a.song).resolve()]
    else:
        ap.error("give a song dir, or --all")

    bad = False
    for d in dirs:
        bad |= check_song(d, a)
    print()
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
