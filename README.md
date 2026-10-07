# Hermes Agency Agents

**English** · [Tiếng Việt](README.vi.md)

A plugin pair for [Hermes Agent](https://hermes-agent.nousresearch.com) that brings the **Agency Agents** expert roster into Hermes: **321 specialist personas across 22 divisions, 5 ready-made expert teams, and a bundled avatar for every expert**.

It is a port of the Agency Agents plugin from DeepSeek Harness ([`@michengai/dsh-agency-agents`](https://github.com/MichengAI/dsh-agency-agents) v1.0.8). The personas come from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents).

<p align="center">
  <img src="avatars/chief-executive-officer.svg" width="56" title="Chief Executive Officer">
  <img src="avatars/engineering-software-architect.svg" width="56" title="Software Architect">
  <img src="avatars/design-ui-designer.svg" width="56" title="UI Designer">
  <img src="avatars/marketing-growth-hacker.svg" width="56" title="Growth Hacker">
  <img src="avatars/security-appsec-engineer.svg" width="56" title="AppSec Engineer">
  <img src="avatars/research-synthesist.svg" width="56" title="Research Synthesist">
  <img src="avatars/product-manager.svg" width="56" title="Product Manager">
</p>

| | |
|---|---|
| Experts | 321 |
| Divisions | 22 |
| Team presets | 5 (editable, and you can add more) |
| Avatars | 321 DiceBear *Lorelei* SVGs, bundled for offline use |
| Backend tools | `agency_agents_search`, `agency_agents_inspect`, `agency_agents_load`, `agency_agents_delegate` |
| Desktop UI | Agency page, chat composer picker, expert/team editor |

---

## Table of contents

1. [What you get](#what-you-get)
2. [How it works](#how-it-works)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Creating and editing experts and teams](#creating-and-editing-experts-and-teams)
6. [Backend tool reference](#backend-tool-reference)
7. [Roster](#roster)
8. [Avatars](#avatars)
9. [Rebuilding from source](#rebuilding-from-source)
10. [Checks](#checks)
11. [Repository layout](#repository-layout)
12. [Troubleshooting](#troubleshooting)
13. [Credits and licenses](#credits-and-licenses)

---

## What you get

The repository has two plugins that work together.

### 1. Backend plugin: `agency-agents-router`

This is a Python Hermes plugin that registers four tools. It keeps the whole roster on disk (`data/agents.json`) and **loads a persona only when it is asked for**. Hermes does not get 321 extra skills crammed into every prompt. The model searches the roster, picks an expert and loads only that one persona.

### 2. Desktop plugin: `agency-agents`

This is a Hermes Desktop plugin (plain ESM, no build step) that adds:

- **An Agency Agents page** in the sidebar, also reachable from the command palette with *Open Agency Agents*:
  - an **Experts** tab with search, a division filter and a card per expert (avatar, name, division, description);
  - a **Teams** tab with every team, its stacked member avatars, and the member names.
- **An Agency button in the chat composer.** It opens a popover with **Experts** and **Teams** tabs, so you can pick one without leaving the chat.
- **An editor** where you can create new experts, edit existing ones, and create or edit teams.

Picking an expert or a team never sends a message on its own. It puts an instruction at the **start of your current draft**, so you can review it, finish typing your task and send it yourself.

---

## How it works

```
┌──────────────────── Hermes Desktop ────────────────────┐
│  Agency page / composer picker                         │
│        │  choose expert or team                        │
│        ▼                                               │
│  instruction inserted at the start of the draft        │
└────────┬───────────────────────────────────────────────┘
         │ you send the message
         ▼
┌──────────────────── Hermes Agent ──────────────────────┐
│  model calls agency_agents_load / _delegate            │
│        │                                               │
│        ▼                                               │
│  agency-agents-router reads data/agents.json           │
│  → returns ONE persona prompt (or runs a subagent)     │
└────────────────────────────────────────────────────────┘
```

**Built-in expert.** The picker inserts a short instruction:

```text
Use agency_agents_load with slug "chief-executive-officer", then answer as Chief Executive Officer (CEO): <your task>
```

The model calls `agency_agents_load`, gets the full specialist prompt and answers in that role.

**Team.** The picker inserts a coordination instruction that names every member and the team goal. The model then calls `agency_agents_delegate` for each member in parallel and combines what they return:

```text
Use agency-agents-router for this task. Coordinate these experts in parallel: Software Architect, Application Security Engineer, Reality Checker. Synthesize under this goal: Review architecture, security risks, and acceptance boundaries. Task: <your task>
```

**Custom expert, or a built-in expert with an overridden prompt.** The backend does not know about these, so the picker puts the prompt itself into the instruction:

```text
Act as <name>. Follow this specialist prompt:
<your prompt>

Task: <your task>
```

If a team includes custom experts, their prompts are appended to the team instruction in the same way.

---

## Installation

`HERMES_HOME` is your Hermes data folder. By default it is `~/.hermes`; on Windows it is wherever you installed Hermes, e.g. `D:\Hermes`.

### Option A: copy the prebuilt plugins (recommended)

```bash
git clone https://github.com/Egggy1998/hermes-agency-agents.git
cd hermes-agency-agents

cp -r plugins/agency-agents-router   "$HERMES_HOME/plugins/"
cp -r desktop-plugins/agency-agents  "$HERMES_HOME/desktop-plugins/"

hermes plugins enable agency-agents-router
```

Then:

1. **Restart Hermes** so the backend tools are registered.
2. The desktop plugin **hot-loads** within a few seconds. If you do not see it, reload the app window (Ctrl+R / Cmd+R).
3. *Agency Agents* now appears in the sidebar, and an Agency button appears in the chat composer.

### Option B: build straight into Hermes

```bash
python scripts/build.py "$HERMES_HOME"
hermes plugins enable agency-agents-router
```

See [Rebuilding from source](#rebuilding-from-source) for what this needs.

### Verify the install

```bash
hermes plugins list --plain --no-bundled        # agency-agents-router should be enabled
hermes chat -Q -q "Call agency_agents_search with query 'chief executive strategy' and limit 1. Reply with only the returned slug."
# → chief-executive-officer
```

---

## Usage

### From the chat composer

1. Click the **Agency** button at the left of the chat input.
2. Pick the **Experts** or **Teams** tab.
3. Type to search. Experts match on name, description and division; teams match on name, description and member slugs. The list shows up to 50 experts at a time.
4. Click a result. The instruction is placed at the start of your draft, and anything you had already typed is kept.
5. Write your task after it and send.

If no chat composer is focused, a notice asks you to click into the chat and pick again.

### From the Agency page

1. Open **Agency Agents** from the sidebar or the command palette.
2. In **Experts**, search and filter by division, then click **Use expert** on a card.
3. In **Teams**, click **Use team** on a card.
4. The instruction is seated in the active chat's composer.

---

## Creating and editing experts and teams

Use the buttons in the Agency page header and the **Edit** button on each card.

### New expert

| Field | Required | Notes |
|---|---|---|
| Name | yes | Used to generate the slug (`Growth Hacker VN` → `growth-hacker-vn`). The slug must be unique. |
| Division | yes | Any text. New divisions appear in the division filter. |
| Description | no | Shown on the card and searched. |
| System prompt | yes | The full specialist persona. It is sent inline, because the backend does not know about custom experts. |

### Edit an existing expert

- **Built-in expert:** change its name, division or description. The **system prompt override** is optional. Leave it empty to keep using the original persona from the backend, or fill it in to replace that persona.
- **Custom expert:** every field can be edited. The slug never changes after creation.

### New team / edit team

| Field | Required | Notes |
|---|---|---|
| Name | yes | Used to generate the team id; must be unique. |
| Description | no | |
| Goal | no (recommended) | Injected into the team instruction as the synthesis goal. |
| Members | yes | Multi-select from all experts, built-in and custom (Ctrl/Cmd+click). The selected members' avatars are shown under the list. |

The five preset teams can be edited too. Your changes are stored as overrides, so the preset definitions themselves are never modified.

### Where your edits are stored

Custom experts, custom teams and overrides live in the desktop plugin's own storage under the key `hermes.plugin.agency-agents.catalog-v1`:

```json
{
  "experts":         [ { "slug", "name", "division", "description", "prompt", "emoji" } ],
  "expertOverrides": { "<built-in slug>": { "...changed fields" } },
  "teams":           [ { "id", "name", "description", "goal", "members": ["slug", "..."] } ],
  "teamOverrides":   { "<preset id>": { "...changed fields" } }
}
```

- The data is **validated when it is loaded**. Malformed entries are dropped instead of breaking the UI.
- Reinstalling or rebuilding the plugin **does not touch** this data, because it is kept apart from the generated roster.
- Hermes stores it per app profile and per machine, so it does not sync between computers.

---

## Backend tool reference

All four tools belong to the `agency_agents` toolset. Every tool that takes an expert accepts either `slug` or `agent`, and the value can be a slug or an exact display name.

| Tool | Arguments | What it does |
|---|---|---|
| `agency_agents_search` | `query` (required), `division`, `limit` (default 8, max 25) | Ranked search across the roster. Returns slugs, names, divisions and descriptions. |
| `agency_agents_inspect` | `slug` / `agent` | Returns one expert's metadata and source path, without the full prompt. |
| `agency_agents_load` | `slug` / `agent`, `task` | Returns the full specialist prompt, paired with the task if you pass one. The model then adopts the persona. |
| `agency_agents_delegate` | `slug` / `agent`, `task` (required) | Runs the expert as an isolated Hermes **subagent** and returns its result. It waits up to 330 s. If subagents are unavailable or the subagent fails, it returns the persona prompt instead so the model can carry on. |

---

## Roster

### Divisions (22)

| Division | Experts | Division | Experts |
|---|---:|---|---:|
| academic | 7 | marketing | 43 |
| company | 6 | paid-media | 7 |
| design | 11 | product | 5 |
| engineering | 68 | project-management | 7 |
| finance | 9 | research | 1 |
| game-development | 21 | sales | 9 |
| gis | 13 | security | 12 |
| healthcare | 3 | spatial-computing | 6 |
| hr | 2 | specialized | 68 |
| legal | 2 | supply-chain | 4 |
| support | 7 | testing | 10 |

### Team presets (5)

| Team | Members | Goal |
|---|---|---|
| Product Review Team | product-manager, design-ux-researcher, engineering-software-architect | Evaluate the value, usability, and feasibility of a product proposal. |
| Technical Review Team | engineering-software-architect, security-appsec-engineer, testing-reality-checker | Review architecture, security risks, and acceptance boundaries. |
| Content Planning Team | marketing-content-creator, marketing-growth-hacker, research-synthesist | Create evidence-aware topics, positioning, and content outlines. |
| Data Analysis Team | engineering-data-engineer, support-analytics-reporter, engineering-data-visualization-engineer | Produce trustworthy analysis with explicit assumptions and chart guidance. |
| Research Team | research-synthesist, product-trend-researcher, specialized-strategy-duel-agent | Separate verified facts, inference, disagreement, and decision trade-offs. |

The full list of experts is in [`plugins/agency-agents-router/data/agents.json`](plugins/agency-agents-router/data/agents.json), and all the avatars are in the [avatar gallery](avatars/README.md).

---

## Avatars

- Every expert has a **DiceBear [Lorelei](https://www.dicebear.com/styles/lorelei/)** avatar, seeded with its slug. The same expert therefore always gets the same face.
- The background palette is `b6e3f4, c0aede, d1d4f9`.
- All 321 SVGs are stored in [`avatars/`](avatars/) and **embedded in `plugin.js`**. Hermes Desktop loads plugins from a `blob:` URL, so a plugin cannot fetch files that sit next to it. Embedding the SVGs is what lets avatars work offline.
- **Custom experts** get their avatar from `https://api.dicebear.com/10.x/lorelei/svg?seed=<slug>`.
- If an avatar fails to load, the expert's **emoji** is shown instead.
- Teams show **stacked member avatars**: up to 6, plus a `+N` badge for the rest. Hover an avatar to see the expert's name.

---

## Rebuilding from source

You only need to rebuild when you want to regenerate the roster from a newer persona source.

```bash
python scripts/build.py                  # regenerate into this repo
python scripts/build.py "$HERMES_HOME"   # regenerate and install into Hermes
```

| Input | Default | Override |
|---|---|---|
| DSH Agency Agents package (persona Markdown) | `~/.dsh/profiles/desktop/node_modules/@michengai/dsh-agency-agents` | env `DSH_AGENCY_PACKAGE` |
| Backend skeleton (from `msitarzewski/agency-agents` → `integrations/hermes`) | this repo's `plugins/agency-agents-router` | env `AGENCY_HERMES_SKELETON` |

What `build.py` does:

1. Parses the front matter of every persona Markdown file (`name`, `description`, `emoji`, `color`, `vibe`) and checks that no two personas share a slug.
2. Writes the backend: `__init__.py`, `plugin.yaml`, `data/agents.json`, `data/teams.json` and the license files.
3. Downloads any avatar not yet in `avatars/` (8 parallel requests, each checked to be an SVG) and regenerates the gallery.
4. Generates `desktop-plugins/agency-agents/plugin.js` with the roster, the teams and the embedded avatars.

Before it replaces an existing backend directory, `build.py` checks that the directory's `plugin.yaml` belongs to `agency-agents-router`. It will not delete an unrelated folder.

Requirements: Python 3.10+ with only the standard library, plus Node.js if you want to run the JS checks.

---

## Checks

```bash
python scripts/check.py
# check ok: 321 experts, 5 teams, 321 bundled avatars, 4 tools

node desktop-plugins/agency-agents/check-catalog.mjs
# catalog check: ok

node --check desktop-plugins/agency-agents/plugin.js
```

- `check.py` confirms the expert count, that slugs are unique, that every team member exists, that every avatar file is a valid SVG **and** is embedded in `plugin.js`, and that the backend registers all four tools.
- `check-catalog.mjs` tests the custom-catalog logic: slug generation, rejection of malformed storage, persistence, how overrides are merged, and the expert and team instructions (including the inline prompts for custom experts).

---

## Repository layout

```
hermes-agency-agents/
├── plugins/agency-agents-router/     # Backend Hermes plugin (Python)
│   ├── __init__.py                   #   registers the 4 tools
│   ├── plugin.yaml
│   ├── data/agents.json              #   321 experts incl. full persona bodies
│   ├── data/teams.json               #   5 team presets
│   └── AGENCY-AGENTS-LICENSE, DSH-LICENSE, DSH-NOTICE
├── desktop-plugins/agency-agents/    # Hermes Desktop plugin (ESM)
│   ├── plugin.js                     #   UI + roster + embedded avatars (~2 MB)
│   └── check-catalog.mjs             #   custom catalog self-check
├── avatars/                          # 321 Lorelei SVGs + gallery README
├── scripts/
│   ├── build.py                      # generator
│   └── check.py                      # repo self-check
├── README.md / README.vi.md
└── LICENSE
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| The Agency button or sidebar entry does not appear | Reload the window with Ctrl+R. Look in `HERMES_HOME/logs/desktop.log` for `Plugin "agency-agents" failed to load`. |
| The model says the `agency_agents_*` tools do not exist | Run `hermes plugins enable agency-agents-router`, then restart Hermes. |
| "Focus a chat composer, then choose again." | Click into the chat input box, then pick the expert or team again. |
| A custom expert has no avatar | You are offline (custom avatars come from the DiceBear API). The emoji fallback is shown. |
| Saving shows "must create a unique slug/id" | Another expert or team already produces that slug. Rename yours. |
| `agency_agents_delegate` returns a `prompt` instead of a `result` | Subagents are not available in this Hermes runtime. The model continues with the persona prompt. |

---

## Credits and licenses

- **This repository's code** (desktop UI, build and check scripts): [MIT](LICENSE) © Egggy1998.
- **Expert personas:** [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents), MIT © Michael Sitarzewski / AgentLand Contributors. See `plugins/agency-agents-router/AGENCY-AGENTS-LICENSE`.
- **DeepSeek Harness plugin:** [MichengAI/dsh-agency-agents](https://github.com/MichengAI/dsh-agency-agents), Apache-2.0. See `DSH-LICENSE` and `DSH-NOTICE`.
- **Avatars:** [DiceBear](https://github.com/dicebear/dicebear) (MIT), *Lorelei* style, a remix of [Lorelei](https://www.figma.com/community/file/1198749693280469639) by Lisa Wischofsky, released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

This is an independent community port. It is not affiliated with or endorsed by Nous Research, DeepSeek, MichengAI or the Agency Agents authors.
