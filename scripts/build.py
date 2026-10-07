from __future__ import annotations

import json
import shutil
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Usage: python build.py [OUT_ROOT]  (default: repo root; pass your Hermes home to install)
# Env: DSH_AGENCY_PACKAGE = installed @michengai/dsh-agency-agents dir; AGENCY_HERMES_SKELETON = upstream skeleton dir
import os
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
DSH_PACKAGE = Path(os.environ.get("DSH_AGENCY_PACKAGE", Path.home() / ".dsh/profiles/desktop/node_modules/@michengai/dsh-agency-agents"))
SOURCE = DSH_PACKAGE / "assets" / "agency-agents"
REPO = Path(__file__).resolve().parents[1]
ROSTER = REPO / "plugins" / "agency-agents-router" / "data" / "agents.json"
# Upstream msitarzewski/agency-agents Hermes skeleton; the repo's own backend copy is the fallback.
SKELETON = next(p for p in (Path(os.environ.get("AGENCY_HERMES_SKELETON", REPO / "missing")), REPO / "plugins" / "agency-agents-router") if (p / "__init__.py").is_file())
BACKEND = OUT / "plugins" / "agency-agents-router"
DESKTOP = OUT / "desktop-plugins" / "agency-agents"
AVATARS = REPO / "avatars"
AVATAR_API = "https://api.dicebear.com/10.x/lorelei/svg?backgroundColor=b6e3f4,c0aede,d1d4f9&seed="


def fetch_avatar(slug: str) -> None:
    path = AVATARS / f"{slug}.svg"
    if path.is_file():
        return
    with urllib.request.urlopen(AVATAR_API + urllib.parse.quote(slug), timeout=30) as response:
        svg = response.read().decode("utf-8")
    if not svg.lstrip().startswith("<svg"):
        raise SystemExit(f"Bad avatar for {slug}")
    path.write_text(svg, encoding="utf-8")


def load_avatars(agents: list[dict[str, str]]) -> dict[str, str]:
    AVATARS.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(8) as pool:
        list(pool.map(fetch_avatar, [a["slug"] for a in agents]))
    (AVATARS / "README.md").write_text(
        f"# Expert avatars ({len(agents)})\n\nDrawn with [DiceBear](https://github.com/dicebear/dicebear) (MIT) using the [Lorelei](https://www.figma.com/community/file/1198749693280469639) illustration collection by Lisa Wischofsky (CC0 1.0), seed = expert slug. Experts from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents). Thank you! 🙏\n\n"
        + "\n".join(f'<img src="{a["slug"]}.svg" width="64" title="{a["name"]}" alt="{a["name"]}">' for a in agents) + "\n",
        encoding="utf-8",
    )
    return {a["slug"]: (AVATARS / f"{a['slug']}.svg").read_text(encoding="utf-8") for a in agents}


def parse_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    if not text.startswith("---\n"):
        return None
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        return None
    fields: dict[str, str] = {}
    current = ""
    for line in parts[1].splitlines():
        if line.startswith((" ", "\t")) and current and line.strip():
            fields[current] += " " + line.strip()
            continue
        current = ""
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current = key.strip()
        value = value.strip()
        if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[current] = value
    return fields, parts[2].lstrip("\n")


def collect_agents() -> list[dict[str, str]]:
    if not SOURCE.is_dir():
        # No DSH package installed: the committed roster already carries every field + full persona body.
        return json.loads(ROSTER.read_text(encoding="utf-8"))
    agents: list[dict[str, str]] = []
    for path in sorted(SOURCE.rglob("*.md")):
        parsed = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not parsed:
            continue
        fields, body = parsed
        name = fields.get("name", "").strip()
        if not name:
            continue
        rel = path.relative_to(SOURCE)
        agents.append(
            {
                "slug": path.stem,
                "name": name,
                "description": fields.get("descriptionEn", "").strip()
                or fields.get("description", "").strip(),
                "division": rel.parts[0],
                "color": fields.get("color", "").strip(),
                "emoji": fields.get("emoji", "").strip() or "✦",
                "vibe": fields.get("vibe", "").strip(),
                "source_path": str(rel).replace("\\", "/"),
                "body": body,
            }
        )
    agents.sort(key=lambda item: (item["division"], item["name"].lower()))
    slugs = [agent["slug"] for agent in agents]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate slugs: {', '.join(duplicates)}")
    return agents


