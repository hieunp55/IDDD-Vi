#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
translate_md.py — Tự động / bán tự động dịch file Markdown Anh -> Việt.

3 CHẾ ĐỘ (subcommand):

  auto   Dịch toàn tự động qua API. Hỗ trợ:
           - ollama    : model chạy LOCAL trên máy bạn (Qwen2.5, SeaLLM...) — FREE TUYỆT ĐỐI,
                         không cần API key, không giới hạn, không lo lộ dữ liệu ra ngoài.
                         Yêu cầu: đã cài Ollama (ollama.com) và đã `ollama pull <model>`.
           - gemini    : Google AI Studio có FREE TIER thật (không cần thẻ), lấy key tại
                         aistudio.google.com. Có rate limit, dùng --sleep-between để tránh 429.
           - anthropic / openai : trả phí theo API, chỉ dùng nếu có budget.

  prep   KHÔNG cần cài gì, KHÔNG cần API key. Chia file gốc thành nhiều chunk, mỗi chunk xuất
         ra 1 file .txt đã có sẵn full prompt — bạn chỉ việc MỞ FILE, COPY, DÁN vào web chat
         free (ChatGPT / Gemini / Claude bản web bình thường), rồi COPY câu trả lời, LƯU lại
         đúng tên file result_XXX.md mà script báo.

  status Quét thư mục chunk, đối chiếu với bản gốc, tự sinh file checklist TRANG_THAI.md —
         biết ngay còn thiếu gì / lệch gì mà không cần tự rà soát cả tài liệu bằng tay.

  merge  Sau khi đã lưu đủ các file result_XXX.md, chạy lệnh này để TỰ ĐỘNG ghép lại thành
         1 file .md hoàn chỉnh + tự động kiểm tra số ảnh/heading/code-block mỗi chunk, cảnh
         báo cho bạn biết chunk nào dịch thiếu/lệch để xem lại.

VÍ DỤ:
  # Cách 1 — free tuyệt đối, chạy local (khuyến nghị nếu máy có GPU ổn):
  ollama pull qwen2.5:14b
  python3 translate_md.py auto --input sach.md --output sach.vi.md \
      --provider ollama --model qwen2.5:14b

  # Cách 2 — free tier Gemini (cần internet + key miễn phí):
  python3 translate_md.py auto --input sach.md --output sach.vi.md \
      --provider gemini --model gemini-2.5-flash --api-key AI... --sleep-between 4

  # Cách 3 — không cài gì cả, dùng web free thủ công (ChatGPT/Gemini/Claude web):
  python3 translate_md.py prep --input sach.md --chunks-dir ./chunks
  #   ... bạn tự paste từng file prompt_XXX.txt vào web chat, lưu reply thành result_XXX.md ...
  python3 translate_md.py status --chunks-dir ./chunks   # xem còn thiếu gì
  python3 translate_md.py merge --chunks-dir ./chunks --output sach.vi.md

Chỉ dùng Python 3 stdlib, không cần pip install gì.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

# ----------------------------------------------------------------------------
# PROMPT TEMPLATE
# ----------------------------------------------------------------------------

