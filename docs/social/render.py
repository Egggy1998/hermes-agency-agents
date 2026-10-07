"""Render Facebook promo images (1080x1350) from real repo data: python docs/social/render.py"""
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
agents = json.loads((REPO / "plugins/agency-agents-router/data/agents.json").read_text(encoding="utf-8"))
teams = json.loads((REPO / "plugins/agency-agents-router/data/teams.json").read_text(encoding="utf-8"))
by = {a["slug"]: a for a in agents}
av = lambda slug: (REPO / "avatars" / f"{slug}.svg").as_uri()
divisions = sorted({a["division"] for a in agents})

CSS = """
*{box-sizing:border-box;margin:0}
body{width:1080px;height:1350px;overflow:hidden;font-family:'Segoe UI',system-ui,sans-serif;color:#eceef4;
background:radial-gradient(1200px 700px at 85% -10%,#3b2f6b 0%,transparent 60%),radial-gradient(900px 600px at -10% 110%,#173a4f 0%,transparent 60%),#0d0e14}
.pad{padding:72px 72px}
.kicker{font-size:26px;letter-spacing:.14em;text-transform:uppercase;color:#a99cff;font-weight:600}
h1{font-size:84px;line-height:1.02;font-weight:800;letter-spacing:-.02em;margin-top:18px}
h2{font-size:60px;line-height:1.05;font-weight:800;letter-spacing:-.015em;margin-top:14px}
.sub{font-size:30px;line-height:1.4;color:#b8bccb;margin-top:22px}
.grad{background:linear-gradient(90deg,#b6e3f4,#c0aede 55%,#d1d4f9);-webkit-background-clip:text;color:transparent}
.av{border-radius:50%;background:#1d2030;display:block}
.foot{position:absolute;left:72px;right:72px;bottom:56px;display:flex;justify-content:space-between;align-items:center;font-size:26px;color:#9aa0b4}
.foot b{color:#eceef4;font-weight:600}
.pill{display:inline-block;border:1px solid #34384c;border-radius:999px;padding:10px 20px;font-size:24px;color:#cfd3e2;margin:0 10px 12px 0;background:#151826}
.card{background:#141724;border:1px solid #262a3d;border-radius:28px;padding:28px 30px}
.stack{display:flex}.stack img{width:64px;height:64px;border-radius:50%;box-shadow:0 0 0 4px #141724;background:#1d2030}
.stack img+img{margin-left:-14px}
"""
FOOT = '<div class="foot"><span>github.com/<b>Egggy1998/hermes-agency-agents</b></span><span>MIT · open source</span></div>'


def page(name: str, body: str) -> None:
    html = OUT / f"{name}.html"
    html.write_text(f"<!doctype html><meta charset=utf-8><style>{CSS}</style><body>{body}</body>", encoding="utf-8")
    png = OUT / f"{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--allow-file-access-from-files", f"--screenshot={png}", "--window-size=1080,1350",
                    "--virtual-time-budget=4000", html.as_uri()], check=True, capture_output=True)
    html.unlink()
    print(png, png.stat().st_size)


# 1. Cover: avatar mosaic
mosaic = "".join(f'<img class="av" src="{av(a["slug"])}" style="width:88px;height:88px">' for a in agents[::4][:70])
page("01-cover", f"""<div class="pad">
<div class="kicker">Hermes Agent plugin · open source</div>
<h1><span class="grad">321 chuyên gia AI</span><br>ngay trong ô chat</h1>
<div class="sub">Agency Agents chuyển từ DeepSeek Harness sang Hermes: {len(divisions)} lĩnh vực, team chuyên gia, avatar riêng cho từng người.</div>
<div style="display:grid;grid-template-columns:repeat(10,88px);gap:6px;margin-top:48px;-webkit-mask-image:linear-gradient(#000 70%,transparent)">{mosaic}</div>
</div>{FOOT}""")