TEAMS = [
    {
        "id": "team-product",
        "name": "Product Review Team",
        "description": "Review requirements, compare options, and plan iterations across value, usability, and implementation cost.",
        "goal": "Evaluate the value, usability, and feasibility of a product proposal.",
        "members": ["product-manager", "design-ux-researcher", "engineering-software-architect"],
    },
    {
        "id": "team-technical",
        "name": "Technical Review Team",
        "description": "Review architecture, security, and delivery readiness; identify risks, minimal fixes, and acceptance criteria.",
        "goal": "Review architecture, security risks, and acceptance boundaries.",
        "members": ["engineering-software-architect", "security-appsec-engineer", "testing-reality-checker"],
    },
    {
        "id": "team-content",
        "name": "Content Planning Team",
        "description": "Find worthwhile content directions that fit the audience, platform, and available evidence.",
        "goal": "Create evidence-aware topics, positioning, and content outlines.",
        "members": ["marketing-content-creator", "marketing-growth-hacker", "research-synthesist"],
    },
    {
        "id": "team-data",
        "name": "Data Analysis Team",
        "description": "Validate definitions and data quality before explaining results and recommending visualizations.",
        "goal": "Produce trustworthy analysis with explicit assumptions and chart guidance.",
        "members": ["engineering-data-engineer", "support-analytics-reporter", "engineering-data-visualization-engineer"],
    },
    {
        "id": "team-research",
        "name": "Research Team",
        "description": "Synthesize evidence, trends, and competing options into a decision-ready recommendation.",
        "goal": "Separate verified facts, inference, disagreement, and decision trade-offs.",
        "members": ["research-synthesist", "product-trend-researcher", "specialized-strategy-duel-agent"],
    },
]


