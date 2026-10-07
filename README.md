# Hermes Agency Agents

**English** · [Tiếng Việt](README.vi.md)

A plugin pair for [Hermes Agent](https://hermes-agent.nousresearch.com) that brings the **Agency Agents** expert roster into Hermes: **324 specialist personas across 22 divisions, 23 ready-made expert teams, and a bundled avatar for every expert**.

It is a port of the Agency Agents plugin from DeepSeek Harness ([`@michengai/dsh-agency-agents`](https://github.com/MichengAI/dsh-agency-agents) v1.0.8). The personas come from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents).

> 🙏 **Built on the shoulders of open source.** All 324 experts come from **[The Agency — msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)** by Michael Sitarzewski and contributors. Every avatar is drawn with the open-source **[DiceBear](https://github.com/dicebear/dicebear)** avatar library and Lisa Wischofsky's **[Lorelei](https://www.dicebear.com/styles/lorelei/)** illustration collection. Thank you! See [Acknowledgements](#acknowledgements).

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
| Experts | 324 |
| Divisions | 22 |
| Team presets | 23 (editable, and you can add more) |
| Avatars | 324 DiceBear *Lorelei* SVGs, bundled for offline use |
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
13. [Acknowledgements](#acknowledgements)
14. [Credits and licenses](#credits-and-licenses)

---

## What you get

The repository has two plugins that work together.

### 1. Backend plugin: `agency-agents-router`

This is a Python Hermes plugin that registers four tools. It keeps the whole roster on disk (`data/agents.json`) and **loads a persona only when it is asked for**. Hermes does not get 324 extra skills crammed into every prompt. The model searches the roster, picks an expert and loads only that one persona.

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

1. **Restart Hermes and open a new chat** so the backend tools are registered. A chat that was already open before you enabled the plugin will not get the tools.
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
| Members | yes | Current members are shown as chips (× removes one). Search below to tick more experts, built-in or custom. |

The preset teams can be edited too. Your changes are stored as overrides, so the preset definitions themselves are never modified.

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
| company | 9 | paid-media | 7 |
| design | 11 | product | 5 |
| engineering | 68 | project-management | 7 |
| finance | 9 | research | 1 |
| game-development | 21 | sales | 9 |
| gis | 13 | security | 12 |
| healthcare | 3 | spatial-computing | 6 |
| hr | 2 | specialized | 68 |
| legal | 2 | supply-chain | 4 |
| support | 7 | testing | 10 |

### Team presets (23)

| Team | Members | Goal |
|---|---|---|
| Product Review Team | product-manager, design-ux-researcher, engineering-software-architect | Evaluate the value, usability, and feasibility of a product proposal. |
| Technical Review Team | engineering-software-architect, security-appsec-engineer, testing-reality-checker | Review architecture, security risks, and acceptance boundaries. |
| Content Planning Team | marketing-content-creator, marketing-growth-hacker, research-synthesist | Create evidence-aware topics, positioning, and content outlines. |
| Data Analysis Team | engineering-data-engineer, support-analytics-reporter, engineering-data-visualization-engineer | Produce trustworthy analysis with explicit assumptions and chart guidance. |
| Research Team | research-synthesist, product-trend-researcher, specialized-strategy-duel-agent | Separate verified facts, inference, disagreement, and decision trade-offs. |
| Executive Leadership Team | chief-executive-officer, chief-financial-officer, chief-operating-officer, chief-technology-officer, chief-product-officer, chief-marketing-officer, chief-revenue-officer, chief-people-officer, chief-legal-officer, chief-of-staff | Turn a company-level question into one decision with owner, budget, risks, and a 90-day execution plan. |
| Product Discovery Team | product-manager, design-ux-researcher, product-feedback-synthesizer, product-trend-researcher, product-sprint-prioritizer | Turn raw ideas and user signals into a validated problem, target user, success metric, and prioritized MVP scope. |
| Product Design Studio | design-ux-architect, design-ui-designer, design-ux-researcher, design-brand-guardian, design-ui-finish-gate-reviewer, testing-accessibility-auditor | Deliver user flows, wireframe-to-UI direction, design tokens, and a finish-gate review with accessibility issues called out. |
| Product Engineering Squad | engineering-software-architect, engineering-senior-developer, engineering-frontend-developer, engineering-backend-architect, engineering-mobile-app-builder, engineering-rapid-prototyper, engineering-code-reviewer | Produce a buildable technical plan: architecture, data model, API contracts, task breakdown, risks, and review checklist. |
| AI Product Team | engineering-ai-engineer, engineering-prompt-engineer, engineering-rag-pipeline-engineer, engineering-multi-agent-systems-architect, specialized-model-qa, security-ai-generated-code-auditor | Choose the right AI architecture, define evals and guardrails, and estimate quality, latency, and cost before shipping. |
| Platform & Reliability Team | engineering-devops-automator, engineering-sre, engineering-database-optimizer, engineering-finops-engineer, engineering-incident-response-commander, security-cloud-security-architect | Define deploy pipeline, SLOs, monitoring, scaling and cost plan, plus an incident runbook. |
| QA & Release Team | testing-test-automation-engineer, testing-api-tester, testing-performance-benchmarker, testing-evidence-collector, testing-reality-checker, engineering-mobile-release-engineer | Produce a test plan, automation scope, performance budget, and a go/no-go release verdict backed by evidence. |
| Security & Privacy Team | security-architect, security-appsec-engineer, security-penetration-tester, security-secrets-credential-engineer, engineering-privacy-engineer, security-compliance-auditor | Deliver a threat model, prioritized vulnerability list with minimal fixes, secrets/auth review, and privacy/compliance gaps. |
| Delivery & PMO Team | project-manager-senior, project-management-project-shepherd, project-management-experiment-tracker, project-management-jira-workflow-steward, project-management-meeting-notes-specialist | Turn goals into a milestone plan with owners, dependencies, risks, experiment tracking, and weekly status. |
| Growth Marketing Powerhouse | chief-marketing-officer, marketing-growth-hacker, design-brand-guardian, marketing-content-creator, marketing-seo-specialist, marketing-ai-citation-strategist, marketing-social-media-strategist, marketing-tiktok-strategist, paid-media-paid-social-strategist, paid-media-creative-strategist, paid-media-tracking-specialist, marketing-email-strategist, marketing-pr-communications-manager, support-analytics-reporter | Build a channel-by-channel growth plan with positioning, offer, content and creative angles, paid budget split, tracking, and weekly KPIs tied to revenue. |
| Build 0 · Go/No-go Decision | chief-executive-officer, chief-financial-officer, chief-product-officer, chief-marketing-officer, product-trend-researcher, research-synthesist | Decide GO or NO-GO for the idea: target customer, painful problem, market and competitor evidence, business model, budget, and 90-day plan. Save the decision memo to docs/00-decision.md in the project folder |
| Build 1 · Discovery & PRD | product-manager, design-ux-researcher, product-feedback-synthesizer, product-trend-researcher, product-sprint-prioritizer | Read docs/00-decision.md. Define problem, primary persona, jobs-to-be-done, MVP limited to 3-5 features, explicit out-of-scope list, and success metrics. Save to docs/01-prd.md |
| Build 2 · Design & Architecture | product-manager, design-ux-architect, design-ui-designer, engineering-software-architect, engineering-backend-architect, engineering-ai-engineer | Read docs/01-prd.md. Save user flows, screen list, and UI direction/tokens to docs/02-design.md. Save architecture, stack, data model, API contracts, AI approach if any, and an ordered task breakdown with milestones to docs/03-tech-plan.md |
| Build 2b · Pre-launch Marketing | chief-marketing-officer, marketing-growth-hacker, design-brand-guardian, marketing-content-creator, marketing-seo-specialist, marketing-social-media-strategist, marketing-email-strategist | Read docs/01-prd.md. Define positioning and offer, waitlist landing page copy, pre-launch content calendar, channel priorities, and waitlist KPI targets. Save to docs/04-gtm.md |
| Build 3 · Build Sprint | project-manager-senior, engineering-senior-developer, engineering-frontend-developer, engineering-backend-architect, engineering-rapid-prototyper, engineering-code-reviewer | Read docs/03-tech-plan.md and docs/05-progress.md if it exists. Implement the next milestone only, review the code, and append what shipped, what is blocked, and the next milestone to docs/05-progress.md |
| Build 4 · Release Gate | testing-reality-checker, testing-test-automation-engineer, testing-api-tester, testing-performance-benchmarker, security-appsec-engineer, security-secrets-credential-engineer, engineering-sre | Test the MVP for functional bugs, API contract breaks, performance, security (auth, secrets, OWASP), and production readiness. Default to NO-GO unless evidence proves otherwise. Save the verdict with blocking issues and minimal fixes to docs/06-release-verdict.md |
| Build 5 · Launch & Growth | chief-marketing-officer, paid-media-paid-social-strategist, paid-media-creative-strategist, paid-media-tracking-specialist, marketing-tiktok-strategist, marketing-content-creator, support-analytics-reporter | Read docs/04-gtm.md and docs/06-release-verdict.md. Run the launch plan: channels, ad creatives and budget split, tracking setup, and launch-week schedule. Then report funnel KPIs and next actions to docs/07-kpi-week-N.md |
| Build 6 · Monthly Iterate | chief-executive-officer, chief-financial-officer, product-manager, product-feedback-synthesizer, support-analytics-reporter, product-sprint-prioritizer | Read the latest docs/07-kpi-week-*.md and user feedback. Decide keep / cut / build next, update unit economics, and save the next PRD to docs/01-prd-vN.md, then restart from Build 2 |

**Building a product from zero:** run the `Build 0` → `Build 6` teams in order. Each one reads the previous phase's file and writes the next one under `docs/` in your project folder, so add the project path when you use the team (for example `Project: D:/work/my-app. Idea: ...`). `Build 2` and `Build 2b` can run in parallel; repeat `Build 3` per milestone; `Build 6` loops back to `Build 2` every month.

The full list of experts is in [`plugins/agency-agents-router/data/agents.json`](plugins/agency-agents-router/data/agents.json), and all the avatars are in the [avatar gallery](avatars/README.md).

---

## Avatars

- Every expert has a **DiceBear [Lorelei](https://www.dicebear.com/styles/lorelei/)** avatar, seeded with its slug. The same expert therefore always gets the same face.
- The background palette is `b6e3f4, c0aede, d1d4f9`.
- All 324 SVGs are stored in [`avatars/`](avatars/) and **embedded in `plugin.js`**. Hermes Desktop loads plugins from a `blob:` URL, so a plugin cannot fetch files that sit next to it. Embedding the SVGs is what lets avatars work offline.
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
| DSH Agency Agents package (persona Markdown), optional | `~/.dsh/profiles/desktop/node_modules/@michengai/dsh-agency-agents`. If it is not installed, the build uses the committed `data/agents.json`, so a fresh clone builds with no extra setup. | env `DSH_AGENCY_PACKAGE` |
| Backend skeleton (from `msitarzewski/agency-agents` → `integrations/hermes`) | this repo's `plugins/agency-agents-router` | env `AGENCY_HERMES_SKELETON` |

What `build.py` does:

1. Parses the front matter of every persona Markdown file (`name`, `description`, `emoji`, `color`, `vibe`) and checks that no two personas share a slug.
2. Writes the backend: `__init__.py`, `plugin.yaml`, `data/agents.json`, `data/teams.json` and the license files. Team presets come from the committed `data/teams.json`: edit it, then rebuild. Experts that exist only in the committed roster (not in the DSH package) are kept.
3. Downloads any avatar not yet in `avatars/` (8 parallel requests, each checked to be an SVG) and regenerates the gallery.
4. Generates `desktop-plugins/agency-agents/plugin.js` with the roster, the teams and the embedded avatars.

Before it replaces an existing backend directory, `build.py` checks that the directory's `plugin.yaml` belongs to `agency-agents-router`. It will not delete an unrelated folder.

Requirements: Python 3.10+ with only the standard library, plus Node.js if you want to run the JS checks.

---

## Checks

```bash
python scripts/check.py
# check ok: 324 experts, 5 teams, 324 bundled avatars, 4 tools

node desktop-plugins/agency-agents/check-catalog.mjs
# catalog check: ok

node --check desktop-plugins/agency-agents/plugin.js
```

- `check.py` confirms that the roster is non-empty, that slugs are unique, that every expert has a persona body, that every team member exists, that every avatar file is a valid SVG **and** is embedded in `plugin.js`, and that the backend registers all four tools.
- `check-catalog.mjs` tests the custom-catalog logic: slug generation, rejection of malformed storage, persistence, how overrides are merged, the expert and team instructions (including the inline prompts for custom experts), and the "tools are off" warning.

---

## Repository layout

```
hermes-agency-agents/
├── plugins/agency-agents-router/     # Backend Hermes plugin (Python)
│   ├── __init__.py                   #   registers the 4 tools
│   ├── plugin.yaml
│   ├── data/agents.json              #   324 experts incl. full persona bodies
│   ├── data/teams.json               #   5 team presets
│   └── AGENCY-AGENTS-LICENSE, DSH-LICENSE, DSH-NOTICE
├── desktop-plugins/agency-agents/    # Hermes Desktop plugin (ESM)
│   ├── plugin.js                     #   UI + roster + embedded avatars (~2 MB)
│   └── check-catalog.mjs             #   custom catalog self-check
├── avatars/                          # 324 Lorelei SVGs + gallery README
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
| A toast says "Agency tools are off" | The `agency_agents` toolset is disabled. Run `hermes plugins enable agency-agents-router`, restart Hermes, then open a new chat. |
| The model says the `agency_agents_*` tools do not exist, but no toast appeared | The chat was opened before the plugin was enabled. Hermes fixes a session's tools when the session starts, so **open a new chat**. |
| "Focus a chat composer, then choose again." | Click into the chat input box, then pick the expert or team again. |
| A custom expert has no avatar | You are offline (custom avatars come from the DiceBear API). The emoji fallback is shown. |
| Saving shows "must create a unique slug/id" | Another expert or team already produces that slug. Rename yours. |
| `agency_agents_delegate` returns a `prompt` instead of a `result` | Subagents are not available in this Hermes runtime. The model continues with the persona prompt. |

---

## Acknowledgements

This project could not exist without the people below. Thank you for sharing your work openly.

- **[The Agency — msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents).** Thanks to **Michael Sitarzewski** and every contributor for writing and maintaining the expert personas. They are the heart of this plugin: every expert you load in Hermes is their work. If this is useful to you, please ⭐ star the original repo.
- **[MichengAI/dsh-agency-agents](https://github.com/MichengAI/dsh-agency-agents).** Thanks to the authors of the DeepSeek Harness plugin. Its expert-team design and UX are what this Hermes version is based on.
- **[DiceBear](https://github.com/dicebear/dicebear).** Thanks to **Florian Körner** and the DiceBear contributors for this open-source avatar library and its free HTTP API.
- **[Lorelei illustration collection](https://www.figma.com/community/file/1198749693280469639)** by **[Lisa Wischofsky](https://www.instagram.com/lischi_art/)**. Thanks for releasing these character illustrations under CC0. Every expert's face comes from this collection.
- **[Hermes Agent](https://hermes-agent.nousresearch.com)** by Nous Research, for a plugin system open enough to make this possible.

---

## Credits and licenses

- **This repository's code** (desktop UI, build and check scripts): [MIT](LICENSE) © Egggy1998.
- **Expert personas:** [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents), MIT © Michael Sitarzewski / AgentLand Contributors. See `plugins/agency-agents-router/AGENCY-AGENTS-LICENSE`.
- **DeepSeek Harness plugin:** [MichengAI/dsh-agency-agents](https://github.com/MichengAI/dsh-agency-agents), Apache-2.0. See `DSH-LICENSE` and `DSH-NOTICE`.
- **Avatars:** [DiceBear](https://github.com/dicebear/dicebear) (MIT), *Lorelei* style, a remix of [Lorelei](https://www.figma.com/community/file/1198749693280469639) by Lisa Wischofsky, released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

This is an independent community port. It is not affiliated with or endorsed by Nous Research, DeepSeek, MichengAI or the Agency Agents authors.