PROMPT_TEMPLATE = """Bạn là chuyên gia dịch thuật kỹ thuật Anh → Việt, chuyên tài liệu kỹ thuật/công nghệ, có kinh nghiệm dịch như biên dịch viên bản ngữ chuyên nghiệp. Nhiệm vụ: dịch TOÀN BỘ nội dung Markdown dưới đây sang tiếng Việt, không bỏ sót bất kỳ phần nào. Đây là MỘT PHẦN (chunk) của một tài liệu lớn hơn, hãy dịch độc lập đoạn này, không thêm lời mở đầu/kết luận về việc đây chỉ là một phần.

QUY TẮC BẮT BUỘC — VI PHẠM LÀ SAI:

1. XÁC ĐỊNH LOẠI TÀI LIỆU TRƯỚC KHI DỊCH
   - Tự phân tích nội dung để xác định loại tài liệu (kỹ thuật/lập trình, tài chính, bảo hiểm, pháp lý, marketing, học thuật, vận hành, sản phẩm...).
   - Chọn văn phong và thuật ngữ CHUẨN NGÀNH tương ứng trong tiếng Việt, nhất quán xuyên suốt.

2. VĂN PHONG — MƯỢT NHƯ NGƯỜI DỊCH, KHÔNG GIẢM CHÍNH XÁC
   - Dịch mượt, tự nhiên, đúng ngữ pháp tiếng Việt — như biên dịch viên bản ngữ dịch tay, KHÔNG dịch máy móc kiểu word-by-word.
   - Được phép đảo cấu trúc câu, tách/gộp câu cho tự nhiên, miễn giữ nguyên 100% ý nghĩa, thông tin, logic, số liệu gốc.
   - Khi "mượt mà" và "chính xác" xung đột → LUÔN ưu tiên chính xác.

3. DỊCH ĐẦY ĐỦ 100%
   - Không tóm tắt, không rút gọn, không lược bỏ đoạn/câu/mục/bullet nào.
   - Số lượng heading, đoạn văn, bảng, code block ở output PHẢI khớp 1:1 với input.
   - Đoạn dài dịch hết, không cắt ngắn.

4. GIỮ NGUYÊN THUẬT NGỮ TIẾNG ANH
   - Thuật ngữ chuyên ngành (tên công nghệ, framework, pattern, tên hàm/biến, acronym...) giữ nguyên tiếng Anh, không dịch, không phiên âm.
   - Ngay sau lần xuất hiện ĐẦU TIÊN của mỗi thuật ngữ, thêm chú thích ngắn trong ngoặc giải thích nghĩa bằng tiếng Việt.
   - Các lần xuất hiện sau KHÔNG cần chú thích lại.

5. GIỮ NGUYÊN FORMAT — RẤT QUAN TRỌNG
   - VỀ ẢNH (làm trước khi dịch): ĐẾM chính xác số lượng thẻ ảnh dạng ![...](...) trong đoạn gốc bên dưới. Output PHẢI có ĐÚNG số lượng thẻ ảnh đó, không được thiếu một cái nào — kể cả ảnh không có caption, không rõ ngữ cảnh, hay trông như ảnh trang trí/lặp lại. Copy nguyên URL 100%, không sửa, không rút gọn, không thay bằng mô tả text.
   - Giữ cấp độ heading (#, ##, ###...), giữ đúng số lượng heading.
   - Giữ cấu trúc bảng (số cột, số hàng, alignment, header row).
   - Giữ code block (```lang ... ```) — KHÔNG dịch code; comment được dịch tại chỗ; **được phép reformat code, tự động xuống dòng/indent chuẩn, không giữ nguyên code 1 dòng; không đổi logic/cú pháp**.
   - Giữ blockquote, callout/note/warning (>, [!NOTE], [!WARNING]...).
   - Giữ list, nested list, checkbox (- [ ]).
   - Giữ nguyên link thường ([text](url)) — chỉ dịch phần text hiển thị, TUYỆT ĐỐI giữ nguyên URL.
   - TRƯỚC KHI TRẢ KẾT QUẢ: tự đếm lại số heading, số ảnh, số dòng ``` giữa bản gốc và bản dịch của bạn, nếu lệch phải sửa lại cho khớp.

6. GIẢI THÍCH ẨN DỤ / KHÁI NIỆM KHÓ
   - Với ẩn dụ, thành ngữ, khái niệm trừu tượng khó hiểu với người Việt, thêm khối giải thích riêng ngay sau đoạn đó:
     > 💡 **Giải thích thêm:** [giải thích dễ hiểu, đủ chuyên sâu, có ví dụ thực tế]
     > Nguồn tham khảo: [link cụ thể để kiểm chứng]
   - CHỈ đưa link nếu chắc chắn tồn tại và đúng nội dung — không bịa link.
   - Không tìm được nguồn tin cậy → ghi rõ: "(Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)".

7. CHỐNG HALLUCINATION (BẮT BUỘC)
   - Không tự thêm thông tin/số liệu/ví dụ/kết luận KHÔNG có trong bản gốc — trừ phần giải thích ẩn dụ ở mục 6 (phải gắn nhãn rõ là phần bổ sung).
   - Câu gốc mơ hồ → dịch sát nghĩa nhất, nếu không chắc ghi chú: "[CẦN KIỂM CHỨNG: câu gốc mơ hồ]".
   - Không tự sửa/thêm/bớt logic kỹ thuật gốc. Không bịa trích dẫn/số liệu/link vô căn cứ.
   - Không tự tóm tắt các đoạn dài thành ý chính rồi diễn giải lại — phải dịch từng câu.

8. OUTPUT
   - Trả về DUY NHẤT nội dung Markdown đã dịch, đặt trong 1 code block (```markdown ... ```).
   - Không thêm lời dẫn/lời chào/giải thích ngoài code block.
   - Không đổi tiêu đề gốc trừ khi cần dịch tiêu đề.

--- NỘI DUNG GỐC CẦN DỊCH (một phần của tài liệu) ---

%%%CHUNK_CONTENT%%%
"""