# 2. Picker (UI reproduction)
picks = ["chief-executive-officer", "engineering-software-architect", "design-ui-designer", "marketing-growth-hacker", "security-appsec-engineer", "product-manager"]
rows = "".join(f'''<div style="display:flex;gap:18px;align-items:center;padding:14px 16px;border-radius:16px;{'background:#202437' if i == 1 else ''}">
<img class="av" src="{av(s)}" style="width:56px;height:56px;border-radius:14px"><div><div style="font-size:27px;font-weight:600">{by[s]["name"]}</div>
<div style="font-size:21px;color:#8e94a8;text-transform:capitalize">{by[s]["division"].replace("-", " ")}</div></div></div>''' for i, s in enumerate(picks))
page("02-chatbar", f"""<div class="pad">
<div class="kicker">Chọn ngay trong chatbar</div>
<h2>Bấm nút Agency, gõ tên,<br>chọn expert hoặc cả team</h2>
<div class="card" style="margin-top:44px;width:640px;padding:22px">
 <div style="display:flex;border:1px solid #30344a;border-radius:14px;padding:4px;font-size:22px">
  <div style="flex:1;text-align:center;padding:10px;border-radius:10px;background:#262a3f">Experts 321</div>
  <div style="flex:1;text-align:center;padding:10px;color:#8e94a8">Teams 5</div></div>
 <div style="margin-top:14px;border:1px solid #30344a;border-radius:14px;padding:14px 18px;font-size:24px;color:#6f7590">🔍 Search experts</div>
 <div style="margin-top:10px">{rows}</div>
</div>
<div class="card" style="margin-top:22px;font-size:24px;color:#cfd3e2;line-height:1.45;font-family:Consolas,monospace">
<span style="color:#a99cff">Use agency_agents_load</span> with slug "engineering-software-architect", then answer as Software Architect: <span style="color:#6f7590">review kiến trúc giúp mình…</span></div>
</div>{FOOT}""")

# 3. Teams
cards = "".join(f'''<div class="card" style="margin-top:20px;display:flex;gap:26px;align-items:center">
<div class="stack">{"".join(f'<img src="{av(m)}">' for m in t["members"])}</div>
<div><div style="font-size:30px;font-weight:700">{t["name"]}</div>
<div style="font-size:22px;color:#9aa0b4;margin-top:6px">{" · ".join(by[m]["name"] for m in t["members"])}</div></div></div>''' for t in teams)
page("03-teams", f"""<div class="pad">
<div class="kicker">Expert teams</div>
<h2>Gọi cả team review song song,<br>rồi tổng hợp một kết luận</h2>
<div class="sub" style="font-size:26px">5 team dựng sẵn. Tự tạo team riêng, thêm expert, sửa prompt ngay trong Hermes.</div>
<div style="margin-top:26px">{cards}</div>
</div>{FOOT}""")

# 4. Divisions + credits
pills = "".join(f'<span class="pill">{d.replace("-", " ")} <b style="color:#a99cff">{sum(a["division"] == d for a in agents)}</b></span>' for d in divisions)
page("04-credits", f"""<div class="pad">
<div class="kicker">{len(divisions)} lĩnh vực · {len(agents)} experts</div>
<div style="margin-top:28px">{pills}</div>
<h2 style="margin-top:46px;font-size:46px;white-space:nowrap">Cảm ơn những người làm nên dự án 🙏</h2>
<div class="card" style="margin-top:28px;font-size:26px;line-height:1.55;color:#cfd3e2">
<b style="color:#eceef4">The Agency</b> · Michael Sitarzewski &amp; contributors<br><span style="color:#8e94a8">github.com/msitarzewski/agency-agents · toàn bộ persona chuyên gia</span><br><br>
<b style="color:#eceef4">DiceBear</b> · Florian Körner &amp; contributors<br><span style="color:#8e94a8">github.com/dicebear/dicebear · thư viện avatar mã nguồn mở</span><br><br>
<b style="color:#eceef4">Lorelei</b> · Lisa Wischofsky<br><span style="color:#8e94a8">bộ minh hoạ nhân vật CC0</span><br><br>
<b style="color:#eceef4">dsh-agency-agents</b> · MichengAI<br><span style="color:#8e94a8">thiết kế expert team gốc trên DeepSeek Harness</span></div>
</div>{FOOT}""")
