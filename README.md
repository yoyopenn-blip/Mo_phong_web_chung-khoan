# ⚡ VN Stock Analytics Pro

> Nền tảng phân tích chứng khoán Việt Nam thông minh — real-time data, chỉ báo kỹ thuật chuyên sâu, và giao diện glassmorphism đẹp mắt.

## ✨ Tính năng chính

- **📡 Dual Data Source** — Tích hợp cả `vnstock3` API (TCBS real-time) và CafeF CDN (toàn thị trường)
- **🔄 Auto Fallback** — Tự động chuyển sang nguồn dự phòng khi API lỗi
- **📦 CafeF Auto-Detect** — Tự động quét và tải file ZIP của ngày giao dịch gần nhất (lùi tối đa 10 ngày)
- **📊 Biểu đồ nến Nhật & Line Chart** — Powered by Plotly với hiệu ứng animation
- **📈 Chỉ báo kỹ thuật** — MA, EMA, Bollinger Bands, RSI
- **🔬 Phát hiện Outliers** — Thuật toán IQR và Z-Score
- **🎨 Giao diện Glassmorphism** — Dark mode với gradient động, responsive layout

---

## 🚀 Cài đặt & Chạy

### Yêu cầu hệ thống
- Python 3.9+
- pip

### 1. Clone repository

```bash
git clone https://github.com/<your-username>/vn-stock-analytics.git
cd vn-stock-analytics
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

> **Lưu ý:** `vnstock3` là optional. App vẫn hoạt động với nguồn CafeF nếu không cài.

### 4. Chạy ứng dụng

```bash
streamlit run app.py
```

Mở trình duyệt tại `http://localhost:8501` 🎉

---

## 📁 Cấu trúc dự án

```
vn-stock-analytics/
├── app.py                  # File chính của ứng dụng Streamlit
├── requirements.txt        # Danh sách thư viện
├── .gitignore              # Các file bị loại khỏi git
└── README.md               # File này
```

---

## 🛠️ Hướng dẫn sử dụng

| Bước | Hành động |
|------|-----------|
| 1 | Chọn **nguồn dữ liệu**: `vnstock3 API` hoặc `CafeF Auto` |
| 2 | Chọn **chế độ tải**: 1 mã cụ thể hoặc toàn bộ thị trường |
| 3 | Nhấn nút **Tải dữ liệu** |
| 4 | Nhập **mã chứng khoán** (VD: `VCB`, `VIC`, `FPT`) |
| 5 | Tùy chỉnh **chỉ báo kỹ thuật** ở sidebar và phân tích |

### Khi nào dùng nguồn nào?

| Tình huống | Nguồn đề xuất | Lý do |
|-----------|--------------|-------|
| Phân tích 1 mã cụ thể | 📡 vnstock3 | Nhanh, real-time |
| So sánh nhiều mã | 📦 CafeF | Toàn thị trường |
| Phân tích lịch sử | 📦 CafeF | Dữ liệu điều chỉnh |
| API bị lỗi | 📦 CafeF | Luôn sẵn sàng |

---

## ⚙️ Cấu hình

Không cần file `.env`. App hoạt động out-of-the-box với dữ liệu công khai từ CafeF CDN và TCBS API.

Nếu muốn dùng `vnstock3`, cài thêm:

```bash
pip install vnstock3
```

---

## 📦 Tech Stack

| Thư viện | Mục đích |
|---------|---------|
| [Streamlit](https://streamlit.io/) | Web UI framework |
| [Plotly](https://plotly.com/) | Biểu đồ tương tác |
| [Pandas](https://pandas.pydata.org/) | Xử lý dữ liệu |
| [NumPy](https://numpy.org/) | Tính toán số học |
| [Requests](https://requests.readthedocs.io/) | HTTP requests |
| [vnstock3](https://github.com/thinh-vu/vnstock) | Dữ liệu chứng khoán VN |