REVIEW_PROMPT_TEMPLATE = """Bạn là một biên tập viên phản biện (critic), nhiệm vụ DUY NHẤT là soi lỗi bản dịch dưới đây, KHÔNG phải dịch lại hay khen ngợi. Đừng khách sáo, cứ thẳng vào vấn đề.

BẢN GỐC (tiếng Anh):
---
%%%ORIGINAL%%%
---

BẢN DỊCH (tiếng Việt) CẦN PHẢN BIỆN:
---
%%%TRANSLATED%%%
---

Kiểm tra và chỉ ra CỤ THỂ (trích câu/cụm từ, không nói chung chung):

1. SAI NGHĨA: câu nào dịch lệch nghĩa, dịch ngược nghĩa, hoặc bỏ sót ý quan trọng so với bản gốc?
2. BỊA ĐẶT: có thông tin/số liệu/ví dụ nào xuất hiện trong bản dịch nhưng KHÔNG có trong bản gốc không (trừ phần giải thích ẩn dụ được đánh dấu rõ là bổ sung)?
3. NGUỒN THAM KHẢO: mỗi link "Nguồn tham khảo" trong bản dịch — link đó có vẻ là một URL thật, hợp lý (đúng domain, đúng định dạng) hay có dấu hiệu bịa (không tồn tại, chung chung, không khớp chủ đề)? Nếu nghi ngờ, nói rõ nên đổi thành "cần tự kiểm chứng".
4. THUẬT NGỮ: thuật ngữ tiếng Anh giữ nguyên có được chú thích đúng nghĩa không, có chỗ nào chú thích sai không?

ĐỊNH DẠNG TRẢ LỜI — CHỈ MỘT TRONG HAI DẠNG SAU, KHÔNG THÊM GÌ KHÁC:

- Nếu không phát hiện vấn đề gì đáng kể: trả lời đúng 1 dòng "ĐẠT — không phát hiện lỗi đáng kể."
- Nếu có vấn đề: liệt kê gạch đầu dòng, mỗi dòng 1 vấn đề, ngắn gọn, trích dẫn cụ thể phần bị lỗi.

Không thêm lời mở đầu, không thêm kết luận ngoài 2 dạng trên.
"""

# ----------------------------------------------------------------------------
# Verify helpers
# ----------------------------------------------------------------------------

IMG_RE = re.compile(r'!\[[^\]]*\]\([^)]*\)')
HEADING_RE = re.compile(r'(?m)^#{1,6}\s')
FENCE_RE = re.compile(r'(?m)^```')


def count_markers(text):
    return {
        'images': len(IMG_RE.findall(text)),
        'headings': len(HEADING_RE.findall(text)),
        'fences': len(FENCE_RE.findall(text)),
    }


def extract_markdown(response_text):
    """
    Tách nội dung markdown ra khỏi câu trả lời của chatbot.

    QUAN TRỌNG: chunk có thể chứa sẵn code block (```python...```) BÊN TRONG.
    Nếu dùng regex non-greedy tìm ``` đầu tiên -> ``` gần nhất, nó sẽ dừng nhầm
    ở fence code NỘI BỘ thay vì fence bao NGOÀI. Vì vậy: lấy vị trí fence MỞ ĐẦU
    đầu tiên, rồi lấy vị trí fence ĐÓNG cuối cùng trong toàn bộ text (rfind) —
    đảm bảo luôn bao trọn vẹn mọi fence lồng bên trong.
    """
    text = response_text.strip()
    first_fence = re.search(r'```[a-zA-Z]*[ \t]*\n', text)
    if first_fence:
        start = first_fence.end()
        last_close = text.rfind('```')
        if last_close > start:
            return text[start:last_close].rstrip('\n')
    return text


# ----------------------------------------------------------------------------
# Chunking
# ----------------------------------------------------------------------------

def split_into_blocks(text):
    lines = text.split('\n')
    blocks = []
    current = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_fence = not in_fence
            current.append(line)
            continue
        if stripped == '' and not in_fence:
            if current:
                blocks.append('\n'.join(current))
                current = []
            continue
        current.append(line)
    if current:
        blocks.append('\n'.join(current))
    return blocks


def pack_blocks(blocks, max_chars):
    chunks = []
    current = []
    current_len = 0
    for b in blocks:
        b_len = len(b) + 2
        if current and current_len + b_len > max_chars:
            chunks.append('\n\n'.join(current))
            current = [b]
            current_len = b_len
        else:
            current.append(b)
            current_len += b_len
    if current:
        chunks.append('\n\n'.join(current))
    return chunks


def make_chunks(source_text, chunk_size):
    blocks = split_into_blocks(source_text)
    return pack_blocks(blocks, chunk_size)


# ----------------------------------------------------------------------------
# API callers (pure stdlib)
# ----------------------------------------------------------------------------

def _post_json(url, headers, payload, provider, timeout=300, retries=3):
    data = json.dumps(payload).encode('utf-8')
    last_err = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode('utf-8'))
            return _extract_text(body, provider)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            last_err = f"HTTP {e.code}: {err_body[:500]}"
            if e.code == 429 or e.code >= 500:
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError(last_err)
        except Exception as e:
            last_err = str(e)
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"[{provider}] request thất bại sau {retries} lần: {last_err}")


