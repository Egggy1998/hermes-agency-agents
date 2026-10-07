# Hermes Agency Agents

[English](README.md) · **Tiếng Việt**

Bộ hai plugin cho [Hermes Agent](https://hermes-agent.nousresearch.com), đưa bộ chuyên gia **Agency Agents** vào Hermes: **321 expert thuộc 22 lĩnh vực (division), 5 team dựng sẵn, và mỗi expert có một avatar được đóng gói kèm**.

Đây là bản chuyển từ plugin Agency Agents của DeepSeek Harness ([`@michengai/dsh-agency-agents`](https://github.com/MichengAI/dsh-agency-agents) v1.0.8). Nội dung persona lấy từ [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents).

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
| Expert | 321 |
| Division | 22 |
| Team dựng sẵn | 5 (sửa được, và tạo thêm được) |
| Avatar | 321 file SVG DiceBear *Lorelei*, đóng gói sẵn, dùng được khi offline |
| Tool backend | `agency_agents_search`, `agency_agents_inspect`, `agency_agents_load`, `agency_agents_delegate` |
| Giao diện desktop | Trang Agency, nút chọn trong chatbar, form tạo/sửa expert và team |

---

## Mục lục

1. [Repo này có gì](#repo-này-có-gì)
2. [Cách hoạt động](#cách-hoạt-động)
3. [Cài đặt](#cài-đặt)
4. [Sử dụng](#sử-dụng)
5. [Tạo và sửa expert, team](#tạo-và-sửa-expert-team)
6. [Danh sách tool backend](#danh-sách-tool-backend)
7. [Danh sách expert và team](#danh-sách-expert-và-team)
8. [Avatar](#avatar)
9. [Build lại từ nguồn](#build-lại-từ-nguồn)
10. [Kiểm tra](#kiểm-tra)
11. [Cấu trúc repo](#cấu-trúc-repo)
12. [Xử lý sự cố](#xử-lý-sự-cố)
13. [Ghi công và giấy phép](#ghi-công-và-giấy-phép)

---

## Repo này có gì

Repo gồm hai plugin chạy cùng nhau.

### 1. Plugin backend: `agency-agents-router`

Plugin Hermes viết bằng Python, đăng ký bốn tool. Toàn bộ danh sách expert nằm trên đĩa (`data/agents.json`), và **persona chỉ được nạp khi cần đến**. Hermes không phải nhồi 321 skill vào mọi prompt. Model tìm trong danh sách, chọn một expert rồi nạp đúng persona đó.

### 2. Plugin desktop: `agency-agents`

Plugin cho Hermes Desktop (ESM thuần, không cần build), thêm các phần sau:

- **Trang Agency Agents** ở sidebar, cũng mở được từ command palette bằng lệnh *Open Agency Agents*:
  - tab **Experts** có ô tìm kiếm, bộ lọc theo division, và một thẻ cho mỗi expert (avatar, tên, division, mô tả);
  - tab **Teams** liệt kê các team, avatar thành viên xếp chồng và tên thành viên.
- **Nút Agency trong ô chat.** Bấm vào sẽ mở popup có hai tab **Experts** và **Teams**, chọn ngay mà không phải rời khung chat.
- **Form chỉnh sửa** để tạo expert mới, sửa expert có sẵn, và tạo hoặc sửa team.

Chọn expert hay team không tự gửi tin nhắn. Plugin chỉ chèn một câu chỉ dẫn vào **đầu bản nháp đang soạn**, để anh/chị xem lại, gõ nốt yêu cầu rồi tự bấm gửi.

---

## Cách hoạt động

```
┌──────────────────── Hermes Desktop ────────────────────┐
│  Trang Agency / nút chọn trong chatbar                 │
│        │  chọn expert hoặc team                        │
│        ▼                                               │
│  chỉ dẫn được chèn vào đầu bản nháp                    │
└────────┬───────────────────────────────────────────────┘
         │ người dùng gửi tin nhắn
         ▼
┌──────────────────── Hermes Agent ──────────────────────┐
│  model gọi agency_agents_load / _delegate              │
│        │                                               │
│        ▼                                               │
│  agency-agents-router đọc data/agents.json             │
│  → trả về MỘT persona (hoặc chạy một subagent)         │
└────────────────────────────────────────────────────────┘
```

**Expert có sẵn.** Plugin chèn một chỉ dẫn ngắn:

```text
Use agency_agents_load with slug "chief-executive-officer", then answer as Chief Executive Officer (CEO): <yêu cầu của bạn>
```

Model gọi `agency_agents_load`, nhận prompt đầy đủ của expert và trả lời trong vai đó.

**Team.** Plugin chèn chỉ dẫn điều phối, nêu tên từng thành viên và mục tiêu của team. Model gọi `agency_agents_delegate` cho các thành viên song song rồi tổng hợp kết quả:

```text
Use agency-agents-router for this task. Coordinate these experts in parallel: Software Architect, Application Security Engineer, Reality Checker. Synthesize under this goal: Review architecture, security risks, and acceptance boundaries. Task: <yêu cầu của bạn>
```

**Expert tự tạo, hoặc expert có sẵn đã bị ghi đè prompt.** Backend không biết các expert này, nên plugin chèn thẳng prompt vào chỉ dẫn:

```text
Act as <tên>. Follow this specialist prompt:
<prompt của bạn>

Task: <yêu cầu của bạn>
```

Nếu team có expert tự tạo, prompt của các expert đó cũng được nối vào chỉ dẫn của team theo cách tương tự.

---

## Cài đặt

`HERMES_HOME` là thư mục dữ liệu của Hermes. Mặc định là `~/.hermes`; trên Windows là thư mục cài Hermes, ví dụ `D:\Hermes`.

### Cách A: copy plugin đã build sẵn (khuyên dùng)

```bash
git clone https://github.com/Egggy1998/hermes-agency-agents.git
cd hermes-agency-agents

cp -r plugins/agency-agents-router   "$HERMES_HOME/plugins/"
cp -r desktop-plugins/agency-agents  "$HERMES_HOME/desktop-plugins/"

hermes plugins enable agency-agents-router
```

Sau đó:

1. **Khởi động lại Hermes** để đăng ký các tool backend.
2. Plugin desktop **tự nạp lại (hot-load)** sau vài giây. Nếu chưa thấy, tải lại cửa sổ bằng Ctrl+R / Cmd+R.
3. Mục *Agency Agents* sẽ xuất hiện ở sidebar, và nút Agency sẽ xuất hiện trong ô chat.

### Cách B: build và cài thẳng vào Hermes

```bash
python scripts/build.py "$HERMES_HOME"
hermes plugins enable agency-agents-router
```

Yêu cầu của cách này xem ở mục [Build lại từ nguồn](#build-lại-từ-nguồn).

### Kiểm tra sau khi cài

```bash
hermes plugins list --plain --no-bundled        # agency-agents-router phải ở trạng thái enabled
hermes chat -Q -q "Call agency_agents_search with query 'chief executive strategy' and limit 1. Reply with only the returned slug."
# → chief-executive-officer
```

---

## Sử dụng

### Từ ô chat

1. Bấm nút **Agency** ở bên trái ô nhập chat.
2. Chọn tab **Experts** hoặc **Teams**.
3. Gõ để tìm. Expert được tìm theo tên, mô tả và division; team được tìm theo tên, mô tả và slug thành viên. Mỗi lần hiện tối đa 50 expert.
4. Bấm vào một kết quả. Chỉ dẫn được chèn vào đầu bản nháp, phần anh/chị đã gõ trước đó vẫn giữ nguyên.
5. Viết yêu cầu tiếp phía sau rồi gửi.

Nếu chưa có ô chat nào đang được chọn, plugin sẽ nhắc bấm vào ô chat rồi chọn lại.

### Từ trang Agency

1. Mở **Agency Agents** từ sidebar hoặc command palette.
2. Ở tab **Experts**, tìm và lọc theo division, rồi bấm **Use expert** trên thẻ.
3. Ở tab **Teams**, bấm **Use team** trên thẻ.
4. Chỉ dẫn được đặt vào ô chat của cuộc hội thoại đang mở.

---

## Tạo và sửa expert, team

Dùng các nút ở phần đầu trang Agency và nút **Edit** trên từng thẻ.

### Tạo expert mới

| Trường | Bắt buộc | Ghi chú |
|---|---|---|
| Name | có | Dùng để sinh slug (`Growth Hacker VN` → `growth-hacker-vn`). Slug không được trùng. |
| Division | có | Nhập tự do. Division mới sẽ xuất hiện trong bộ lọc. |
| Description | không | Hiển thị trên thẻ và dùng khi tìm kiếm. |
| System prompt | có | Toàn bộ persona của expert. Prompt được gửi kèm trong chỉ dẫn, vì backend không biết expert tự tạo. |

### Sửa expert có sẵn

- **Expert có sẵn:** sửa được tên, division và mô tả. Trường **ghi đè system prompt** không bắt buộc: để trống thì giữ persona gốc từ backend, điền vào thì dùng prompt mới thay cho persona gốc.
- **Expert tự tạo:** sửa được mọi trường. Slug giữ nguyên sau khi tạo.

### Tạo team / sửa team

| Trường | Bắt buộc | Ghi chú |
|---|---|---|
| Name | có | Dùng để sinh id của team; không được trùng. |
| Description | không | |
| Goal | không (nên điền) | Được đưa vào chỉ dẫn của team làm mục tiêu tổng hợp. |
| Members | có | Chọn nhiều expert, cả có sẵn lẫn tự tạo (giữ Ctrl/Cmd khi bấm). Avatar các thành viên đã chọn hiện ngay bên dưới. |

Năm team dựng sẵn cũng sửa được. Thay đổi được lưu thành bản ghi đè, nên định nghĩa gốc của các team này không bị động tới.

### Dữ liệu chỉnh sửa được lưu ở đâu

Expert tự tạo, team tự tạo và các bản ghi đè nằm trong storage riêng của plugin desktop, với key `hermes.plugin.agency-agents.catalog-v1`:

```json
{
  "experts":         [ { "slug", "name", "division", "description", "prompt", "emoji" } ],
  "expertOverrides": { "<slug có sẵn>": { "...các trường đã sửa" } },
  "teams":           [ { "id", "name", "description", "goal", "members": ["slug", "..."] } ],
  "teamOverrides":   { "<id team dựng sẵn>": { "...các trường đã sửa" } }
}
```

- Dữ liệu được **kiểm tra khi nạp**. Bản ghi sai định dạng bị bỏ qua, không làm hỏng giao diện.
- Cài lại hay build lại plugin **không ảnh hưởng** dữ liệu này, vì nó được lưu tách khỏi danh sách expert sinh ra khi build.
- Hermes lưu dữ liệu này theo từng profile và từng máy, nên không đồng bộ giữa các máy.

---

## Danh sách tool backend

Cả bốn tool thuộc toolset `agency_agents`. Tool nào nhận expert thì chấp nhận `slug` hoặc `agent`, giá trị có thể là slug hoặc đúng tên hiển thị.

| Tool | Tham số | Chức năng |
|---|---|---|
| `agency_agents_search` | `query` (bắt buộc), `division`, `limit` (mặc định 8, tối đa 25) | Tìm và xếp hạng expert. Trả về slug, tên, division và mô tả. |
| `agency_agents_inspect` | `slug` / `agent` | Trả về thông tin và đường dẫn nguồn của một expert, không kèm prompt đầy đủ. |
| `agency_agents_load` | `slug` / `agent`, `task` | Trả về prompt đầy đủ của expert, kèm task nếu có truyền vào. Model sau đó nhập vai expert này. |
| `agency_agents_delegate` | `slug` / `agent`, `task` (bắt buộc) | Chạy expert như một **subagent** riêng của Hermes và trả về kết quả, chờ tối đa 330 giây. Nếu không dùng được subagent hoặc subagent lỗi, tool trả về prompt của persona để model tự làm tiếp. |

---

## Danh sách expert và team

### Division (22)

| Division | Số expert | Division | Số expert |
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

### Team dựng sẵn (5)

| Team | Thành viên | Mục tiêu |
|---|---|---|
| Product Review Team | product-manager, design-ux-researcher, engineering-software-architect | Đánh giá giá trị, khả năng sử dụng và tính khả thi của một đề xuất sản phẩm. |
| Technical Review Team | engineering-software-architect, security-appsec-engineer, testing-reality-checker | Rà soát kiến trúc, rủi ro bảo mật và tiêu chí nghiệm thu. |
| Content Planning Team | marketing-content-creator, marketing-growth-hacker, research-synthesist | Lên chủ đề, định vị và dàn ý nội dung dựa trên dữ liệu có căn cứ. |
| Data Analysis Team | engineering-data-engineer, support-analytics-reporter, engineering-data-visualization-engineer | Phân tích dữ liệu đáng tin cậy, nêu rõ giả định và gợi ý biểu đồ. |
| Research Team | research-synthesist, product-trend-researcher, specialized-strategy-duel-agent | Tách bạch sự thật đã kiểm chứng, suy luận, điểm bất đồng và đánh đổi khi ra quyết định. |

Danh sách đầy đủ các expert nằm trong [`plugins/agency-agents-router/data/agents.json`](plugins/agency-agents-router/data/agents.json). Toàn bộ avatar xem tại [thư viện avatar](avatars/README.md).

---

## Avatar

- Mỗi expert có một avatar **DiceBear [Lorelei](https://www.dicebear.com/styles/lorelei/)**, sinh từ slug của expert. Vì vậy cùng một expert luôn có cùng một khuôn mặt.
- Bảng màu nền: `b6e3f4, c0aede, d1d4f9`.
- Cả 321 file SVG nằm trong [`avatars/`](avatars/) và được **nhúng thẳng vào `plugin.js`**. Hermes Desktop nạp plugin từ một địa chỉ `blob:`, nên plugin không đọc được file nằm cạnh nó. Nhúng SVG vào là cách để avatar hiện được cả khi offline.
- **Expert tự tạo** lấy avatar từ `https://api.dicebear.com/10.x/lorelei/svg?seed=<slug>`.
- Nếu avatar không tải được, **emoji** của expert sẽ hiện thay.
- Team hiển thị **avatar thành viên xếp chồng**: tối đa 6 avatar, phần còn lại gộp thành ô `+N`. Rê chuột vào avatar để xem tên expert.

---

## Build lại từ nguồn

Chỉ cần build lại khi muốn sinh lại danh sách expert từ nguồn persona mới hơn.

```bash
python scripts/build.py                  # sinh lại vào repo này
python scripts/build.py "$HERMES_HOME"   # sinh lại và cài thẳng vào Hermes
```

| Nguồn vào | Mặc định | Đổi bằng |
|---|---|---|
| Package DSH Agency Agents (file Markdown của persona) | `~/.dsh/profiles/desktop/node_modules/@michengai/dsh-agency-agents` | biến môi trường `DSH_AGENCY_PACKAGE` |
| Khung backend (từ `msitarzewski/agency-agents` → `integrations/hermes`) | thư mục `plugins/agency-agents-router` của repo này | biến môi trường `AGENCY_HERMES_SKELETON` |

`build.py` làm các bước sau:

1. Đọc front matter của từng file Markdown persona (`name`, `description`, `emoji`, `color`, `vibe`) và kiểm tra không có hai persona trùng slug.
2. Ghi backend: `__init__.py`, `plugin.yaml`, `data/agents.json`, `data/teams.json` và các file giấy phép.
3. Tải những avatar chưa có trong `avatars/` (8 request song song, mỗi file đều được kiểm tra đúng là SVG) rồi tạo lại thư viện avatar.
4. Sinh `desktop-plugins/agency-agents/plugin.js` gồm danh sách expert, các team và avatar đã nhúng.

Trước khi thay thư mục backend đang có, `build.py` kiểm tra `plugin.yaml` trong đó có đúng là của `agency-agents-router` không, để không xoá nhầm thư mục khác.

Yêu cầu: Python 3.10 trở lên, chỉ dùng thư viện chuẩn. Cần thêm Node.js nếu muốn chạy các bài kiểm tra JS.

---

## Kiểm tra

```bash
python scripts/check.py
# check ok: 321 experts, 5 teams, 321 bundled avatars, 4 tools

node desktop-plugins/agency-agents/check-catalog.mjs
# catalog check: ok

node --check desktop-plugins/agency-agents/plugin.js
```

- `check.py` kiểm tra số lượng expert, slug không trùng, mọi thành viên team đều tồn tại, mỗi file avatar là SVG hợp lệ **và** đã được nhúng vào `plugin.js`, và backend đăng ký đủ bốn tool.
- `check-catalog.mjs` kiểm tra phần expert/team tự tạo: sinh slug, loại bỏ dữ liệu storage sai định dạng, lưu dữ liệu, ghép bản ghi đè, và nội dung chỉ dẫn cho expert lẫn team (kể cả prompt kèm theo của expert tự tạo).

---

## Cấu trúc repo

```
hermes-agency-agents/
├── plugins/agency-agents-router/     # Plugin backend Hermes (Python)
│   ├── __init__.py                   #   đăng ký 4 tool
│   ├── plugin.yaml
│   ├── data/agents.json              #   321 expert kèm nội dung persona đầy đủ
│   ├── data/teams.json               #   5 team dựng sẵn
│   └── AGENCY-AGENTS-LICENSE, DSH-LICENSE, DSH-NOTICE
├── desktop-plugins/agency-agents/    # Plugin Hermes Desktop (ESM)
│   ├── plugin.js                     #   giao diện + danh sách expert + avatar nhúng (~2 MB)
│   └── check-catalog.mjs             #   kiểm tra phần expert/team tự tạo
├── avatars/                          # 321 file SVG Lorelei + README thư viện avatar
├── scripts/
│   ├── build.py                      # script sinh plugin
│   └── check.py                      # kiểm tra toàn repo
├── README.md / README.vi.md
└── LICENSE
```

---

## Xử lý sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| Không thấy nút Agency hoặc mục ở sidebar | Tải lại cửa sổ bằng Ctrl+R. Tìm dòng `Plugin "agency-agents" failed to load` trong `HERMES_HOME/logs/desktop.log`. |
| Model báo không có tool `agency_agents_*` | Chạy `hermes plugins enable agency-agents-router`, rồi khởi động lại Hermes. |
| Hiện thông báo "Focus a chat composer, then choose again." | Bấm vào ô nhập chat, rồi chọn lại expert hoặc team. |
| Expert tự tạo không có avatar | Máy đang offline (avatar của expert tự tạo lấy từ DiceBear API). Lúc này emoji sẽ hiện thay. |
| Khi lưu báo "must create a unique slug/id" | Đã có expert hoặc team khác sinh ra cùng slug. Đổi tên khác. |
| `agency_agents_delegate` trả về `prompt` thay vì `result` | Bản Hermes đang dùng không chạy được subagent. Model sẽ làm tiếp với prompt của persona. |

---

## Ghi công và giấy phép

- **Code của repo này** (giao diện desktop, script build và kiểm tra): [MIT](LICENSE) © Egggy1998.
- **Persona các expert:** [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents), MIT © Michael Sitarzewski / AgentLand Contributors. Xem `plugins/agency-agents-router/AGENCY-AGENTS-LICENSE`.
- **Plugin DeepSeek Harness:** [MichengAI/dsh-agency-agents](https://github.com/MichengAI/dsh-agency-agents), Apache-2.0. Xem `DSH-LICENSE` và `DSH-NOTICE`.
- **Avatar:** [DiceBear](https://github.com/dicebear/dicebear) (MIT), style *Lorelei*, phối lại từ tác phẩm [Lorelei](https://www.figma.com/community/file/1198749693280469639) của Lisa Wischofsky, phát hành theo [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

Đây là bản chuyển đổi độc lập của cộng đồng, không liên kết với và không được bảo trợ bởi Nous Research, DeepSeek, MichengAI hay các tác giả Agency Agents.
