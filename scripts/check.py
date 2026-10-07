"""Repo self-check: python scripts/check.py"""
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BACKEND = REPO / "plugins" / "agency-agents-router"
PLUGIN_JS = (REPO / "desktop-plugins" / "agency-agents" / "plugin.js").read_text(encoding="utf-8")

agents = json.loads((BACKEND / "data" / "agents.json").read_text(encoding="utf-8"))
teams = json.loads((BACKEND / "data" / "teams.json").read_text(encoding="utf-8"))
slugs = {a["slug"] for a in agents}
assert len(agents) == len(slugs) == 321, len(agents)
assert all(m in slugs for t in teams for m in t["members"]), "team member missing"

for slug in slugs:
    svg = (REPO / "avatars" / f"{slug}.svg").read_text(encoding="utf-8")
    assert svg.lstrip().startswith("<svg"), slug
    assert f'"{slug}":"<svg' in PLUGIN_JS, f"avatar not bundled: {slug}"

spec = importlib.util.spec_from_file_location("agency_router", BACKEND / "__init__.py", submodule_search_locations=[str(BACKEND)])
module = importlib.util.module_from_spec(spec)
sys.modules["agency_router"] = module
spec.loader.exec_module(module)
tools = {}
module.register(type("Ctx", (), {"register_tool": lambda self, name=None, **kw: tools.setdefault(name or kw.get("name"), kw)})())
assert set(tools) >= {"agency_agents_search", "agency_agents_inspect", "agency_agents_load", "agency_agents_delegate"}, tools.keys()
print(f"check ok: {len(agents)} experts, {len(teams)} teams, {len(slugs)} bundled avatars, {len(tools)} tools")