def _extract_text(body, provider):
    if provider == 'anthropic':
        parts = body.get('content', [])
        return ''.join(p.get('text', '') for p in parts if p.get('type') == 'text')
    if provider == 'openai':
        choices = body.get('choices', [])
        if not choices:
            raise RuntimeError(f"OpenAI response không có 'choices': {body}")
        return choices[0]['message']['content']
    if provider == 'gemini':
        candidates = body.get('candidates', [])
        if not candidates:
            raise RuntimeError(f"Gemini response không có 'candidates': {body}")
        parts = candidates[0].get('content', {}).get('parts', [])
        return ''.join(p.get('text', '') for p in parts)
    if provider == 'ollama':
        if 'error' in body:
            raise RuntimeError(f"Ollama lỗi: {body['error']}")
        return body.get('response', '')
    raise ValueError(f"Provider không hỗ trợ: {provider}")


def call_anthropic(prompt, model, api_key, max_tokens=8192, web_search=False, **kwargs):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "content-type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if web_search:
        # Cho phep Claude thuc su tra cuu web khi can xac minh nguon tham khao
        # (thay vi chi doan tu du lieu huan luyen). Ton them token/thoi gian.
        payload["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
    return _post_json(url, headers, payload, provider="anthropic")


def call_openai(prompt, model, api_key, max_tokens=8192, web_search=False, **kwargs):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "max_completion_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    # LUU Y: endpoint /v1/chat/completions KHONG ho tro tool web search that
    # (chi co o Responses API rieng). web_search=True bi bo qua o day, script
    # se in canh bao truoc khi chay — xem cmd_auto.
    return _post_json(url, headers, payload, provider="openai")


def call_gemini(prompt, model, api_key, max_tokens=8192, web_search=False, **kwargs):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"content-type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    if web_search:
        # Bat Grounding with Google Search that su — model tu quyet dinh khi
        # nao can tra cuu de tra loi chinh xac hon, tra ve link nguon that
        # thay vi tu doan/bia. Free tier co quota rieng, gioi han theo ngay.
        payload["tools"] = [{"google_search": {}}]
    return _post_json(url, headers, payload, provider="gemini")


def call_ollama(prompt, model, api_key=None, max_tokens=8192, host="http://localhost:11434",
                num_ctx=8192, **kwargs):
    url = f"{host.rstrip('/')}/api/generate"
    headers = {"content-type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens, "num_ctx": num_ctx},
    }
    # Local inference có thể chậm, timeout dài hơn mặc định
    return _post_json(url, headers, payload, provider="ollama", timeout=900, retries=2)


CALL_FUNCS = {
    'anthropic': call_anthropic,
    'openai': call_openai,
    'gemini': call_gemini,
    'ollama': call_ollama,
}

ENV_KEYS = {
    'anthropic': 'ANTHROPIC_API_KEY',
    'openai': 'OPENAI_API_KEY',
    'gemini': 'GEMINI_API_KEY',
    'ollama': None,  # không cần key
}


# ----------------------------------------------------------------------------
# Dịch 1 chunk qua API, verify, tự retry (dùng cho chế độ "auto")
# ----------------------------------------------------------------------------

def translate_chunk_api(chunk_text, idx, total, provider, model, api_key, max_retries,
                         provider_kwargs=None):
    provider_kwargs = provider_kwargs or {}
    src_counts = count_markers(chunk_text)
    prompt = PROMPT_TEMPLATE.replace("%%%CHUNK_CONTENT%%%", chunk_text)

    for attempt in range(1, max_retries + 2):
        try:
            raw = CALL_FUNCS[provider](prompt, model, api_key, **provider_kwargs)
        except Exception as e:
            print(f"  [{idx}/{total}] LỖI GỌI API (lần {attempt}): {e}", file=sys.stderr)
            time.sleep(5)
            continue

        translated = extract_markdown(raw)
        out_counts = count_markers(translated)

        if out_counts == src_counts:
            return translated, True

        print(f"  [{idx}/{total}] LỆCH SỐ LƯỢNG: gốc={src_counts} dịch={out_counts} -> thử lại...",
              file=sys.stderr)
        prompt = prompt + (
            f"\n\nCẢNH BÁO: Lần trước bạn dịch bị LỆCH số lượng so với bản gốc "
            f"(cần đúng {src_counts['images']} ảnh, {src_counts['headings']} heading, "
            f"{src_counts['fences']} dòng ```, nhưng bản dịch chỉ có "
            f"{out_counts['images']} ảnh, {out_counts['headings']} heading, "
            f"{out_counts['fences']} dòng ```). "
            f"LẦN NÀY PHẢI ĐẾM LẠI THẬT KỸ và đảm bảo khớp chính xác trước khi trả lời."
        )
        time.sleep(2)

    fallback = (
        f"<!-- ⚠️ TỰ ĐỘNG DỊCH THẤT BẠI SAU {max_retries + 1} LẦN THỬ "
        f"(lệch số ảnh/heading/code-block so với bản gốc). "
        f"GIỮ NGUYÊN BẢN GỐC (TIẾNG ANH) Ở DƯỚI, CẦN DỊCH TAY ĐOẠN NÀY. -->\n\n"
        + chunk_text
    )
    print(f"  [{idx}/{total}] THẤT BẠI sau {max_retries + 1} lần, giữ bản gốc + đánh dấu.",
          file=sys.stderr)
    return fallback, False


def review_translation(original_text, translated_text, provider, model, api_key, provider_kwargs=None):
    """
    Goi API mot lan NUA, dong vai nguoi phan bien, cham lai ban dich vua tao.
    Day la kiem tra NGHIA (semantic), khac voi verify dem anh/heading/code-block
    (chi kiem tra CAU TRUC). Van chi la mot AI tu doc lai — KHONG phai bang
    chung tuyet doi, van nen tu doc lai nhung cho no danh dau la co van de.
    """
    provider_kwargs = provider_kwargs or {}
    prompt = (
        REVIEW_PROMPT_TEMPLATE
        .replace("%%%ORIGINAL%%%", original_text)
        .replace("%%%TRANSLATED%%%", translated_text)
    )
    try:
        raw = CALL_FUNCS[provider](prompt, model, api_key, **provider_kwargs)
        return raw.strip()
    except Exception as e:
        return f"(Không chạy được bước phản biện: {e})"


def cmd_auto(args):
    api_key = args.api_key
    if args.provider != 'ollama' and not api_key:
        api_key = os.environ.get(ENV_KEYS[args.provider])
    if args.provider != 'ollama' and not api_key:
        print(f"LỖI: thiếu API key. Truyền --api-key hoặc đặt biến môi trường "
              f"{ENV_KEYS[args.provider]}.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"LỖI: không tìm thấy file input: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.web_search and args.provider not in ('gemini', 'anthropic'):
        print(f"CẢNH BÁO: --web-search chỉ hỗ trợ provider gemini/anthropic, "
              f"bỏ qua cho provider={args.provider} (chạy bình thường, không tra web).",
              file=sys.stderr)

    with open(args.input, 'r', encoding='utf-8') as f:
        source = f.read()

    chunks = make_chunks(source, args.chunk_size)
    total = len(chunks)
    print(f"Đã chia thành {total} chunk (~{args.chunk_size} ký tự/chunk). "
          f"Bắt đầu dịch bằng {args.provider}/{args.model}"
          + (" (có tra web)" if args.web_search and args.provider in ('gemini', 'anthropic') else "")
          + (" (có phản biện 2 lượt)" if args.double_check else "")
          + "...\n", file=sys.stderr)

    provider_kwargs = {}
    if args.provider == 'ollama':
        provider_kwargs = {"host": args.ollama_host, "num_ctx": args.ollama_num_ctx}
    if args.web_search and args.provider in ('gemini', 'anthropic'):
        provider_kwargs["web_search"] = True

    translated_chunks = []
    failed_indices = []
    flagged_indices = []
    for i, chunk in enumerate(chunks, 1):
        translated, ok = translate_chunk_api(
            chunk, i, total, args.provider, args.model, api_key, args.max_retries,
            provider_kwargs=provider_kwargs,
        )
        if ok and args.double_check:
            review = review_translation(chunk, translated, args.provider, args.model,
                                         api_key, provider_kwargs=provider_kwargs)
            if not review.strip().upper().startswith("ĐẠT"):
                flagged_indices.append(i)
                translated = translated + (
                    f"\n\n<!-- 🔎 PHẢN BIỆN TỰ ĐỘNG cho chunk {i} (chỉ là AI tự đọc lại, "
                    f"không phải bằng chứng tuyệt đối — nên tự xem lại):\n{review}\n-->"
                )
                print(f"  [{i}/{total}] PHẢN BIỆN phát hiện vấn đề, đã đánh dấu trong output.",
                      file=sys.stderr)
        translated_chunks.append(translated)
        if not ok:
            failed_indices.append(i)
        if args.sleep_between > 0 and i < total:
            time.sleep(args.sleep_between)

    final_text = '\n\n'.join(translated_chunks) + '\n'
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(final_text)

    print(f"\nXONG. Đã ghi file: {args.output}", file=sys.stderr)
    if failed_indices:
        print(f"CẢNH BÁO: {len(failed_indices)}/{total} chunk KHÔNG qua được verify tự động.\n"
              f"Các chunk này vẫn còn nguyên bản tiếng Anh trong file output, đánh dấu bằng\n"
              f"comment '<!-- ⚠️ TỰ ĐỘNG DỊCH THẤT BẠI ... -->'. Số chunk lỗi: {failed_indices}",
              file=sys.stderr)
    else:
        print("Tất cả chunk đều qua verify (khớp số ảnh/heading/code-block với bản gốc).",
              file=sys.stderr)
    if args.double_check:
        if flagged_indices:
            print(f"PHẢN BIỆN: {len(flagged_indices)}/{total} chunk bị AI phản biện gắn cờ nghi vấn "
                  f"(comment '<!-- 🔎 PHẢN BIỆN TỰ ĐỘNG ... -->' trong file). Số chunk: {flagged_indices}",
                  file=sys.stderr)
        else:
            print("PHẢN BIỆN: không chunk nào bị gắn cờ (nhưng đây vẫn chỉ là AI tự đọc lại, "
                  "không thay thế việc bạn tự xem qua bản dịch).", file=sys.stderr)




# ----------------------------------------------------------------------------
# Chế độ "prep" + "status" + "merge" — dịch tay qua web free, không cần cài/trả gì
# ----------------------------------------------------------------------------

def load_manifest_or_die(chunks_dir):
    manifest_path = os.path.join(chunks_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        print(f"LỖI: không tìm thấy manifest.json trong {chunks_dir}. "
              f"Bạn đã chạy lệnh 'prep' trước chưa?", file=sys.stderr)
        sys.exit(1)
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def scan_results(chunks_dir, manifest):
    """
    Quét toàn bộ thư mục chunk, đối chiếu với manifest.
    Trả về 1 danh sách dict, mỗi phần tử là 1 chunk với:
      status: 'ok' | 'mismatch' | 'missing'
      content: nội dung dùng để ghép vào file cuối (đã xử lý fallback)
      src_counts / out_counts, các tên file liên quan.
    Đây là NƠI DUY NHẤT làm việc đối chiếu này — status và merge đều gọi hàm này
    để đảm bảo 2 lệnh luôn báo cáo khớp nhau.

    LƯU Ý: bản gốc từng chunk được đọc từ manifest["chunks"][i]["original_text"]
    (nhúng thẳng trong manifest.json), KHÔNG có file original_XXX.md riêng —
    giảm một nửa số file trong thư mục chunk, người dùng không cần đụng tới.
    """
    results = []
    for entry in manifest["chunks"]:
        idx = entry["index"]
        result_path = os.path.join(chunks_dir, entry["result_file"])
        original_text = entry["original_text"]

        if not os.path.exists(result_path):
            results.append({
                "index": idx, "status": "missing",
                "prompt_file": entry["prompt_file"], "result_file": entry["result_file"],
                "src_counts": entry["counts"], "out_counts": None,
                "content": (
                    f"<!-- ⚠️ CHƯA CÓ BẢN DỊCH cho chunk {idx} "
                    f"(không tìm thấy {entry['result_file']}). "
                    f"GIỮ NGUYÊN BẢN GỐC (TIẾNG ANH) Ở DƯỚI. -->\n\n" + original_text
                ),
            })
            continue

        with open(result_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        translated = extract_markdown(raw)
        out_counts = count_markers(translated)
        src_counts = entry["counts"]

        if out_counts == src_counts:
            results.append({
                "index": idx, "status": "ok",
                "prompt_file": entry["prompt_file"], "result_file": entry["result_file"],
                "src_counts": src_counts, "out_counts": out_counts,
                "content": translated,
            })
        else:
            results.append({
                "index": idx, "status": "mismatch",
                "prompt_file": entry["prompt_file"], "result_file": entry["result_file"],
                "src_counts": src_counts, "out_counts": out_counts,
                "content": (
                    translated
                    + f"\n\n<!-- ⚠️ CẢNH BÁO chunk {idx}: số ảnh/heading/code-block KHÔNG khớp "
                      f"bản gốc (gốc={src_counts}, dịch={out_counts}). "
                      f"Xem lại đoạn này bằng tay. -->"
                ),
            })

    return results


def write_status_report(chunks_dir, results):
    """
    Ghi 1 file checklist riêng (TRANG_THAI.md) để người dùng KHÔNG PHẢI tự rà soát
    cả cuốn sách — chỉ cần mở file này là thấy ngay còn thiếu gì, lệch gì.
    Ghi đè mỗi lần gọi 'status' hoặc 'merge' để luôn phản ánh đúng hiện trạng.
    """
    total = len(results)
    missing = [r for r in results if r["status"] == "missing"]
    mismatched = [r for r in results if r["status"] == "mismatch"]
    ok = [r for r in results if r["status"] == "ok"]

    lines = []
    lines.append(f"# Trạng thái dịch — {len(ok)}/{total} chunk xong hoàn toàn\n")

    if missing:
        lines.append(f"## ⬜ Chưa dịch ({len(missing)})\n")
        lines.append("Mở file prompt tương ứng, dán vào chat, lưu kết quả thành đúng tên result:\n")
        for r in missing:
            lines.append(f"- [ ] `{r['prompt_file']}`  →  lưu thành `{r['result_file']}`")
        lines.append("")

    if mismatched:
        lines.append(f"## ⚠️ Đã dịch nhưng LỆCH số ảnh/heading/code-block, cần xem lại ({len(mismatched)})\n")
        for r in mismatched:
            lines.append(
                f"- [ ] `{r['result_file']}` — gốc: {r['src_counts']}  |  dịch hiện tại: {r['out_counts']}"
            )
        lines.append("")

    if ok:
        lines.append(f"## ✅ Đã xong, khớp hoàn toàn ({len(ok)})\n")
        lines.append("_(không liệt kê chi tiết — các file này không cần bạn động vào nữa)_\n")

    if not missing and not mismatched:
        lines.append("**Tất cả chunk đã xong và khớp — có thể chạy `merge` để xuất file cuối cùng.**\n")
    else:
        lines.append(
            f"**Còn {len(missing) + len(mismatched)}/{total} chunk cần làm tiếp.** "
            f"Chạy lại `status` bất cứ lúc nào để cập nhật danh sách này."
        )

    report_path = os.path.join(chunks_dir, "TRANG_THAI.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    return report_path, ok, mismatched, missing


def cmd_prep(args):
    if not os.path.exists(args.input):
        print(f"LỖI: không tìm thấy file input: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, 'r', encoding='utf-8') as f:
        source = f.read()

    chunk_size = args.chunk_size
    if args.target_files:
        # Uoc luong chunk-size de ra khoang target_files file — khong chinh xac
        # tuyet doi (con tuy cach noi dung chia block tu nhien) nhung du gan.
        estimate = max(1500, len(source) // args.target_files)
        chunk_size = estimate
        print(f"--target-files {args.target_files} -> tự ước lượng chunk-size ≈ {chunk_size} ký tự.",
              file=sys.stderr)

    chunks = make_chunks(source, chunk_size)
    total = len(chunks)
    digits = max(3, len(str(total)))

    os.makedirs(args.chunks_dir, exist_ok=True)

    manifest = {"total": total, "chunks": []}
    for i, chunk in enumerate(chunks, 1):
        idx_str = str(i).zfill(digits)
        prompt_file = f"prompt_{idx_str}.txt"
        result_file = f"result_{idx_str}.md"

        prompt = PROMPT_TEMPLATE.replace("%%%CHUNK_CONTENT%%%", chunk)
        with open(os.path.join(args.chunks_dir, prompt_file), 'w', encoding='utf-8') as f:
            f.write(prompt)

        manifest["chunks"].append({
            "index": i,
            "prompt_file": prompt_file,
            "result_file": result_file,
            "original_text": chunk,
            "counts": count_markers(chunk),
        })

    manifest_path = os.path.join(args.chunks_dir, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    results = scan_results(args.chunks_dir, manifest)
    report_path, ok, mismatched, missing = write_status_report(args.chunks_dir, results)

    print(f"\nĐã tạo {total} file prompt trong thư mục: {args.chunks_dir}\n", file=sys.stderr)
    print(f"(Tổng cộng thư mục có {total} file `prompt_XXX.txt` (việc CỦA BẠN) "
          f"+ 2 file tự động (manifest.json, TRANG_THAI.md) — không có file rác nào khác.)\n",
          file=sys.stderr)
    print("CÁC BƯỚC TIẾP THEO (làm tay, không cần cài gì):", file=sys.stderr)
    print(f"  1. Mở từng file {args.chunks_dir}/prompt_XXX.txt, copy TOÀN BỘ nội dung.",
          file=sys.stderr)
    print("  2. Dán vào chat web free (ChatGPT / Gemini / Claude bản web bình thường).",
          file=sys.stderr)
    print(f"  3. Copy câu trả lời, lưu thành file result_XXX.md đúng tên (xem checklist).",
          file=sys.stderr)
    print(f"  4. Bất cứ lúc nào muốn biết còn thiếu gì, chạy:\n"
          f"       python3 translate_md.py status --chunks-dir {args.chunks_dir}\n"
          f"     Hoặc mở thẳng file này lên để xem checklist (tự cập nhật mỗi lần chạy status/merge):\n"
          f"       {report_path}", file=sys.stderr)
    print(f"  5. Khi checklist hết mục 'Chưa dịch' và 'Cần xem lại', chạy:\n"
          f"       python3 translate_md.py merge --chunks-dir {args.chunks_dir} "
          f"--output <file_dich_ra>.md", file=sys.stderr)


def cmd_status(args):
    manifest = load_manifest_or_die(args.chunks_dir)
    results = scan_results(args.chunks_dir, manifest)
    report_path, ok, mismatched, missing = write_status_report(args.chunks_dir, results)

    total = len(results)
    print(f"Đã cập nhật checklist: {report_path}\n", file=sys.stderr)
    print(f"  OK hoàn toàn      : {len(ok)}/{total}", file=sys.stderr)
    print(f"  Lệch, cần xem lại : {len(mismatched)}/{total}"
          + (f"  -> chunk {[r['index'] for r in mismatched]}" if mismatched else ""),
          file=sys.stderr)
    print(f"  Chưa dịch         : {len(missing)}/{total}"
          + (f"  -> chunk {[r['index'] for r in missing]}" if missing else ""),
          file=sys.stderr)
    if not missing and not mismatched:
        print("\nXong hết rồi — chạy 'merge' để xuất file cuối cùng.", file=sys.stderr)
    else:
        print(f"\nMở file {report_path} để xem danh sách cụ thể (có tên file rõ ràng).",
              file=sys.stderr)


def cmd_merge(args):
    manifest = load_manifest_or_die(args.chunks_dir)
    results = scan_results(args.chunks_dir, manifest)
    report_path, ok, mismatched, missing = write_status_report(args.chunks_dir, results)

    final_text = '\n\n'.join(r["content"] for r in results) + '\n'
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(final_text)

    total = len(results)
    print(f"Đã ghép xong: {args.output}", file=sys.stderr)
    print(f"  - OK (khớp hoàn toàn): {len(ok)}/{total}", file=sys.stderr)
    if missing:
        print(f"  - CHƯA DỊCH (thiếu file result): {[r['index'] for r in missing]}", file=sys.stderr)
    if mismatched:
        print(f"  - LỆCH SỐ LƯỢNG (vẫn giữ bản dịch, nhưng nên xem lại): "
              f"{[r['index'] for r in mismatched]}", file=sys.stderr)
    if not missing and not mismatched:
        print("  Tất cả chunk đều khớp — không cần xem lại gì thêm.", file=sys.stderr)
    else:
        print(f"  Chi tiết đầy đủ (tên file cụ thể) xem trong: {report_path}", file=sys.stderr)


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Dịch file Markdown Anh -> Việt (tự động qua API/Ollama, hoặc bán tự động qua web free)")
    sub = parser.add_subparsers(dest='command', required=True)

    p_auto = sub.add_parser('auto', help='Dịch toàn tự động qua API (ollama local free / gemini free tier / anthropic / openai)')
    p_auto.add_argument('--input', required=True)
    p_auto.add_argument('--output', required=True)
    p_auto.add_argument('--provider', required=True, choices=['anthropic', 'openai', 'gemini', 'ollama'])
    p_auto.add_argument('--model', required=True,
                         help="VD: qwen2.5:14b (ollama) / gemini-2.5-flash / claude-sonnet-5 / gpt-4o")
    p_auto.add_argument('--api-key', default=None, help="Không cần nếu provider=ollama")
    p_auto.add_argument('--ollama-host', default='http://localhost:11434')
    p_auto.add_argument('--ollama-num-ctx', type=int, default=8192,
                         help="Context window cho Ollama, giảm --chunk-size nếu model bị tràn ngữ cảnh")
    p_auto.add_argument('--chunk-size', type=int, default=6000)
    p_auto.add_argument('--max-retries', type=int, default=2)
    p_auto.add_argument('--sleep-between', type=float, default=0.0,
                         help="Số giây nghỉ giữa các chunk — đặt >0 (vd 4-6) khi dùng free tier để tránh 429")
    p_auto.add_argument('--web-search', action='store_true',
                         help="Bật tra cứu web thật khi dịch (chỉ hỗ trợ provider gemini/anthropic) — "
                              "để link 'Nguồn tham khảo' là link thật thay vì AI tự đoán. Tốn thêm "
                              "thời gian, và có quota riêng (giới hạn theo ngày) ngoài quota sinh văn bản.")
    p_auto.add_argument('--double-check', action='store_true',
                         help="Sau khi dịch mỗi chunk, gọi thêm 1 lượt API đóng vai phản biện chấm lại "
                              "bản dịch (sai nghĩa, bịa đặt, link nguồn khả nghi). Gấp đôi số lần gọi API "
                              "và thời gian chạy. Vẫn chỉ là AI tự đọc lại, không phải bằng chứng tuyệt đối.")

    p_prep = sub.add_parser('prep', help='Chia file + tạo sẵn file prompt để dán tay vào web chat free')
    p_prep.add_argument('--input', required=True)
    p_prep.add_argument('--chunks-dir', required=True)
    p_prep.add_argument('--chunk-size', type=int, default=12000,
                         help="Số ký tự tối đa mỗi phần (mặc định 12000 — lớn hơn 'auto' vì web chat "
                              "free thường nhận paste dài được). Bỏ qua nếu dùng --target-files.")
    p_prep.add_argument('--target-files', type=int, default=None,
                         help="Muốn tối đa khoảng bao nhiêu file prompt — script tự ước lượng "
                              "--chunk-size cho vừa (ưu tiên hơn --chunk-size nếu đặt cả hai). VD: --target-files 20")

    p_status = sub.add_parser('status', help='Quét thư mục chunk, tự sinh checklist TRANG_THAI.md — biết ngay còn thiếu/lệch gì mà không cần rà soát tay')
    p_status.add_argument('--chunks-dir', required=True)

    p_merge = sub.add_parser('merge', help='Ghép các kết quả đã dịch tay lại + tự verify + cập nhật checklist')
    p_merge.add_argument('--chunks-dir', required=True)
    p_merge.add_argument('--output', required=True)

    args = parser.parse_args()

    if args.command == 'auto':
        cmd_auto(args)
    elif args.command == 'prep':
        cmd_prep(args)
    elif args.command == 'status':
        cmd_status(args)
    elif args.command == 'merge':
        cmd_merge(args)


if __name__ == '__main__':
    main()
