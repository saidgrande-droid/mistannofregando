#!/usr/bin/env python3
"""
Builds a zero-Node standalone browser bundle (`public/app-bundle.js` and `dist/`)
from the TypeScript/React source tree in `src/`.
"""
import json
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
DIST_DIR = os.path.join(BASE_DIR, "dist")

MODULES_TO_COLLECT = [
    "core/types.ts",
    "core/dataset.ts",
    "core/calculator.ts",
    "core/storage.ts",
    "core/crowdsource.ts",
    "core/affiliate.ts",
    "core/index.ts",
    "components/Tachometer.tsx",
    "components/ResultSummary.tsx",
    "components/ShareCard.tsx",
    "components/AdSlot.tsx",
    "components/AffiliateCard.tsx",
    "components/CalculatorForm.tsx",
    "components/CrowdsourceModal.tsx",
    "components/LegalModal.tsx",
    "components/CookieBanner.tsx",
    "components/index.ts",
    "App.tsx",
    "main.tsx",
]

def main():
    modules_map = {}
    for rel_path in MODULES_TO_COLLECT:
        full_path = os.path.join(SRC_DIR, rel_path)
        with open(full_path, "r", encoding="utf-8") as f:
            modules_map["src/" + rel_path] = f.read()

    dataset_path = os.path.join(SRC_DIR, "core", "dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset_json = json.load(f)

    bundle_js = f"""// Auto-generated standalone browser runtime bundle for "Mi Stanno Fregando?"
(function() {{
  const RAW_MODULES = {json.dumps(modules_map, ensure_ascii=False)};
  const DATASET_JSON = {json.dumps(dataset_json, ensure_ascii=False)};

  // Clean SVG Lucide React Icon Factory
  const React = window.React;
  function createIcon(paths, viewBox = "0 0 24 24") {{
    return function IconComponent(props) {{
      const {{ className = "w-5 h-5", size, strokeWidth = 2, ...rest }} = props || {{}};
      const style = size ? {{ width: size, height: size, ...(props && props.style) }} : (props && props.style);
      return React.createElement(
        "svg",
        {{
          xmlns: "http://www.w3.org/2000/svg",
          viewBox,
          fill: "none",
          stroke: "currentColor",
          strokeWidth,
          strokeLinecap: "round",
          strokeLinejoin: "round",
          className,
          style,
          "aria-hidden": "true",
          ...rest
        }},
        ...paths.map((el, idx) => React.createElement(el[0], {{ key: idx, ...el[1] }}))
      );
    }};
  }}

  const LUCIDE_ICONS = {{
    CheckCircle2: createIcon([["circle", {{ cx: 12, cy: 12, r: 10 }}], ["path", {{ d: "m9 12 2 2 4-4" }}]]),
    Users: createIcon([["path", {{ d: "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" }}], ["circle", {{ cx: 9, cy: 7, r: 4 }}], ["path", {{ d: "M22 21v-2a4 4 0 0 0-3-3.87" }}], ["path", {{ d: "M16 3.13a4 4 0 0 1 0 7.75" }}]]),
    Share2: createIcon([["circle", {{ cx: 18, cy: 5, r: 3 }}], ["circle", {{ cx: 6, cy: 12, r: 3 }}], ["circle", {{ cx: 18, cy: 19, r: 3 }}], ["line", {{ x1: 8.59, y1: 13.51, x2: 15.42, y2: 17.49 }}], ["line", {{ x1: 15.41, y1: 6.51, x2: 8.59, y2: 10.49 }}]]),
    Download: createIcon([["path", {{ d: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" }}], ["polyline", {{ points: "7 10 12 15 17 10" }}], ["line", {{ x1: 12, y1: 15, x2: 12, y2: 3 }}]]),
    Copy: createIcon([["rect", {{ width: 14, height: 14, x: 8, y: 8, rx: 2, ry: 2 }}], ["path", {{ d: "M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" }}]]),
    Check: createIcon([["path", {{ d: "M20 6 9 17l-5-5" }}]]),
    AlertTriangle: createIcon([["path", {{ d: "m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" }}], ["path", {{ d: "M12 9v4" }}], ["path", {{ d: "M12 17h.01" }}]]),
    MinusCircle: createIcon([["circle", {{ cx: 12, cy: 12, r: 10 }}], ["path", {{ d: "M8 12h8" }}]]),
    TrendingUp: createIcon([["polyline", {{ points: "22 7 13.5 15.5 8.5 10.5 2 17" }}], ["polyline", {{ points: "16 7 22 7 22 13" }}]]),
    TrendingDown: createIcon([["polyline", {{ points: "22 17 13.5 8.5 8.5 13.5 2 7" }}], ["polyline", {{ points: "16 17 22 17 22 11" }}]]),
    Info: createIcon([["circle", {{ cx: 12, cy: 12, r: 10 }}], ["path", {{ d: "M12 16v-4" }}], ["path", {{ d: "M12 8h.01" }}]]),
    MapPin: createIcon([["path", {{ d: "M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" }}], ["circle", {{ cx: 12, cy: 10, r: 3 }}]]),
    Sparkles: createIcon([["path", {{ d: "m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" }}]]),
    ArrowRight: createIcon([["path", {{ d: "M5 12h14" }}], ["path", {{ d: "m12 5 7 7-7 7" }}]]),
    ExternalLink: createIcon([["path", {{ d: "M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" }}], ["polyline", {{ points: "15 3 21 3 21 9" }}], ["line", {{ x1: 10, y1: 14, x2: 21, y2: 3 }}]]),
    ShieldAlert: createIcon([["path", {{ d: "M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" }}], ["path", {{ d: "M12 8v4" }}], ["path", {{ d: "M12 16h.01" }}]]),
    Tag: createIcon([["path", {{ d: "M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z" }}], ["circle", {{ cx: 7.5, cy: 7.5, r: 0.5, fill: "currentColor" }}]]),
    Car: createIcon([["path", {{ d: "M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" }}], ["circle", {{ cx: 7, cy: 17, r: 2 }}], ["path", {{ d: "M9 17h6" }}], ["circle", {{ cx: 17, cy: 17, r: 2 }}]]),
    Home: createIcon([["path", {{ d: "m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" }}], ["polyline", {{ points: "9 22 9 12 15 12 15 22" }}]]),
    Smile: createIcon([["circle", {{ cx: 12, cy: 12, r: 10 }}], ["path", {{ d: "M8 14s1.5 2 4 2 4-2 4-2" }}], ["line", {{ x1: 9, y1: 9, x2: 9.01, y2: 9 }}], ["line", {{ x1: 15, y1: 9, x2: 15.01, y2: 9 }}]]),
    HeartPulse: createIcon([["path", {{ d: "M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" }}], ["path", {{ d: "M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27" }}]]),
    Key: createIcon([["circle", {{ cx: 7.5, cy: 15.5, r: 5.5 }}], ["path", {{ d: "m21 2-9.6 9.6" }}], ["path", {{ d: "m15.5 7.5 3 3L22 7l-3-3" }}]]),
    Search: createIcon([["circle", {{ cx: 11, cy: 11, r: 8 }}], ["path", {{ d: "m21 21-4.3-4.3" }}]]),
    ChevronDown: createIcon([["path", {{ d: "m6 9 6 6 6-6" }}]]),
    AlertCircle: createIcon([["circle", {{ cx: 12, cy: 12, r: 10 }}], ["line", {{ x1: 12, y1: 8, x2: 12, y2: 12 }}], ["line", {{ x1: 12, y1: 16, x2: 12.01, y2: 16 }}]]),
    Calculator: createIcon([["rect", {{ width: 16, height: 20, x: 4, y: 2, rx: 2 }}], ["line", {{ x1: 8, x2: 16, y1: 6, y2: 6 }}], ["line", {{ x1: 16, x2: 16, y1: 14, y2: 18 }}], ["path", {{ d: "M16 10h.01" }}], ["path", {{ d: "M12 10h.01" }}], ["path", {{ d: "M8 10h.01" }}], ["path", {{ d: "M12 14h.01" }}], ["path", {{ d: "M8 14h.01" }}], ["path", {{ d: "M12 18h.01" }}], ["path", {{ d: "M8 18h.01" }}]]),
    X: createIcon([["path", {{ d: "M18 6 6 18" }}], ["path", {{ d: "m6 6 12 12" }}]]),
    Layers: createIcon([["polygon", {{ points: "12 2 2 7 12 12 22 7 12 2" }}], ["polyline", {{ points: "2 17 12 22 22 17" }}], ["polyline", {{ points: "2 12 12 17 22 12" }}]]),
    ListFilter: createIcon([["path", {{ d: "M3 6h18" }}], ["path", {{ d: "M7 12h10" }}], ["path", {{ d: "M10 18h4" }}]]),
    Megaphone: createIcon([["path", {{ d: "m3 11 18-5v12L3 14v-3z" }}], ["path", {{ d: "M11.6 16.8a3 3 0 1 1-5.8-1.6" }}]]),
    Send: createIcon([["path", {{ d: "m22 2-7 20-4-9-9-4Z" }}], ["path", {{ d: "M22 2 11 13" }}]]),
    Coins: createIcon([["circle", {{ cx: 8, cy: 8, r: 6 }}], ["path", {{ d: "M18.09 10.37A6 6 0 1 1 10.34 18" }}], ["path", {{ d: "M7 6h1v4" }}], ["path", {{ d: "m16.71 13.88.7.71-2.82 2.82" }}]]),
    ShieldCheck: createIcon([["path", {{ d: "M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" }}], ["path", {{ d: "m9 12 2 2 4-4" }}]]),
  }};

  const MODULE_CACHE = {{}};

  function normalizePath(baseDir, relPath) {{
    if (!relPath.startsWith(".")) return relPath;
    const parts = baseDir.split("/").filter(Boolean);
    for (const seg of relPath.split("/")) {{
      if (seg === "." || seg === "") continue;
      if (seg === "..") parts.pop();
      else parts.push(seg);
    }}
    const candidate = parts.join("/");
    if (RAW_MODULES[candidate]) return candidate;
    if (RAW_MODULES[candidate + ".ts"]) return candidate + ".ts";
    if (RAW_MODULES[candidate + ".tsx"]) return candidate + ".tsx";
    if (RAW_MODULES[candidate + "/index.ts"]) return candidate + "/index.ts";
    if (candidate.endsWith("dataset.json")) return "src/core/dataset.json";
    return candidate;
  }}

  function requireModule(fromDir, spec) {{
    if (spec === "react") return window.React;
    if (spec === "react-dom/client" || spec === "react-dom") return window.ReactDOM;
    if (spec === "lucide-react") return LUCIDE_ICONS;
    if (spec.endsWith(".css")) return {{}};

    const resolved = normalizePath(fromDir, spec);
    if (resolved === "src/core/dataset.json") return DATASET_JSON;
    if (MODULE_CACHE[resolved]) return MODULE_CACHE[resolved].exports;

    const source = RAW_MODULES[resolved];
    if (source === undefined) {{
      throw new Error("Module not found: " + spec + " (resolved: " + resolved + ")");
    }}

    const mod = {{ exports: {{}} }};
    MODULE_CACHE[resolved] = mod;
    const dir = resolved.substring(0, resolved.lastIndexOf("/"));

    const compiled = window.Babel.transform(source, {{
      filename: resolved,
      presets: [
        ["env", {{ modules: "commonjs" }}],
        ["react", {{ runtime: "classic" }}],
        "typescript"
      ]
    }}).code;

    const fn = new Function("module", "exports", "require", compiled);
    fn(mod, mod.exports, function(childSpec) {{
      return requireModule(dir, childSpec);
    }});

    return mod.exports;
  }}

  window.addEventListener("DOMContentLoaded", function() {{
    try {{
      requireModule("src", "./main.tsx");
    }} catch (err) {{
      console.error("Failed to boot Mi Stanno Fregando?:", err);
      const root = document.getElementById("root");
      if (root) {{
        root.innerHTML = '<div style="padding:24px;color:#fda4af;font-family:sans-serif">Errore di avvio: ' + String(err.message || err) + '</div>';
      }}
    }}
  }});
}})();
"""

    os.makedirs(PUBLIC_DIR, exist_ok=True)
    bundle_path = os.path.join(PUBLIC_DIR, "app-bundle.js")
    with open(bundle_path, "w", encoding="utf-8") as f:
        f.write(bundle_js)

    print(f"Wrote {bundle_path} ({len(bundle_js)} bytes)")

if __name__ == "__main__":
    main()
