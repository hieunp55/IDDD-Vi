# Hướng dẫn sử dụng `translate_md.py`

Script dịch file Markdown Anh → Việt, giữ nguyên format (heading, bảng, code
block, ảnh), giữ thuật ngữ tiếng Anh kèm chú thích, có giải thích ẩn dụ, tự
kiểm tra chống thiếu/lệch nội dung. Chỉ dùng Python 3 có sẵn (stdlib), không
cần cài thư viện gì thêm.

## Yêu cầu

- Python 3.8 trở lên (kiểm tra: `python3 --version`).
- Một trong các thứ sau, tuỳ cách bạn chọn ở dưới:
  - Đã cài [Ollama](https://ollama.com) (cách 1 — free tuyệt đối), **hoặc**
  - Một API key free của Google AI Studio (cách 2), **hoặc**
  - Không cần gì cả, chỉ cần trình duyệt (cách 3).

---

## Chọn 1 trong 3 cách

| Cách | Chi phí | Cần cài gì | Tốc độ | Phù hợp khi |
|---|---|---|---|---|
| 1. Ollama (local) | Free tuyệt đối | Ollama + GPU/CPU đủ khoẻ | Nhanh, không giới hạn | Có máy chạy được model 7B–14B |
| 2. Gemini free tier | Free (có rate limit) | Không cần cài gì, chỉ cần key | Trung bình (có delay tránh 429) | Có internet, không có GPU mạnh |
| 3. Web thủ công | Free | Không cần cài gì | Chậm nhất (làm tay từng chunk) | Không muốn cài/đăng ký gì cả |

---

## Cách 1 — Chạy local bằng Ollama (khuyến nghị nếu máy đủ khoẻ)

```bash
# Cài Ollama (1 lần): xem hướng dẫn tại ollama.com
ollama pull qwen2.5:14b      # hoặc qwen2.5:7b nếu VRAM ít hơn

python3 translate_md.py auto \
  --input sach.md \
  --output sach.vi.md \
  --provider ollama \
  --model qwen2.5:14b
```

- Không cần `--api-key`.
- Nếu model báo lỗi tràn ngữ cảnh (context) hoặc bị cắt giữa chừng, giảm
  `--chunk-size` (mặc định 6000 ký tự) xuống 3000–4000, hoặc tăng
  `--ollama-num-ctx` (mặc định 8192) nếu máy đủ RAM/VRAM.
- Nếu Ollama chạy ở máy/cổng khác mặc định, thêm
  `--ollama-host http://<ip>:<port>`.
- Model khác đáng cân nhắc: `gemma4:31b` (dense 31B, 256K context, đa ngôn
  ngữ tốt) — nhưng bản gốc FP16 cần khoảng 74GB VRAM, phải quant Q4
  (~18-20GB) mới chạy vừa GPU tiêu dùng loại khá (24GB trở lên); GPU 12GB sẽ
  phải offload CPU, chậm hơn nhiều. `qwen2.5:14b` hoặc `gemma4:26b` (MoE, ít
  active params hơn) nhẹ và nhanh hơn trên máy VRAM thấp.
- Log khi chạy `auto` giờ chỉ hiện dòng có vấn đề (lỗi gọi API, lệch số
  lượng, thất bại) — chunk dịch OK không in ra để đỡ rối màn hình.

## Cách 2 — Dùng free tier của Gemini (Google AI Studio)

1. Lấy API key miễn phí tại [aistudio.google.com](https://aistudio.google.com)
   (không cần thẻ thanh toán cho free tier).
2. Chạy:

```bash
python3 translate_md.py auto \
  --input sach.md \
  --output sach.vi.md \
  --provider gemini \
  --model gemini-2.5-flash \
  --api-key AIzaSy... \
  --sleep-between 4
```

- `--sleep-between 4` (giây) giúp tránh bị chặn lỗi `429` do free tier giới
  hạn số request/phút. Nếu vẫn bị 429 thường xuyên, tăng số này lên (6, 8...).
- Có thể đặt biến môi trường thay vì `--api-key`:
  `export GEMINI_API_KEY=AIzaSy...`
- Cũng dùng được `--provider anthropic` hoặc `--provider openai` theo cách
  tương tự, nhưng 2 dịch vụ này **không có free tier**, sẽ tốn tiền theo API.

### Tuỳ chọn nâng cao: `--web-search` và `--double-check`

Mặc định model dịch chỉ dựa vào kiến thức có sẵn — nếu prompt yêu cầu chèn
link "Nguồn tham khảo" cho phần giải thích ẩn dụ, model **không thực sự tra
cứu**, dễ bịa link. Thêm 2 cờ này để giảm rủi ro đó (chỉ hỗ trợ
`--provider gemini` hoặc `--provider anthropic`):

```bash
python3 translate_md.py auto --input sach.md --output sach.vi.md \
  --provider gemini --model gemini-2.5-flash --api-key AIzaSy... \
  --sleep-between 4 --web-search --double-check
```

- **`--web-search`**: bật tra cứu Google Search thật trong lúc dịch, để
  link nguồn là link model thực sự tìm thấy, không phải đoán. Dùng quota
  riêng, **giới hạn theo ngày** (tách biệt với quota sinh văn bản thường),
  nên chỉ bật khi tài liệu có nhiều ẩn dụ/thuật ngữ cần trích nguồn.
- **`--double-check`**: sau khi dịch xong mỗi phần, gọi thêm 1 lượt API
  đóng vai người phản biện — chấm xem có câu nào dịch sai nghĩa, bịa thông
  tin, hay link nguồn trông đáng ngờ không. Nếu phát hiện vấn đề, gắn thẳng
  comment `<!-- 🔎 PHẢN BIỆN TỰ ĐỘNG ... -->` vào ngay dưới đoạn đó trong
  file kết quả, kèm mô tả cụ thể. **Tốn gấp đôi số lần gọi API và thời gian
  chạy.**

> **Giới hạn thật của 2 cờ này:** đây vẫn là AI tự tra cứu / AI tự đọc lại,
> không phải con người kiểm tra hay công cụ đối chiếu độc lập. Không có
> comment cảnh báo không có nghĩa là bản dịch chắc chắn đúng 100% — chỉ là
> không phát hiện vấn đề rõ ràng ở lượt đọc đó. Tài liệu quan trọng vẫn nên
> tự đọc lại, đặc biệt các đoạn có số liệu, thuật ngữ pháp lý/y tế/tài chính.

## Cách 3 — Không cài gì cả, dịch tay qua web free

Dùng 3 lệnh theo thứ tự: `prep` → (bạn tự dịch tay) → `status` (kiểm tra) →
`merge` (ghép file cuối).

### Bước 1 — Chia file thành các phần nhỏ kèm sẵn prompt

```bash
# Mặc định (chunk 12.000 ký tự/phần):
python3 translate_md.py prep --input sach.md --chunks-dir ./chunks

# Hoặc tự chốt số file tối đa, VD muốn tối đa khoảng 20 file:
python3 translate_md.py prep --input sach.md --chunks-dir ./chunks --target-files 20
```

Lệnh này tạo trong thư mục `./chunks/`:
- `prompt_001.txt`, `prompt_002.txt`, ... — **file DUY NHẤT bạn cần thao tác**,
  mỗi file đã có sẵn đầy đủ hướng dẫn dịch + nội dung cần dịch.
- `manifest.json` — dữ liệu nội bộ (đã nhúng sẵn bản gốc từng phần bên
  trong, không tạo file riêng cho từng phần) — không cần đụng vào.
- `TRANG_THAI.md` — checklist trạng thái (xem mục riêng bên dưới).

Tổng số file trong thư mục = (số chunk) + 2, không hơn — sách chia 20 chunk
thì thư mục có 22 file, trong đó chỉ 20 file `prompt_XXX.txt` là việc của bạn.

> Muốn ít file hơn nữa: tăng `--chunk-size` (hoặc giảm `--target-files`) — đổi
> lại mỗi lần dán/copy sẽ dài hơn. Ngược lại nếu web chat hay bị cắt output
> giữa chừng, giảm `--chunk-size` để mỗi phần ngắn, an toàn hơn.

### Bước 2 — Dịch tay từng phần

Với **mỗi** file `prompt_XXX.txt`:

1. Mở file, copy **toàn bộ** nội dung.
2. Dán vào một chat web free (ChatGPT, Gemini, hoặc Claude bản web bình
   thường — không cần tài khoản trả phí).
3. Copy câu trả lời của chatbot.
4. Lưu thành file `result_XXX.md` **trong cùng thư mục `./chunks/`**, đúng
   số thứ tự (VD: trả lời của `prompt_003.txt` → lưu thành `result_003.md`).

> **Lưu ý:** Nếu câu trả lời của chatbot **không** tự bọc trong
> ` ```markdown ... ``` `, hãy tự thêm dòng ` ```markdown ` vào đầu và
> ` ``` ` vào cuối trước khi lưu — script cần dấu này để tách đúng nội dung,
> nhất là khi phần đó có sẵn code block bên trong.

### Bước 3 — Kiểm tra tiến độ bất cứ lúc nào

```bash
python3 translate_md.py status --chunks-dir ./chunks
```

Lệnh này **không** cần làm xong hết mới chạy được — chạy bao nhiêu lần cũng
được, để biết còn thiếu/lệch gì. Xem chi tiết trong `./chunks/TRANG_THAI.md`.

### Bước 4 — Ghép thành file cuối cùng

Khi `TRANG_THAI.md` hết mục "Chưa dịch" và "Cần xem lại":

```bash
python3 translate_md.py merge --chunks-dir ./chunks --output sach.vi.md
```

`merge` vẫn chạy được ngay cả khi **chưa** làm xong hết — phần nào chưa dịch
sẽ giữ nguyên bản tiếng Anh kèm đánh dấu rõ ràng trong file kết quả, không
bao giờ mất nội dung.

---

## Đọc file `TRANG_THAI.md`

Đây là file checklist tự động cập nhật mỗi khi chạy `status` hoặc `merge`,
mở bằng bất kỳ trình đọc Markdown nào (hoặc trình soạn thảo text thường):

```
# Trạng thái dịch — 5/8 chunk xong hoàn toàn

## ⬜ Chưa dịch (2)
- [ ] `prompt_003.txt`  →  lưu thành `result_003.md`
- [ ] `prompt_007.txt`  →  lưu thành `result_007.md`

## ⚠️ Đã dịch nhưng LỆCH số ảnh/heading/code-block, cần xem lại (1)
- [ ] `result_005.md` — gốc: {'images': 1, ...}  |  dịch hiện tại: {'images': 0, ...}

## ✅ Đã xong, khớp hoàn toàn (5)
- [x] `result_001.md`
...
```

- **⬜ Chưa dịch**: chưa lưu file `result_XXX.md` tương ứng — làm bước 2.
- **⚠️ Lệch**: đã có bản dịch nhưng số ảnh/heading/code-block không khớp bản
  gốc (thường do chatbot bỏ sót ảnh, mất 1 dòng ``` , hoặc gộp/thiếu heading)
  — mở file `result_XXX.md` đó, so với `original_XXX.md`, sửa tay cho khớp.
- **✅ Đã xong**: không cần đụng vào nữa.

---

## Bảng tham số

### `auto` (dịch toàn tự động qua API)

| Tham số | Bắt buộc | Mặc định | Ý nghĩa |
|---|---|---|---|
| `--input` | có | — | File Markdown gốc |
| `--output` | có | — | File Markdown kết quả |
| `--provider` | có | — | `ollama` / `gemini` / `anthropic` / `openai` |
| `--model` | có | — | Tên model, VD: `qwen2.5:14b`, `gemini-2.5-flash` |
| `--api-key` | tuỳ provider | — | Không cần nếu `--provider ollama` |
| `--ollama-host` | không | `http://localhost:11434` | Địa chỉ Ollama server |
| `--ollama-num-ctx` | không | `8192` | Context window cho Ollama |
| `--chunk-size` | không | `6000` | Số ký tự tối đa mỗi phần dịch |
| `--max-retries` | không | `2` | Số lần tự dịch lại nếu lệch số lượng |
| `--sleep-between` | không | `0` | Giây nghỉ giữa các phần (dùng cho free tier) |
| `--web-search` | không | tắt | Bật tra web thật (chỉ gemini/anthropic) |
| `--double-check` | không | tắt | Gọi thêm 1 lượt phản biện chấm lại bản dịch |
| `--abort-after` | không | `3` | Dừng cả job nếu bấy nhiêu chunk liên tiếp cùng lỗi (nghi lỗi hệ thống). `0` = tắt, chạy hết dù lỗi bao nhiêu |

### `prep` (chuẩn bị chunk để dịch tay)

| Tham số | Bắt buộc | Mặc định | Ý nghĩa |
|---|---|---|---|
| `--input` | có | — | File Markdown gốc |
| `--chunks-dir` | có | — | Thư mục lưu các file chunk |
| `--chunk-size` | không | `12000` | Số ký tự tối đa mỗi phần |
| `--target-files` | không | — | Tự ước lượng `--chunk-size` để ra khoảng N file (ưu tiên hơn `--chunk-size` nếu đặt cả hai) |

### `status` (kiểm tra tiến độ)

| Tham số | Bắt buộc | Ý nghĩa |
|---|---|---|
| `--chunks-dir` | có | Thư mục chunk đã tạo bằng `prep` |

### `merge` (ghép file cuối cùng)

| Tham số | Bắt buộc | Ý nghĩa |
|---|---|---|
| `--chunks-dir` | có | Thư mục chunk đã tạo bằng `prep` |
| `--output` | có | File Markdown kết quả cuối cùng |

---

## Xử lý sự cố thường gặp

**Lỗi `429` liên tục khi dùng `--provider gemini`**
→ Free tier bị giới hạn số request/phút. Tăng `--sleep-between` (VD: 8–10
giây), hoặc chuyển sang model `gemini-2.5-flash` (quota rộng hơn `pro`).

**Lỗi `HTTP 500: Internal error encountered` liên tục ngay từ chunk đầu**
→ Đây là lỗi từ phía Google trả về, không phải bug của script. Từ 3 chunk
liên tiếp lỗi trở lên, script tự **dừng sớm** cả job (mặc định, xem
`--abort-after`) thay vì chạy mù hết cả trăm chunk cùng lỗi — phần chưa thử
vẫn được giữ nguyên bản gốc, đánh dấu rõ trong file output, không mất gì.
Cách cô lập nguyên nhân:
  1. Thử lại với `--chunk-size` lớn (VD 50000) để chỉ tạo 1-2 chunk, dễ đọc
     lỗi đầy đủ hơn.
  2. Thử bỏ `--web-search` — một số model (đặc biệt bản Gemma phục vụ qua
     Gemini API) có thể chưa hỗ trợ ổn định tool tra web, gây lỗi 500 thay
     vì lỗi rõ ràng hơn.
  3. Kiểm tra lại `--model` gõ đúng chính tả, còn khả dụng (model có thể bị
     deprecate/đổi tên).
  4. Kiểm tra quota/trạng thái key tại aistudio.google.com.
  5. Nếu vẫn không rõ nguyên nhân, thử đổi sang model khác (VD
     `gemini-2.5-flash`) để xác định lỗi do model cụ thể hay do tài khoản.

**Ollama báo lỗi tràn ngữ cảnh / bị cắt nội dung giữa chừng**
→ Giảm `--chunk-size` xuống 3000–4000, hoặc tăng `--ollama-num-ctx` nếu máy
đủ RAM/VRAM (mỗi lần tăng gấp đôi tốn thêm bộ nhớ đáng kể).

**Kết quả `merge` có đoạn tiếng Anh kèm dòng `<!-- ⚠️ ... -->`**
→ Bình thường — đó là phần chưa dịch hoặc dịch bị lệch số lượng mà script cố
ý giữ lại thay vì xoá mất. Xem `TRANG_THAI.md` để biết chính xác phần nào,
sửa tay rồi chạy lại `merge`.

**`status`/`merge` báo lệch số ảnh/heading dù bạn nhìn bằng mắt thấy bản dịch đủ**
→ Đã từng có bug: nếu chatbot trả lời **không bọc** toàn bộ câu trả lời trong
cặp ` ```markdown ... ``` ` bao ngoài (chỉ trả markdown thô, có sẵn code block
riêng ở giữa như Java/SQL), script cũ hiểu nhầm fence code đó là fence bao
ngoài, cắt mất nội dung trước/sau nó. Đã sửa. Nếu vẫn gặp: mở `result_XXX.md`
đó lên, đảm bảo toàn bộ câu trả lời được bọc trong đúng một cặp
` ```markdown` ở đầu và ` ``` ` ở cuối, không có chữ nào lọt ra ngoài cặp đó.

**Không biết mình còn thiếu chunk nào giữa cả trăm file**
→ Đừng tự đếm — chạy `python3 translate_md.py status --chunks-dir ./chunks`
rồi mở `TRANG_THAI.md`, danh sách hiện đầy đủ tên file cần làm.

**Muốn đổi chatbot dịch giữa chừng (VD: nửa sau dùng Claude thay vì ChatGPT)**
→ Không sao — mỗi `prompt_XXX.txt` độc lập, dán vào chatbot nào cũng được,
kể cả đổi qua lại giữa các chunk.

---

## Câu hỏi thường gặp

**File sách quá dài, có nên chạy 1 lần hết luôn không?**
Được, script tự chia chunk và chạy tuần tự. Với `auto`, cứ để chạy nền (VD:
`nohup python3 translate_md.py auto ... &`); với cách 3, làm dần từng buổi,
`status` bất cứ lúc nào để biết đang tới đâu.

**Chạy `merge` nhiều lần có sao không?**
Không sao — `merge` không sửa các file `original_XXX.md` / `result_XXX.md`,
chỉ đọc và ghi lại file output + `TRANG_THAI.md`. Chạy lại bao nhiêu lần
cũng an toàn.

**Có cách nào tăng chất lượng bản dịch không?**
Model lớn hơn (VD: `qwen2.5:32b` thay vì `7b`, hoặc `gemini-2.5-pro` thay vì
`flash`) thường dịch mượt và bắt ẩn dụ tốt hơn, nhưng chậm hơn / tốn quota
hơn. `--chunk-size` nhỏ hơn cũng giúp model tập trung hơn mỗi lần, nhưng tăng
số lần gọi.
