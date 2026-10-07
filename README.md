# Hermes Agency Agents

Plugin [Hermes](https://hermes-agent.nousresearch.com) chuyển từ Agency Agents của DeepSeek Harness (`@michengai/dsh-agency-agents` v1.0.8).

- **321 expert**, 22 division, 5 team preset
- **321 avatar** DiceBear Lorelei được bundle sẵn, chạy offline. Xem [`avatars/`](avatars/README.md)
- Backend gồm 4 tool: `agency_agents_search`, `agency_agents_inspect`, `agency_agents_load`, `agency_agents_delegate`
- Desktop có trang Agency Agents: duyệt, lọc, **tạo và sửa expert**, **tạo và sửa team**
- Picker trong chatbar có 2 tab Experts / Teams, chèn chỉ dẫn vào draft đang soạn

## Cài đặt

```bash
cp -r plugins/agency-agents-router         <HERMES_HOME>/plugins/
cp -r desktop-plugins/agency-agents        <HERMES_HOME>/desktop-plugins/
hermes plugins enable agency-agents-router
```

Sau khi copy, khởi động lại Hermes để nạp backend. Desktop plugin tự hot-load.

Expert và team tự tạo được lưu trong storage của desktop plugin (`hermes.plugin.agency-agents.catalog-v1`). Build lại plugin không làm mất dữ liệu này.

## Build lại

```bash
python scripts/build.py              # ghi vào repo này
python scripts/build.py D:/Hermes    # cài thẳng vào Hermes home
python scripts/check.py              # kiểm tra 321 expert, team member, avatar bundle, 4 tool
node desktop-plugins/agency-agents/check-catalog.mjs   # kiểm tra logic expert/team tự tạo
```

`build.py` đọc persona từ package DSH đã cài. Avatar còn thiếu được tải về `avatars/` một lần rồi nhúng vào `plugin.js`, vì plugin chạy từ blob URL nên không đọc được file nằm cạnh. Expert tự tạo vẫn lấy avatar từ DiceBear API.

## License

- Code trong repo: MIT, xem [LICENSE](LICENSE)
- Persona expert: MIT, © Michael Sitarzewski / AgentLand Contributors, xem `plugins/agency-agents-router/AGENCY-AGENTS-LICENSE`
- Phần chuyển từ `dsh-agency-agents`: Apache-2.0, xem `DSH-LICENSE` và `DSH-NOTICE`
- Avatar: [DiceBear](https://github.com/dicebear/dicebear) style Lorelei, remix từ tác phẩm của Lisa Wischofsky, phát hành theo CC0 1.0