def install_backend(agents: list[dict[str, str]]) -> None:
    if not (SKELETON / "__init__.py").is_file():
        raise SystemExit(f"Missing generated Hermes skeleton: {SKELETON}")
    if SKELETON.resolve() == BACKEND.resolve():
        pass  # rebuilding in place from the repo's own copy
    elif BACKEND.exists():
        manifest = BACKEND / "plugin.yaml"
        if not manifest.is_file() or "name: agency-agents-router" not in manifest.read_text(encoding="utf-8"):
            raise SystemExit(f"Refusing to replace unowned directory: {BACKEND}")
        shutil.rmtree(BACKEND)
    if SKELETON.resolve() != BACKEND.resolve():
        shutil.copytree(SKELETON, BACKEND, ignore=shutil.ignore_patterns("__pycache__"))
    (BACKEND / "data" / "agents.json").write_text(
        json.dumps(agents, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    (BACKEND / "data" / "teams.json").write_text(
        json.dumps(TEAMS, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (BACKEND / "plugin.yaml").write_text(
        "name: agency-agents-router\n"
        "version: 1.0.8\n"
        f"description: Lazy Hermes router for the {len(agents)}-expert DSH Agency Agents roster.\n"
        "provides_tools:\n"
        "  - agency_agents_search\n"
        "  - agency_agents_inspect\n"
        "  - agency_agents_load\n"
        "  - agency_agents_delegate\n",
        encoding="utf-8",
    )
    (BACKEND / "README.md").write_text(
        "# Agency Agents Router for Hermes\n\n"
        "Converted from `@michengai/dsh-agency-agents` v1.0.8 installed in DeepSeek Harness.\n\n"
        f"- Experts: {len(agents)}\n"
        f"- Divisions: {len({a['division'] for a in agents})}\n"
        "- Tools: search, inspect, load, delegate\n"
        f"- Runtime strategy: lazy on-disk roster; no {len(agents)}-skill prompt inflation\n\n"
        "Restart Hermes after installation so tool discovery reloads the plugin.\n",
        encoding="utf-8",
    )
    for filename in ("LICENSE", "NOTICE"):
        source = DSH_PACKAGE / filename
        if source.is_file():
            shutil.copy2(source, BACKEND / f"DSH-{filename}")
    if (SOURCE / "LICENSE").is_file():
        shutil.copy2(SOURCE / "LICENSE", BACKEND / "AGENCY-AGENTS-LICENSE")


def js_dataset(agents: list[dict[str, str]]) -> str:
    compact = [
        {
            "slug": a["slug"],
            "name": a["name"],
            "division": a["division"],
            "description": a["description"],
            "emoji": a["emoji"],
        }
        for a in agents
    ]
    return json.dumps(compact, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def desktop_plugin(agents: list[dict[str, str]], avatars: dict[str, str]) -> str:
    data = js_dataset(agents)
    teams = json.dumps(TEAMS, ensure_ascii=False, separators=(",", ":"))
    svgs = json.dumps(avatars, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'''import {{ Button, Codicon, COMPOSER_AREAS, Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, Input, PALETTE_AREA, Popover, PopoverContent, PopoverTrigger, ROUTES_AREA, SearchField, SIDEBAR_NAV_AREA, Textarea, host }} from '@hermes/plugin-sdk'
import {{ useEffect, useMemo, useState }} from 'react'
import {{ jsx, jsxs }} from 'react/jsx-runtime'

const ID = 'agency-agents'
const EXPERTS = {data}
const TEAMS = {teams}
// Bundled DiceBear Lorelei SVGs (CC0): the plugin loads from a blob URL, so sibling files can't be fetched.
const AVATARS = {svgs}
let pluginCtx = null

const divisionName = value => value.split('-').map(part => part[0].toUpperCase() + part.slice(1)).join(' ')
const avatarUrl = expert => AVATARS[expert.slug]
  ? `data:image/svg+xml;charset=utf-8,${{encodeURIComponent(AVATARS[expert.slug])}}`
  : `https://api.dicebear.com/10.x/lorelei/svg?seed=${{encodeURIComponent(expert.slug)}}&backgroundColor=b6e3f4,c0aede,d1d4f9`
const CATALOG_KEY = 'catalog-v1'
const EMPTY_CATALOG = {{ experts: [], expertOverrides: {{}}, teams: [], teamOverrides: {{}} }}
let catalog = EMPTY_CATALOG
const catalogListeners = new Set()

const slugify = value => value.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 80)
const normalizeCatalog = value => {{
  const source = value && typeof value === 'object' ? value : {{}}
  return {{
    experts: Array.isArray(source.experts) ? source.experts.filter(item => item && item.slug && item.name && item.prompt) : [],
    expertOverrides: source.expertOverrides && typeof source.expertOverrides === 'object' && !Array.isArray(source.expertOverrides) ? source.expertOverrides : {{}},
    teams: Array.isArray(source.teams) ? source.teams.filter(item => item && item.id && item.name && Array.isArray(item.members)) : [],
    teamOverrides: source.teamOverrides && typeof source.teamOverrides === 'object' && !Array.isArray(source.teamOverrides) ? source.teamOverrides : {{}}
  }}
}}
const saveCatalog = value => {{
  catalog = normalizeCatalog(value)
  pluginCtx.storage.set(CATALOG_KEY, catalog)
  catalogListeners.forEach(listener => listener(catalog))
}}
function useCatalog() {{
  const [value, setValue] = useState(catalog)
  useEffect(() => {{ catalogListeners.add(setValue); return () => catalogListeners.delete(setValue) }}, [])
  return [value, saveCatalog]
}}
const catalogExperts = value => [
  ...EXPERTS.map(expert => {{
    const override = value.expertOverrides[expert.slug]
    return {{ ...expert, ...(override || {{}}), slug: expert.slug, builtin: true, customPrompt: Boolean(override?.prompt) }}
  }}),
  ...value.experts.map(expert => ({{ ...expert, builtin: false, customPrompt: true }}))
]
const catalogTeams = value => [
  ...TEAMS.map(team => ({{ ...team, ...(value.teamOverrides[team.id] || {{}}), id: team.id, builtin: true }})),
  ...value.teams.map(team => ({{ ...team, builtin: false }}))
]
const expertInstruction = expert => expert.customPrompt
  ? `Act as ${{expert.name}}. Follow this specialist prompt:\n${{expert.prompt}}\n\nTask: `
  : `Use agency_agents_load with slug "${{expert.slug}}", then answer as ${{expert.name}}: `
const teamInstruction = (team, experts) => {{
  const members = team.members.map(slug => experts.find(expert => expert.slug === slug)).filter(Boolean)
  const custom = members.filter(expert => expert.customPrompt)
  const base = `Coordinate these experts in parallel: ${{members.map(expert => expert.name).join(', ')}}. Synthesize under this goal: ${{(team.goal || team.name).replace(/[.]+$/, '')}}. `
  return custom.length ? `${{base}}Custom specialist prompts:\n${{custom.map(expert => `## ${{expert.name}}\n${{expert.prompt}}`).join(`\n\n`)}}\n\nTask: ` : `Use agency-agents-router for this task. ${{base}}Task: `
}}

const teamMembers = (team, experts) => team.members.map(slug => experts.find(expert => expert.slug === slug) || {{ slug, name: slug }})

function Avatar({{ expert, className = '', style }}) {{
  return jsxs('span', {{ className: `relative flex shrink-0 items-center justify-center overflow-hidden bg-(--chrome-action-hover) ${{className}}`, style, children: [
    jsx('span', {{ 'aria-hidden': true, children: expert.emoji || '✦' }}),
    jsx('img', {{ alt: '', className: 'absolute inset-0 size-full object-cover', loading: 'lazy', onError: event => event.currentTarget.remove(), referrerPolicy: 'no-referrer', src: avatarUrl(expert) }})
  ] }})
}}

function AvatarStack({{ members, className = '' }}) {{
  const shown = members.slice(0, 6)
  // inline style: plugin classes aren't guaranteed in the host Tailwind build
  const ring = index => ({{ marginLeft: index ? -8 : 0, boxShadow: '0 0 0 2px var(--background)' }})
  return jsxs('span', {{ className: `flex items-center ${{className}}`, children: [
    ...shown.map((expert, index) => jsx('span', {{ title: expert.name, className: 'rounded-full', style: ring(index), children: jsx(Avatar, {{ expert, className: 'size-7 rounded-full text-xs' }}) }}, expert.slug)),
    members.length > shown.length ? jsx('span', {{ className: 'flex size-7 items-center justify-center rounded-full bg-(--chrome-action-hover) text-xs text-(--ui-text-secondary)', style: ring(1), children: `+${{members.length - shown.length}}` }}) : null
  ] }})
}}

// Instructions that call the backend fail silently when its toolset is off. This sees config state only:
// a chat opened before the plugin was enabled still lacks the tools (sessions snapshot toolsets), hence the hint.
const TOOLS_OFF = 'Agency tools are off: run `hermes plugins enable agency-agents-router`, restart Hermes, then open a new chat.'
const warnIfToolsOff = async text => {{
  if (!/agency_agents_|agency-agents-router/.test(text)) return
  try {{
    const toolset = (await host.toolsets.list()).find(item => item.name === 'agency_agents')
    if (!toolset?.enabled) host.notify({{ kind: 'warning', message: TOOLS_OFF }})
  }} catch {{}}  // backend unreachable: nothing reliable to report
}}

function seatPrompt(text) {{
  warnIfToolsOff(text)
  const sessionId = host.state.activeSessionId.get()
  host.navigate(sessionId ? `/session/${{sessionId}}` : '/')
  const target = sessionId || 'new'
  const attempt = async retries => {{
    if (await host.composer.setDraft(target, text)) {{
      host.composer.focus(target)
      return
    }}
    if (retries > 0) pluginCtx.setTimeout(() => attempt(retries - 1), 120)
    else host.notify({{ kind: 'warning', message: 'Open a conversation, then choose the expert again.' }})
  }}
  pluginCtx.setTimeout(() => attempt(4), 80)
}}

function ExpertCard({{ expert, onEdit }}) {{
  const prompt = expertInstruction(expert)
  return jsxs('article', {{
    className: 'flex min-h-48 flex-col rounded-2xl border border-(--ui-stroke-secondary) p-4 transition-colors hover:border-(--ui-accent)',
    children: [
      jsxs('div', {{ className: 'flex items-start gap-3', children: [
        jsx(Avatar, {{ expert, className: 'size-11 rounded-xl text-xl' }}),
        jsxs('div', {{ className: 'min-w-0', children: [
          jsx('h3', {{ className: 'font-semibold leading-tight text-foreground', children: expert.name }}),
          jsx('div', {{ className: 'mt-1 text-xs text-(--ui-text-tertiary)', children: divisionName(expert.division) }})
        ] }})
      ] }}),
      jsx('p', {{ className: 'mt-3 line-clamp-4 flex-1 text-sm leading-6 text-(--ui-text-secondary)', children: expert.description || 'Specialist agent from The Agency roster.' }}),
      jsxs('div', {{ className: 'mt-4 flex gap-2', children: [
        jsx('button', {{ type: 'button', className: 'inline-flex h-9 flex-1 items-center justify-center rounded-xl bg-(--ui-accent) px-3 text-sm font-medium text-(--ui-accent-foreground) hover:opacity-90', onClick: () => seatPrompt(prompt), children: 'Use expert' }}),
        jsx('button', {{ type: 'button', className: 'h-9 rounded-xl border border-(--ui-stroke-secondary) px-3 text-sm text-(--ui-text-secondary) hover:bg-(--chrome-action-hover)', onClick: () => onEdit(expert), children: 'Edit' }})
      ] }})
    ]
  }})
}}

function TeamCard({{ team, experts, onEdit }}) {{
  const members = teamMembers(team, experts)
  const prompt = teamInstruction(team, experts)
  return jsxs('article', {{
    className: 'rounded-2xl border border-(--ui-stroke-secondary) p-4',
    children: [
      jsx('h3', {{ className: 'font-semibold text-foreground', children: team.name }}),
      jsx('p', {{ className: 'mt-2 text-sm leading-6 text-(--ui-text-secondary)', children: team.description }}),
      jsx(AvatarStack, {{ members, className: 'mt-3' }}),
      jsx('div', {{ className: 'mt-2 text-xs leading-5 text-(--ui-text-tertiary)', children: members.map(item => item.name).join(' · ') }}),
      jsxs('div', {{ className: 'mt-4 flex gap-2', children: [
        jsx('button', {{ type: 'button', className: 'inline-flex h-9 flex-1 items-center justify-center rounded-xl bg-(--ui-accent) px-3 text-sm font-medium text-(--ui-accent-foreground) hover:opacity-90', onClick: () => seatPrompt(prompt), children: 'Use team' }}),
        jsx('button', {{ type: 'button', className: 'h-9 rounded-xl border border-(--ui-stroke-secondary) px-3 text-sm text-(--ui-text-secondary) hover:bg-(--chrome-action-hover)', onClick: () => onEdit(team), children: 'Edit' }})
      ] }})
    ]
  }})
}}

function CatalogEditor({{ editor, experts, onClose, onSave }}) {{
  const [draft, setDraft] = useState({{}})
  useEffect(() => {{
    if (!editor) return
    setDraft(editor.item ? {{ ...editor.item, members: [...(editor.item.members || [])] }} : editor.kind === 'expert'
      ? {{ name: '', division: 'custom', description: '', prompt: '' }}
      : {{ name: '', description: '', goal: '', members: [] }})
  }}, [editor])
  if (!editor) return null
  const field = (key, value) => setDraft(current => ({{ ...current, [key]: value }}))
  const submit = event => {{
    event.preventDefault()
    if (!draft.name?.trim() || (editor.kind === 'expert' ? !editor.item?.builtin && !draft.prompt?.trim() : !draft.members?.length)) return
    if (onSave(editor.kind, draft)) onClose()
  }}
  return jsx(Dialog, {{
    open: true,
    onOpenChange: value => {{ if (!value) onClose() }},
    children: jsxs(DialogContent, {{ className: 'max-h-[85vh] max-w-2xl overflow-y-auto', children: [
      jsx(DialogHeader, {{ children: jsx(DialogTitle, {{ children: `${{editor.item ? 'Edit' : 'New'}} ${{editor.kind}}` }}) }}),
      jsxs('form', {{ className: 'grid gap-4', onSubmit: submit, children: [
        jsxs('label', {{ className: 'grid gap-1 text-sm text-(--ui-text-secondary)', children: ['Name', jsx(Input, {{ required: true, value: draft.name || '', onChange: event => field('name', event.target.value) }})] }}),
        editor.kind === 'expert' ? jsxs('label', {{ className: 'grid gap-1 text-sm text-(--ui-text-secondary)', children: ['Division', jsx(Input, {{ required: true, value: draft.division || '', onChange: event => field('division', event.target.value) }})] }}) : null,
        jsxs('label', {{ className: 'grid gap-1 text-sm text-(--ui-text-secondary)', children: ['Description', jsx(Textarea, {{ rows: 3, value: draft.description || '', onChange: event => field('description', event.target.value) }})] }}),
        editor.kind === 'expert'
          ? jsxs('label', {{ className: 'grid gap-1 text-sm text-(--ui-text-secondary)', children: [editor.item?.builtin ? 'System prompt override (empty = original)' : 'System prompt', jsx(Textarea, {{ required: !editor.item?.builtin, rows: 12, value: draft.prompt || '', onChange: event => field('prompt', event.target.value) }})] }})
          : jsxs('div', {{ className: 'grid gap-3', children: [
              jsxs('label', {{ className: 'grid gap-1 text-sm text-(--ui-text-secondary)', children: ['Goal', jsx(Textarea, {{ rows: 3, value: draft.goal || '', onChange: event => field('goal', event.target.value) }})] }}),
              jsxs('label', {{ className: 'grid gap-1 text-sm text-(--ui-text-secondary)', children: ['Members', jsx('select', {{ className: 'h-52 rounded-lg border border-(--ui-stroke-secondary) bg-background p-2 text-sm text-foreground', multiple: true, required: true, value: draft.members || [], onChange: event => field('members', Array.from(event.target.selectedOptions, option => option.value)), children: experts.map(expert => jsx('option', {{ value: expert.slug, children: `${{expert.name}} · ${{expert.slug}}` }}, expert.slug)) }})] }}),
              draft.members?.length ? jsx(AvatarStack, {{ members: teamMembers(draft, experts) }}) : null
            ] }}),
        jsxs(DialogFooter, {{ children: [
          jsx(Button, {{ type: 'button', variant: 'ghost', onClick: onClose, children: 'Cancel' }}),
          jsx(Button, {{ type: 'submit', children: 'Save' }})
        ] }})
      ] }})
    ] }})
  }})
}}

function ExpertPicker() {{
  const [catalogState] = useCatalog()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [tab, setTab] = useState('experts')
  const experts = useMemo(() => catalogExperts(catalogState), [catalogState])
  const teams = useMemo(() => catalogTeams(catalogState), [catalogState])
  const matches = useMemo(() => {{
    const needle = query.trim().toLowerCase()
    return experts.filter(expert => !needle || `${{expert.name}} ${{expert.description}} ${{expert.division}}`.toLowerCase().includes(needle)).slice(0, 50)
  }}, [experts, query])
  const teamMatches = useMemo(() => {{
    const needle = query.trim().toLowerCase()
    return teams.filter(team => !needle || `${{team.name}} ${{team.description}} ${{team.members.join(' ')}}`.toLowerCase().includes(needle))
  }}, [query, teams])

  const insert = async instruction => {{
    if (!(await host.composer.insertText(null, instruction, {{ mode: 'prefix' }}))) {{
      host.notify({{ kind: 'warning', message: 'Focus a chat composer, then choose again.' }})
      return
    }}
    warnIfToolsOff(instruction)
    setOpen(false)
    setQuery('')
    host.composer.focus(null)
  }}

  return jsx(Popover, {{
    open,
    onOpenChange: setOpen,
    children: jsxs('div', {{ children: [
      jsx(PopoverTrigger, {{
        asChild: true,
        children: jsx(Button, {{
          'aria-label': 'Choose Agency expert',
          title: 'Choose Agency expert',
          size: 'icon',
          type: 'button',
          variant: 'ghost',
          children: jsx(Codicon, {{ name: 'organization', size: '0.875rem' }})
        }})
      }}),
      jsxs(PopoverContent, {{
        align: 'start',
        side: 'top',
        className: 'w-80 p-2',
        variant: 'menu',
        children: [
          jsxs('div', {{ className: 'mb-2 flex rounded-lg border border-(--ui-stroke-secondary) p-0.5', children: [
            jsx('button', {{ type: 'button', onClick: () => setTab('experts'), className: `flex-1 rounded-md px-2 py-1 text-xs ${{tab === 'experts' ? 'bg-(--chrome-action-hover) text-foreground' : 'text-(--ui-text-tertiary)'}}`, children: `Experts ${{experts.length}}` }}),
            jsx('button', {{ type: 'button', onClick: () => setTab('teams'), className: `flex-1 rounded-md px-2 py-1 text-xs ${{tab === 'teams' ? 'bg-(--chrome-action-hover) text-foreground' : 'text-(--ui-text-tertiary)'}}`, children: `Teams ${{teams.length}}` }})
          ] }}),
          jsx(SearchField, {{ 'aria-label': 'Search Agency experts or teams', containerClassName: 'w-full', onChange: setQuery, placeholder: tab === 'experts' ? 'Search experts' : 'Search teams', value: query }}),
          tab === 'experts' ? jsx('div', {{
            className: 'mt-2 max-h-72 overflow-y-auto',
            children: matches.map(expert => jsxs('button', {{
              type: 'button',
              className: 'flex w-full items-start gap-2 rounded-lg px-2 py-2 text-left hover:bg-(--chrome-action-hover)',
              onClick: () => insert(expertInstruction(expert)),
              children: [
                jsx(Avatar, {{ expert, className: 'mt-0.5 size-7 rounded-lg text-sm' }}),
                jsxs('span', {{ className: 'min-w-0', children: [
                  jsx('span', {{ className: 'block truncate text-sm font-medium text-foreground', children: expert.name }}),
                  jsx('span', {{ className: 'block truncate text-xs text-(--ui-text-tertiary)', children: divisionName(expert.division) }})
                ] }})
              ]
            }}, expert.slug))
          }}) : jsx('div', {{
            className: 'mt-2 max-h-72 overflow-y-auto',
            children: teamMatches.map(team => jsxs('button', {{
              type: 'button',
              className: 'w-full rounded-lg px-2 py-2 text-left hover:bg-(--chrome-action-hover)',
              onClick: () => insert(teamInstruction(team, experts)),
              children: [
                jsx('span', {{ className: 'block truncate text-sm font-medium text-foreground', children: team.name }}),
                jsx(AvatarStack, {{ members: teamMembers(team, experts), className: 'mt-1.5' }})
              ]
            }}, team.id))
          }}),
          (tab === 'experts' ? matches : teamMatches).length ? null : jsx('div', {{ className: 'px-2 py-6 text-center text-sm text-(--ui-text-tertiary)', children: 'No match' }})
        ]
      }})
    ] }})
  }})
}}

function AgencyPage() {{
  const [catalogState] = useCatalog()
  const [query, setQuery] = useState('')
  const [division, setDivision] = useState('all')
  const [tab, setTab] = useState('experts')
  const [editor, setEditor] = useState(null)
  const experts = useMemo(() => catalogExperts(catalogState), [catalogState])
  const teams = useMemo(() => catalogTeams(catalogState), [catalogState])
  const divisions = useMemo(() => ['all', ...new Set(experts.map(item => item.division))], [experts])
  const filtered = useMemo(() => {{
    const needle = query.trim().toLowerCase()
    return experts.filter(item => (division === 'all' || item.division === division) && (!needle || `${{item.name}} ${{item.description}} ${{item.division}}`.toLowerCase().includes(needle)))
  }}, [division, experts, query])
  const saveItem = (kind, draft) => {{
    const next = {{ ...catalogState }}
    if (kind === 'expert') {{
      const slug = editor.item?.slug || slugify(draft.name)
      if (!slug || (!editor.item && experts.some(expert => expert.slug === slug))) return host.notify({{ kind: 'error', message: 'Expert name must create a unique slug.' }})
      const value = {{ slug, name: draft.name.trim(), division: draft.division.trim(), description: draft.description?.trim() || '', prompt: draft.prompt?.trim() || '', emoji: draft.emoji || '✦' }}
      if (editor.item?.builtin) next.expertOverrides = {{ ...next.expertOverrides, [slug]: value }}
      else next.experts = editor.item ? next.experts.map(item => item.slug === slug ? value : item) : [...next.experts, value]
    }} else {{
      const id = editor.item?.id || slugify(draft.name)
      if (!id || (!editor.item && teams.some(team => team.id === id))) return host.notify({{ kind: 'error', message: 'Team name must create a unique id.' }})
      const value = {{ id, name: draft.name.trim(), description: draft.description?.trim() || '', goal: draft.goal?.trim() || '', members: [...new Set(draft.members)] }}
      if (editor.item?.builtin) next.teamOverrides = {{ ...next.teamOverrides, [id]: value }}
      else next.teams = editor.item ? next.teams.map(item => item.id === id ? value : item) : [...next.teams, value]
    }}
    saveCatalog(next)
    host.notify({{ kind: 'success', message: `${{kind === 'expert' ? 'Expert' : 'Team'}} saved.` }})
    return true
  }}

  return jsxs('div', {{ className: 'h-full overflow-auto p-5', children: [
    jsxs('header', {{ className: 'mb-5 flex flex-wrap items-end justify-between gap-3', children: [
      jsxs('div', {{ children: [
        jsx('h1', {{ className: 'text-2xl font-semibold tracking-tight text-foreground', children: 'Agency Agents' }}),
        jsx('p', {{ className: 'mt-1 text-sm text-(--ui-text-tertiary)', children: `${{experts.length}} experts · ${{divisions.length - 1}} divisions` }})
      ] }}),
      jsxs('div', {{ className: 'flex flex-wrap gap-2', children: [
        jsx(Button, {{ variant: 'outline', onClick: () => setEditor({{ kind: 'expert' }}), children: 'New expert' }}),
        jsx(Button, {{ variant: 'outline', onClick: () => setEditor({{ kind: 'team' }}), children: 'New team' }}),
        jsxs('div', {{ className: 'flex rounded-xl border border-(--ui-stroke-secondary) p-1', children: [
          jsx('button', {{ type: 'button', onClick: () => setTab('experts'), className: `rounded-lg px-3 py-1.5 text-sm ${{tab === 'experts' ? 'bg-(--chrome-action-hover) text-foreground' : 'text-(--ui-text-tertiary)'}}`, children: `Experts ${{experts.length}}` }}),
          jsx('button', {{ type: 'button', onClick: () => setTab('teams'), className: `rounded-lg px-3 py-1.5 text-sm ${{tab === 'teams' ? 'bg-(--chrome-action-hover) text-foreground' : 'text-(--ui-text-tertiary)'}}`, children: `Teams ${{teams.length}}` }})
        ] }})
      ] }})
    ] }}),
    tab === 'experts' ? jsxs('div', {{ children: [
      jsxs('div', {{ className: 'mb-4 grid gap-3 md:grid-cols-[1fr_240px]', children: [
        jsx('input', {{ value: query, onChange: event => setQuery(event.target.value), placeholder: 'Search experts by role or capability', className: 'h-10 rounded-xl border border-(--ui-stroke-secondary) bg-background px-3 text-sm text-foreground outline-none placeholder:text-(--ui-text-quaternary) focus:border-(--ui-accent)' }}),
        jsx('select', {{ value: division, onChange: event => setDivision(event.target.value), className: 'h-10 rounded-xl border border-(--ui-stroke-secondary) bg-background px-3 text-sm text-foreground outline-none', children: divisions.map(value => jsx('option', {{ value, children: value === 'all' ? 'All divisions' : divisionName(value) }}, value)) }})
      ] }}),
      jsx('div', {{ className: 'mb-3 text-xs text-(--ui-text-tertiary)', children: `${{filtered.length}} matching experts` }}),
      jsx('div', {{ className: 'grid gap-3 pb-8', style: {{ gridTemplateColumns: 'repeat(auto-fill,minmax(250px,1fr))' }}, children: filtered.map(expert => jsx(ExpertCard, {{ expert, onEdit: item => setEditor({{ kind: 'expert', item }}) }}, expert.slug)) }})
    ] }}) : jsx('div', {{ className: 'grid gap-3 pb-8', style: {{ gridTemplateColumns: 'repeat(auto-fill,minmax(300px,1fr))' }}, children: teams.map(team => jsx(TeamCard, {{ team, experts, onEdit: item => setEditor({{ kind: 'team', item }}) }}, team.id)) }}),
    jsx(CatalogEditor, {{ editor, experts, onClose: () => setEditor(null), onSave: saveItem }})
  ] }})
}}

export default {{
  id: ID,
  name: 'Agency Agents',
  register(ctx) {{
    pluginCtx = ctx
    catalog = normalizeCatalog(ctx.storage.get(CATALOG_KEY, EMPTY_CATALOG))
    ctx.onDispose(() => {{ pluginCtx = null; catalogListeners.clear() }})
    ctx.registerMany([
      {{ id: 'page', area: ROUTES_AREA, data: {{ path: '/agency-agents' }}, render: () => jsx(AgencyPage, {{}}) }},
      {{ id: 'nav', area: SIDEBAR_NAV_AREA, data: {{ path: '/agency-agents', label: 'Agency Agents', codicon: 'organization' }} }},
      {{ id: 'composer-picker', area: COMPOSER_AREAS.leading, render: () => jsx(ExpertPicker, {{}}) }},
      {{ id: 'open', area: PALETTE_AREA, data: {{ id: 'agency-agents.open', label: 'Open Agency Agents', keywords: ['experts', 'agency', 'agents', 'team'], run: () => host.navigate('/agency-agents') }} }}
    ])
  }}
}}
'''


def install_desktop(agents: list[dict[str, str]]) -> None:
    DESKTOP.mkdir(parents=True, exist_ok=True)
    (DESKTOP / "plugin.js").write_text(desktop_plugin(agents, load_avatars(agents)), encoding="utf-8")
    (DESKTOP / "README.md").write_text(
        "# Agency Agents for Hermes Desktop\n\n"
        "Native roster page for the converted DeepSeek Harness Agency Agents plugin.\n"
        "Use a card to seat a lazy-router instruction in the active Hermes composer.\n",
        encoding="utf-8",
    )


def main() -> None:
    agents = collect_agents()
    manifest = DSH_PACKAGE / "package.json"
    source = f"dsh {json.loads(manifest.read_text(encoding='utf-8')).get('version')}" if SOURCE.is_dir() else "committed roster"
    install_backend(agents)
    install_desktop(agents)
    print(json.dumps({
        "source": source,
        "experts": len(agents),
        "divisions": len({agent['division'] for agent in agents}),
        "teams": len(TEAMS),
        "backend": str(BACKEND),
        "desktop": str(DESKTOP),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
