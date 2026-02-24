# === CÁC THƯ VIỆN CẦN THIẾT ===
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import warnings
import numpy as np
import requests
from io import BytesIO
import zipfile

# Tắt warnings
warnings.filterwarnings('ignore')

# Try import vnstock3
try:
    from vnstock3 import Vnstock
    VNSTOCK_AVAILABLE = True
except ImportError:
    VNSTOCK_AVAILABLE = False
    st.warning("⚠️ vnstock3 chưa cài đặt. Sử dụng nguồn dữ liệu CafeF.")

# === CẤU HÌNH TRANG WEB ===
st.set_page_config(
    page_title="VN Stock Analytics", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CUSTOM CSS ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Space Grotesk', 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(-45deg, #0a0e1f, #1a1532, #2a1f3a, #151b35);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 0;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main-header {
        background: rgba(92, 88, 187, 0.15);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(185, 87, 206, 0.2);
        padding: 2.5rem;
        border-radius: 25px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(89, 148, 206, 0.2), inset 0 1px 1px rgba(255, 255, 255, 0.1);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .main-header h1 {
        color: #ffffff !important;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 10px rgba(92, 88, 187, 0.8);
    }
    
    .main-header p {
        color: #ffffff !important;
        font-size: 1.2rem;
        margin-top: 0.8rem;
        font-weight: 500;
        text-shadow: 0 1px 5px rgba(0, 0, 0, 0.5);
    }
    
    .stMetric {
        background: rgba(58, 78, 147, 0.2);
        backdrop-filter: blur(10px);
        padding: 1.8rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(92, 88, 187, 0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stMetric:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(92, 88, 187, 0.4);
        border-color: rgba(185, 87, 206, 0.6);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(58, 78, 147, 0.95) 0%, rgba(26, 21, 50, 0.98) 100%);
        backdrop-filter: blur(20px);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #5c58bb 0%, #b957ce 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2.5rem;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(92, 88, 187, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(92, 88, 187, 0.6);
    }
    
    .data-table-container {
        background: rgba(58, 78, 147, 0.15);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(92, 88, 187, 0.3);
        border-radius: 25px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    .chart-container {
        background: rgba(58, 78, 147, 0.15);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 25px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(92, 88, 187, 0.3);
        margin: 2rem 0;
    }
    
    .stats-card {
        background: rgba(58, 78, 147, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(92, 88, 187, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .stats-card:hover {
        border-color: rgba(185, 87, 206, 0.5);
        transform: translateY(-3px);
    }
    </style>
    """, unsafe_allow_html=True)

# === HEADER ===
st.markdown("""
    <div class="main-header">
        <h1>⚡ VN STOCK ANALYTICS PRO</h1>
        <p>🚀 Nền tảng phân tích chứng khoán thông minh với vnstock3 API & CafeF</p>
    </div>
    """, unsafe_allow_html=True)

# === PHẦN 1: HÀM TẢI DỮ LIỆU ===

def process_cafef_zip(zip_content, date_info):
    """Xử lý file ZIP từ CafeF với validation tốt hơn"""
    try:
        with zipfile.ZipFile(zip_content) as z:
            # Liệt kê tất cả files
            all_files = z.namelist()
            st.info(f"📦 Tổng số files trong ZIP: {len(all_files)}")
            
            csv_files = [f for f in all_files if f.lower().endswith('.csv')]
            
            if not csv_files:
                st.error(f"⚠️ Không tìm thấy file CSV trong archive")
                st.info(f"📁 Files tìm thấy: {', '.join(all_files[:10])}...")
                return None
            
            st.info(f"📂 Tìm thấy {len(csv_files)} file CSV, đang xử lý...")
            
            all_data = []
            processed_files = 0
            error_files = 0
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, csv_file in enumerate(csv_files):
                try:
                    status_text.text(f"⏳ Đang xử lý file {idx+1}/{len(csv_files)}: {csv_file[:50]}...")
                    progress_bar.progress((idx + 1) / len(csv_files))
                    
                    with z.open(csv_file) as f:
                        # Thử nhiều encoding
                        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
                        df = None
                        
                        for encoding in encodings:
                            try:
                                f.seek(0)
                                df = pd.read_csv(f, encoding=encoding, on_bad_lines='skip')
                                break
                            except (UnicodeDecodeError, pd.errors.ParserError):
                                continue
                        
                        if df is None or df.empty:
                            error_files += 1
                            continue
                        
                        # Debug: Hiển thị columns của file đầu tiên
                        if idx == 0:
                            st.info(f"🔍 Cột trong file mẫu: {', '.join(df.columns.tolist()[:10])}")
                        
                        # Mapping cột - mở rộng hơn
                        column_mapping = {
                            # Tiếng Việt
                            'Mã CK': '<Ticker>', 'Mã': '<Ticker>', 'TICKER': '<Ticker>', 'Ma': '<Ticker>',
                            'Ngày': '<DTYYYYMMDD>', 'Thời gian': '<DTYYYYMMDD>', 'NGAY': '<DTYYYYMMDD>',
                            'ThoiGian': '<DTYYYYMMDD>', 'Thoi gian': '<DTYYYYMMDD>',
                            'Mở cửa': '<Open>', 'Giá mở cửa': '<Open>', 'OPEN': '<Open>', 'GiaMoCua': '<Open>',
                            'Cao nhất': '<High>', 'Giá cao nhất': '<High>', 'HIGH': '<High>', 'GiaCaoNhat': '<High>',
                            'Thấp nhất': '<Low>', 'Giá thấp nhất': '<Low>', 'LOW': '<Low>', 'GiaThapNhat': '<Low>',
                            'Đóng cửa': '<Close>', 'Giá đóng cửa': '<Close>', 'CLOSE': '<Close>', 'GiaDongCua': '<Close>',
                            'Đ.Cửa': '<Close>', 'DC': '<Close>',
                            'KLGD': '<Volume>', 'Khối lượng': '<Volume>', 'KL': '<Volume>', 'VOLUME': '<Volume>',
                            'KhoiLuong': '<Volume>', 'Khoi luong': '<Volume>',
                            # Tiếng Anh
                            'Code': '<Ticker>', 'Symbol': '<Ticker>', 'Ticker': '<Ticker>',
                            'TradingDate': '<DTYYYYMMDD>', 'Date': '<DTYYYYMMDD>', 
                            'Time': '<DTYYYYMMDD>', 'DateTime': '<DTYYYYMMDD>',
                            'Open': '<Open>', 'OpenPrice': '<Open>',
                            'High': '<High>', 'HighPrice': '<High>',
                            'Low': '<Low>', 'LowPrice': '<Low>',
                            'Close': '<Close>', 'ClosePrice': '<Close>',
                            'Volume': '<Volume>', 'TotalVolume': '<Volume>', 'Vol': '<Volume>'
                        }
                        
                        # Đổi tên cột
                        df = df.rename(columns=column_mapping)
                        
                        # Kiểm tra có đủ cột cần thiết không
                        if '<Ticker>' not in df.columns or '<Close>' not in df.columns:
                            error_files += 1
                            continue
                        
                        # Xử lý cột ngày
                        if '<DTYYYYMMDD>' in df.columns:
                            df['<DTYYYYMMDD>'] = pd.to_datetime(df['<DTYYYYMMDD>'], errors='coerce')
                        else:
                            error_files += 1
                            continue
                        
                        # Lọc các cột cần thiết
                        required_cols = ['<Ticker>', '<DTYYYYMMDD>', '<Open>', '<High>', '<Low>', '<Close>', '<Volume>']
                        
                        # Thêm các cột thiếu với giá trị mặc định
                        for col in required_cols:
                            if col not in df.columns:
                                if col == '<Open>':
                                    df[col] = df['<Close>']
                                elif col in ['<High>', '<Low>']:
                                    df[col] = df['<Close>']
                                elif col == '<Volume>':
                                    df[col] = 0
                        
                        df = df[required_cols]
                        
                        # Kiểm tra có dữ liệu hợp lệ không
                        if len(df) > 0:
                            all_data.append(df)
                            processed_files += 1
                        else:
                            error_files += 1
                        
                except Exception as e:
                    error_files += 1
                    if idx < 5:  # Chỉ hiển thị lỗi 5 file đầu
                        st.warning(f"⚠️ Lỗi file {csv_file}: {str(e)[:100]}")
                    continue
            
            progress_bar.empty()
            status_text.empty()
            
            st.info(f"📊 Xử lý: {processed_files} thành công, {error_files} lỗi")
            
            if all_data:
                st.info("🔄 Đang gộp và làm sạch dữ liệu...")
                combined_df = pd.concat(all_data, ignore_index=True)
                
                st.info(f"📦 Tổng bản ghi ban đầu: {len(combined_df):,}")
                
                # Làm sạch dữ liệu
                combined_df = combined_df.dropna(subset=['<DTYYYYMMDD>', '<Close>', '<Ticker>'])
                st.info(f"✓ Sau khi loại NaN: {len(combined_df):,}")
                
                combined_df['<Ticker>'] = combined_df['<Ticker>'].astype(str).str.strip().str.upper()
                combined_df = combined_df[combined_df['<Ticker>'] != '']
                combined_df = combined_df[combined_df['<Ticker>'] != 'NAN']
                st.info(f"✓ Sau khi loại ticker rỗng: {len(combined_df):,}")
                
                combined_df = combined_df[combined_df['<Close>'] > 0]
                st.info(f"✓ Sau khi loại giá <= 0: {len(combined_df):,}")
                
                combined_df = combined_df.sort_values(['<Ticker>', '<DTYYYYMMDD>'])
                combined_df = combined_df.drop_duplicates(subset=['<Ticker>', '<DTYYYYMMDD>'], keep='last')
                st.info(f"✓ Sau khi loại trùng: {len(combined_df):,}")
                
                unique_tickers = len(combined_df['<Ticker>'].unique())
                total_records = len(combined_df)
                
                if total_records > 0:
                    # Debug: Hiển thị mẫu dữ liệu
                    st.success(f"✅ Thành công: {unique_tickers} mã, {total_records:,} bản ghi (ngày {date_info})")
                    
                    # Hiển thị 5 mã đầu tiên
                    sample_tickers = sorted(combined_df['<Ticker>'].unique())[:5]
                    st.info(f"🔍 Mẫu mã: {', '.join(sample_tickers)}")
                    
                    # Hiển thị date range
                    min_date = combined_df['<DTYYYYMMDD>'].min()
                    max_date = combined_df['<DTYYYYMMDD>'].max()
                    st.info(f"📅 Khoảng thời gian: {min_date.strftime('%d/%m/%Y')} - {max_date.strftime('%d/%m/%Y')}")
                    
                    return combined_df
                else:
                    st.error("❌ Không có dữ liệu sau khi làm sạch")
                    return None
            else:
                st.error(f"⚠️ Không có dữ liệu hợp lệ từ {len(csv_files)} files")
                return None
                
    except zipfile.BadZipFile:
        st.error("❌ File tải về không phải định dạng ZIP hợp lệ")
    except Exception as e:
        st.error(f"❌ Lỗi xử lý ZIP: {str(e)}")
        st.exception(e)
    
    return None

def download_latest_cafef_data():
    """Tự động tìm ngày có dữ liệu gần nhất và tải file ZIP từ CafeF"""
    MAX_DAYS_TO_CHECK = 10
    
    st.info("🔍 Đang tìm dữ liệu CafeF mới nhất...")
    
    # Vòng lặp tìm ngày có dữ liệu
    for i in range(1, MAX_DAYS_TO_CHECK + 1):
        check_date = datetime.now() - timedelta(days=i)
        date_str_path = check_date.strftime('%Y%m%d')
        date_str_file = check_date.strftime('%d%m%Y')
        
        url = f"https://cafef1.mediacdn.vn/data/ami_data/{date_str_path}/CafeF.SolieuGD.Upto{date_str_file}.zip"
        
        try:
            st.info(f"🔎 Kiểm tra ngày: {check_date.strftime('%d-%m-%Y')} (lùi {i} ngày)...")
            
            # Kiểm tra file có tồn tại không
            response = requests.head(url, timeout=10)
            
            st.info(f"📡 HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                st.success(f"✅ Tìm thấy dữ liệu ngày: {check_date.strftime('%d-%m-%Y')}")
                
                # Hiển thị thông tin file
                if 'content-length' in response.headers:
                    file_size = int(response.headers['content-length']) / (1024 * 1024)
                    st.info(f"📦 Kích thước file: {file_size:.2f} MB")
                
                # Tải file zip
                st.info("📥 Đang tải dữ liệu...")
                
                download_progress = st.progress(0)
                download_status = st.empty()
                
                with requests.get(url, stream=True, timeout=120) as r:
                    r.raise_for_status()
                    
                    total_size = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    chunks = []
                    
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            chunks.append(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = downloaded / total_size
                                download_progress.progress(progress)
                                download_status.text(f"⏬ Đã tải: {downloaded/(1024*1024):.1f}/{total_size/(1024*1024):.1f} MB")
                    
                    zip_content = BytesIO(b''.join(chunks))
                
                download_progress.empty()
                download_status.empty()
                
                st.success("✅ Tải thành công! Đang xử lý...")
                
                # Xử lý file zip
                result = process_cafef_zip(zip_content, check_date.strftime('%d-%m-%Y'))
                
                if result is not None:
                    st.balloons()
                    return result
                else:
                    st.error("❌ Xử lý file thất bại, thử ngày khác...")
                    continue
                    
        except requests.exceptions.Timeout:
            st.warning(f"⏱️ Timeout khi kiểm tra ngày {check_date.strftime('%d-%m-%Y')}")
            continue
        except requests.exceptions.RequestException as e:
            st.warning(f"🔌 Lỗi kết nối ngày {check_date.strftime('%d-%m-%Y')}: {str(e)[:100]}")
            continue
        except Exception as e:
            st.error(f"❌ Lỗi không xác định: {str(e)}")
            continue
    
    st.error(f"❌ Không tìm thấy dữ liệu trong vòng {MAX_DAYS_TO_CHECK} ngày qua")
    st.info("💡 Gợi ý: Thử sử dụng vnstock3 API hoặc tăng MAX_DAYS_TO_CHECK")
    return None

def download_stock_data_vnstock(symbol, days_back=365):
    """Tải từ vnstock3 API"""
    if not VNSTOCK_AVAILABLE:
        return None
        
    try:
        stock = Vnstock().stock(symbol=symbol, source='TCBS')
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        df = stock.quote.history(start=start_date, end=end_date, interval='1D')
        
        if df is not None and not df.empty:
            df = df.reset_index()
            df = df.rename(columns={
                'time': '<DTYYYYMMDD>', 'open': '<Open>',
                'high': '<High>', 'low': '<Low>',
                'close': '<Close>', 'volume': '<Volume>'
            })
            df['<Ticker>'] = symbol
            
            if not pd.api.types.is_datetime64_any_dtype(df['<DTYYYYMMDD>']):
                df['<DTYYYYMMDD>'] = pd.to_datetime(df['<DTYYYYMMDD>'])
            
            return df[['<Ticker>', '<DTYYYYMMDD>', '<Open>', '<High>', '<Low>', '<Close>', '<Volume>']]
            
    except Exception as e:
        st.error(f"❌ Lỗi vnstock3 cho {symbol}: {str(e)}")
    return None

def download_stock_data(symbol, days_back=365, data_source='vnstock3'):
    """Tải dữ liệu từ nguồn được chọn"""
    if data_source == 'vnstock3' and VNSTOCK_AVAILABLE:
        return download_stock_data_vnstock(symbol, days_back)
    elif data_source == 'cafef':
        st.warning("⚠️ CafeF yêu cầu tải toàn bộ thị trường")
        return None
    return None

# === PHẦN 2: CHỈ BÁO KỸ THUẬT ===
def calculate_ma(data, period):
    return data['<Close>'].rolling(window=period).mean()

def calculate_ema(data, period):
    return data['<Close>'].ewm(span=period, adjust=False).mean()

def calculate_bollinger_bands(data, period=20, std_dev=2):
    ma = data['<Close>'].rolling(window=period).mean()
    std = data['<Close>'].rolling(window=period).std()
    return ma, ma + (std * std_dev), ma - (std * std_dev)

def calculate_rsi(data, period=14):
    delta = data['<Close>'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# === PHẦN 3: XỬ LÝ OUTLIERS ===
def detect_outliers_iqr(data, column, multiplier=1.5):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR
    return data[(data[column] < lower) | (data[column] > upper)], lower, upper

def detect_outliers_zscore(data, column, threshold=3):
    z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
    return data[z_scores > threshold]

def remove_outliers(data, column, method='iqr', **kwargs):
    if method == 'iqr':
        outliers, lower, upper = detect_outliers_iqr(data, column, **kwargs)
        cleaned = data[(data[column] >= lower) & (data[column] <= upper)]
    else:
        outliers = detect_outliers_zscore(data, column, **kwargs)
        cleaned = data[~data.index.isin(outliers.index)]
    return cleaned, outliers

# === PHẦN 4: CACHE DATA ===
@st.cache_data(ttl=3600)
def get_master_data(symbols_list, data_source='vnstock3'):
    all_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, symbol in enumerate(symbols_list):
        status_text.text(f"⏳ Đang tải {symbol}...")
        df = download_stock_data(symbol, data_source=data_source)
        if df is not None:
            all_data.append(df)
        progress_bar.progress((idx + 1) / len(symbols_list))
        time.sleep(0.5)
    
    progress_bar.empty()
    status_text.empty()
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        st.success(f"✅ Tải thành công {len(all_data)}/{len(symbols_list)} mã!")
        return combined_df
    return None

@st.cache_data(ttl=3600)
def get_cafef_all_exchanges():
    """Tải dữ liệu từ CafeF (tự động tìm ngày mới nhất)"""
    return download_latest_cafef_data()

# === DANH SÁCH MÃ ===
DEFAULT_STOCKS = ['FPT', 'VNM', 'VIC', 'VHM', 'HPG', 'TCB', 'VCB', 'BID', 'CTG', 'MBB',
                  'VPB', 'MSN', 'MWG', 'PLX', 'GAS', 'VRE', 'VJC', 'SSI', 'HDB', 'STB']

# === SIDEBAR ===
with st.sidebar:
    st.markdown("### ⚙️ CẤU HÌNH HỆ THỐNG")
    
    # RESET BUTTON
    if st.button("🔄 RESET DỮ LIỆU", use_container_width=True, type="secondary"):
        keys_to_delete = ['data', 'stock_list', 'data_source']
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Đã xóa dữ liệu!")
        time.sleep(1)
        st.rerun()
    
    st.markdown("---")
    
    # === PHẦN 1: CHỌN NGUỒN DỮ LIỆU ===
    st.markdown("#### 🌐 NGUỒN DỮ LIỆU")
    
    vnstock_status = "✅ Sẵn sàng" if VNSTOCK_AVAILABLE else "❌ Chưa cài"
    vnstock_color = "🟢" if VNSTOCK_AVAILABLE else "🔴"
    
    st.markdown(f"""
    <div style="background: rgba(58, 78, 147, 0.2); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>📡 vnstock3 API</span>
            <span>{vnstock_color} {vnstock_status}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>📦 CafeF Auto</span>
            <span>🟢 Sẵn sàng</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    data_source_options = []
    if VNSTOCK_AVAILABLE:
        data_source_options.append("📡 vnstock3")
    data_source_options.append("📦 CafeF")
    
    selected_source = st.radio(
        "Chọn nguồn:", 
        data_source_options,
        label_visibility="collapsed",
        key="source_selector"
    )
    
    source = 'vnstock3' if "vnstock3" in selected_source else 'cafef'
    
    # Hiển thị trạng thái nguồn đã chọn
    if source == 'vnstock3':
        st.success("✅ Đang dùng: **vnstock3 API**")
        st.info("📊 Real-time • 1 mã hoặc nhiều mã")
    else:
        st.info("✅ Đang dùng: **CafeF Auto**")
        st.warning("📊 Toàn thị trường • Tự động tìm ngày mới")
    
    st.markdown("---")

# === PHẦN 2: TẢI DỮ LIỆU (CONDITIONAL UI) ===
with st.sidebar:
    if source == 'vnstock3':
        st.markdown("### 📡 VNSTOCK3 - TẢI DỮ LIỆU")
        
        load_mode = st.radio(
            "Chọn chế độ:",
            ["🎯 Tải 1 mã", "📦 Tải nhiều mã"],
            label_visibility="collapsed"
        )
        
        if load_mode == "🎯 Tải 1 mã":
            st.markdown("#### 🔍 Nhập mã cổ phiếu")
            single_stock = st.text_input(
                "Ví dụ: FPT, VNM, VIC...",
                value="FPT",
                key="vnstock_single",
                label_visibility="collapsed"
            ).upper().strip()
            
            if st.button("🚀 TẢI DỮ LIỆU", use_container_width=True, type="primary"):
                if single_stock:
                    with st.spinner(f"⏳ Đang tải {single_stock} từ vnstock3..."):
                        df = download_stock_data(single_stock, data_source='vnstock3')
                        if df is not None and not df.empty:
                            st.session_state['data'] = df
                            st.session_state['stock_list'] = [single_stock]
                            st.session_state['data_source'] = 'vnstock3'
                            st.success(f"✅ Tải thành công {single_stock}!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"❌ Không tải được {single_stock}")
                else:
                    st.warning("⚠️ Vui lòng nhập mã cổ phiếu")
        
        else:  # Tải nhiều mã
            st.markdown("#### 📦 Tải danh sách phổ biến")
            st.info(f"Sẽ tải {len(DEFAULT_STOCKS)} mã blue-chip")
            
            with st.expander("📋 Xem danh sách"):
                st.write(", ".join(DEFAULT_STOCKS))
            
            if st.button("📥 TẢI DANH SÁCH", use_container_width=True, type="primary"):
                with st.spinner(f"⏳ Đang tải {len(DEFAULT_STOCKS)} mã..."):
                    df = get_master_data(DEFAULT_STOCKS, data_source='vnstock3')
                    if df is not None and not df.empty:
                        st.session_state['data'] = df
                        st.session_state['stock_list'] = DEFAULT_STOCKS
                        st.session_state['data_source'] = 'vnstock3'
                        st.success(f"✅ Tải thành công {len(DEFAULT_STOCKS)} mã!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Lỗi tải dữ liệu")
    
    else:  # CafeF
        st.markdown("### 📦 CAFEF - TẢI DỮ LIỆU")
        
        # Kiểm tra xem đã có dữ liệu chưa
        has_data = 'data' in st.session_state and st.session_state['data'] is not None
        
        if has_data:
            st.success("✅ Đã có dữ liệu trong bộ nhớ")
            total_stocks = len(st.session_state['data']['<Ticker>'].unique())
            st.info(f"📊 Có {total_stocks} mã cổ phiếu")
            
            st.markdown("#### 🔍 Tìm kiếm mã cụ thể")
            search_stock = st.text_input(
                "Nhập mã để lọc:",
                key="cafef_search",
                placeholder="Ví dụ: FPT",
                label_visibility="collapsed"
            ).upper().strip()
            
            if search_stock:
                if st.button("🔍 LỌC MÃ", use_container_width=True):
                    df = st.session_state['data']
                    filtered = df[df['<Ticker>'] == search_stock]
                    if not filtered.empty:
                        st.session_state['data'] = filtered
                        st.session_state['stock_list'] = [search_stock]
                        st.success(f"✅ Đã lọc {search_stock}")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"❌ Không tìm thấy {search_stock}")
            
            if st.button("🔄 TẢI LẠI TOÀN BỘ", use_container_width=True, type="secondary"):
                if 'data' in st.session_state:
                    del st.session_state['data']
                if 'stock_list' in st.session_state:
                    del st.session_state['stock_list']
                st.info("Nhấn nút 'TẢI TOÀN THỊ TRƯỜỜNG' để tải lại")
                st.rerun()
        
        else:  # Chưa có dữ liệu
            st.markdown("#### 📥 Tải toàn thị trường")
            st.info("🔍 Tự động tìm ngày gần nhất (lùi max 10 ngày)")
            st.warning("⏱️ Quá trình có thể mất 30-90 giây")
            
            with st.expander("ℹ️ Thông tin"):
                st.markdown("""
                **CafeF Auto sẽ:**
                - 🔎 Quét 10 ngày gần nhất
                - 📥 Tải file ZIP (~50-100MB)
                - 📦 Giải nén và xử lý CSV
                - 🧹 Làm sạch dữ liệu
                - ✅ Trả về toàn bộ thị trường
                """)
            
            if st.button("📥 TẢI TOÀN THỊ TRƯỜỜNG", use_container_width=True, type="primary"):
                with st.spinner("⏳ Đang xử lý..."):
                    df = get_cafef_all_exchanges()
                    if df is not None and not df.empty:
                        st.info(f"✓ Nhận được {len(df)} bản ghi")
                        st.info(f"✓ Columns: {', '.join(df.columns.tolist())}")
                        
                        # Làm sạch ticker
                        ticker_series = df['<Ticker>'].dropna().astype(str)
                        ticker_list = [t.strip() for t in ticker_series.unique() 
                                     if t.strip() and t.strip().upper() != 'NAN']
                        
                        if ticker_list:
                            st.session_state['data'] = df
                            st.session_state['stock_list'] = sorted(ticker_list)
                            st.session_state['data_source'] = 'cafef'
                            st.success(f"🎉 Lưu thành công {len(ticker_list)} mã!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Không có ticker hợp lệ")
                    else:
                        st.error("❌ Không tải được dữ liệu")
    
    st.markdown("---")

# === PHẦN 3: ĐIỀU KHIỂN BIỂU ĐỒ (CHỈ HIỆN KHI CÓ DỮ LIỆU) ===
if 'data' in st.session_state and st.session_state['data'] is not None:
    with st.sidebar:
        st.markdown("### 📊 ĐIỀU KHIỂN BIỂU ĐỒ")
        
        df = st.session_state['data']
        
        # Làm sạch ticker list
        ticker_series = df['<Ticker>'].dropna().astype(str)
        ticker_list = sorted([t.strip() for t in ticker_series.unique() 
                            if t.strip() and t.strip().upper() != 'NAN'])
        
        if not ticker_list:
            st.error("❌ Không có mã hợp lệ")
            st.stop()
        
        # Chọn mã
        st.markdown("#### 🎯 Chọn mã cổ phiếu")
        stock_code = st.selectbox(
            f"Tổng: {len(ticker_list)} mã",
            ticker_list,
            label_visibility="collapsed",
            key="stock_selector"
        )
        
        st.markdown("---")
        
        # Loại biểu đồ
        st.markdown("#### 📈 Loại biểu đồ")
        chart_type = st.radio(
            "Chọn:",
            ["📊 Nến Nhật", "📈 Line Chart"],
            label_visibility="collapsed"
        )
        chart_type = "Nến Nhật" if "Nến" in chart_type else "Line Chart"
        
        st.markdown("---")
        
        # Chỉ báo kỹ thuật
        st.markdown("#### 📊 Chỉ báo kỹ thuật")
        
        col1, col2 = st.columns(2)
        with col1:
            show_ma = st.checkbox("MA", value=True)
            show_bb = st.checkbox("Bollinger")
        with col2:
            show_ema = st.checkbox("EMA", value=False)
            show_rsi = st.checkbox("RSI", value=False)
        
        # Cấu hình MA
        if show_ma:
            ma_period = st.slider("Chu kỳ MA:", 5, 50, 20, key="ma")
        
        # Cấu hình EMA
        if show_ema:
            ema_period = st.slider("Chu kỳ EMA:", 5, 50, 12, key="ema")
        
        st.markdown("---")
        
        # Outliers
        st.markdown("#### 🔬 Phát hiện Outliers")
        show_outliers = st.checkbox("Hiện Outliers", value=False)
        
        if show_outliers:
            outlier_method = st.radio(
                "Phương pháp:",
                ["IQR", "Z-Score"],
                horizontal=True,
                label_visibility="collapsed"
            )
            
            if outlier_method == "IQR":
                iqr_multiplier = st.slider("IQR Multiplier:", 1.0, 3.0, 1.5, 0.1)
            else:
                zscore_threshold = st.slider("Z-Score:", 2.0, 4.0, 3.0, 0.1)
            
            remove_outlier = st.checkbox("Loại bỏ Outliers")
        
        st.markdown("---")
        
        # Cài đặt chart
        st.markdown("#### ⚙️ Cài đặt")
        chart_height = st.slider("Chiều cao:", 500, 1000, 700, 50)
    
    stock_data = df[df['<Ticker>'] == stock_code].sort_values(by='<DTYYYYMMDD>').copy()
    
    if not stock_data.empty:
        original_data = stock_data.copy()
        outliers_data = None
        
        if show_outliers:
            if outlier_method == "IQR":
                outliers_data, lower, upper = detect_outliers_iqr(stock_data, '<Close>', multiplier=iqr_multiplier)
                if remove_outlier:
                    stock_data, _ = remove_outliers(stock_data, '<Close>', method='iqr', multiplier=iqr_multiplier)
            else:
                outliers_data = detect_outliers_zscore(stock_data, '<Close>', threshold=zscore_threshold)
                if remove_outlier:
                    stock_data, _ = remove_outliers(stock_data, '<Close>', method='zscore', threshold=zscore_threshold)
        
        # METRICS
        latest = stock_data.iloc[-1]
        prev = stock_data.iloc[-2] if len(stock_data) > 1 else latest
        
        price_change = latest['<Close>'] - prev['<Close>']
        price_change_pct = (price_change / prev['<Close>'] * 100) if prev['<Close>'] != 0 else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("💰 GIÁ ĐÓNG", f"{latest['<Close>']:,.2f}", f"{price_change:+,.2f} ({price_change_pct:+.2f}%)")
        with col2:
            st.metric("📈 CAO NHẤT", f"{latest['<High>']:,.2f}")
        with col3:
            st.metric("📉 THẤP NHẤT", f"{latest['<Low>']:,.2f}")
        with col4:
            st.metric("📊 KHỐI LƯỢNG", f"{latest['<Volume>']:,.0f}")
        with col5:
            avg_volume = stock_data['<Volume>'].tail(20).mean()
            volume_change = ((latest['<Volume>'] - avg_volume) / avg_volume * 100) if avg_volume != 0 else 0
            st.metric("📦 TB 20", f"{avg_volume:,.2f}", f"{volume_change:+.2f}%")
        
        if show_outliers and outliers_data is not None and len(outliers_data) > 0:
            st.warning(f"⚠️ Phát hiện {len(outliers_data)} outliers ({outlier_method})")
            if remove_outlier:
                st.info(f"✅ Đã loại bỏ {len(outliers_data)} outliers")
        
        st.markdown("---")
        st.markdown(f"### 📈 Phân tích: **{stock_code}**")
        
        time_range = st.select_slider("⏱️ Thời gian:", options=['1 tháng', '3 tháng', '6 tháng', '1 năm', 'Tất cả'], value='3 tháng')
        
        if time_range != 'Tất cả':
            days_map = {'1 tháng': 30, '3 tháng': 90, '6 tháng': 180, '1 năm': 365}
            cutoff_date = datetime.now() - timedelta(days=days_map[time_range])
            stock_data = stock_data[stock_data['<DTYYYYMMDD>'] >= cutoff_date]
            if outliers_data is not None and not outliers_data.empty:
                outliers_data = outliers_data[outliers_data['<DTYYYYMMDD>'] >= cutoff_date]
        
        if show_ma:
            stock_data['MA'] = calculate_ma(stock_data, ma_period)
        if show_ema:
            stock_data['EMA'] = calculate_ema(stock_data, ema_period)
        if show_bb:
            stock_data['BB_MA'], stock_data['BB_Upper'], stock_data['BB_Lower'] = calculate_bollinger_bands(stock_data)
        if show_rsi:
            stock_data['RSI'] = calculate_rsi(stock_data)
        
        # === PHẦN SỬA LỖI HIỂN THỊ NGÀY ===
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        rows = 3 if show_rsi else 2
        row_heights = [0.6, 0.2, 0.2] if show_rsi else [0.7, 0.3]
        subplot_titles = [f'💹 {stock_code}', '📊 Volume', '📉 RSI'] if show_rsi else [f'💹 {stock_code}', '📊 Volume']
        
        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, subplot_titles=subplot_titles, row_heights=row_heights)
        
        # Biểu đồ chính
        if chart_type == "Nến Nhật":
            fig.add_trace(go.Candlestick(
                x=stock_data['<DTYYYYMMDD>'],
                open=stock_data['<Open>'],
                high=stock_data['<High>'],
                low=stock_data['<Low>'],
                close=stock_data['<Close>'],
                name="Giá",
                increasing_line_color='#5994ce',
                decreasing_line_color='#b957ce'
            ), row=1, col=1)
        else:
            fig.add_trace(go.Scatter(
                x=stock_data['<DTYYYYMMDD>'],
                y=stock_data['<Close>'],
                name="Giá",
                line=dict(color='#5994ce', width=2.5),
                fill='tozeroy',
                fillcolor='rgba(89, 148, 206, 0.1)'
            ), row=1, col=1)
        
        # Outliers
        if show_outliers and outliers_data is not None and not outliers_data.empty:
            fig.add_trace(go.Scatter(
                x=outliers_data['<DTYYYYMMDD>'],
                y=outliers_data['<Close>'],
                mode='markers',
                name='Outliers',
                marker=dict(color='#ff4444', size=12, symbol='x', line=dict(color='#ffffff', width=2))
            ), row=1, col=1)
        
        # MA
        if show_ma and 'MA' in stock_data.columns:
            fig.add_trace(go.Scatter(
                x=stock_data['<DTYYYYMMDD>'],
                y=stock_data['MA'],
                name=f'MA{ma_period}',
                line=dict(color='#ffa502', width=2.5)
            ), row=1, col=1)
        
        # EMA
        if show_ema and 'EMA' in stock_data.columns:
            fig.add_trace(go.Scatter(
                x=stock_data['<DTYYYYMMDD>'],
                y=stock_data['EMA'],
                name=f'EMA{ema_period}',
                line=dict(color='#5c58bb', width=2.5)
            ), row=1, col=1)
        
        # Bollinger Bands
        if show_bb and 'BB_Upper' in stock_data.columns:
            fig.add_trace(go.Scatter(x=stock_data['<DTYYYYMMDD>'], y=stock_data['BB_Upper'], name='BB Upper', line=dict(color='rgba(185, 87, 206, 0.5)', width=1, dash='dash'), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=stock_data['<DTYYYYMMDD>'], y=stock_data['BB_MA'], name='BB Mid', line=dict(color='rgba(185, 87, 206, 0.8)', width=1.5), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=stock_data['<DTYYYYMMDD>'], y=stock_data['BB_Lower'], name='BB Lower', line=dict(color='rgba(185, 87, 206, 0.5)', width=1, dash='dash'), fill='tonexty', fillcolor='rgba(185, 87, 206, 0.1)', showlegend=False), row=1, col=1)
        
        # Volume
        colors = ['#5994ce' if row['<Close>'] >= row['<Open>'] else '#b957ce' for index, row in stock_data.iterrows()]
        fig.add_trace(go.Bar(x=stock_data['<DTYYYYMMDD>'], y=stock_data['<Volume>'], name="Volume", marker_color=colors), row=2, col=1)
        
        # RSI
        if show_rsi and 'RSI' in stock_data.columns:
            fig.add_trace(go.Scatter(x=stock_data['<DTYYYYMMDD>'], y=stock_data['RSI'], name="RSI", line=dict(color='#5c58bb', width=2)), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#b957ce", opacity=0.5, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#5994ce", opacity=0.5, row=3, col=1)
        
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            height=chart_height,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff', size=12),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1, bgcolor='rgba(58, 78, 147, 0.8)'),
            margin=dict(l=10, r=10, t=60, b=10)
        )
        
        for i in range(1, rows + 1):
            fig.update_xaxes(gridcolor='rgba(92, 88, 187, 0.1)', showgrid=True, zeroline=False, row=i, col=1)
            fig.update_yaxes(gridcolor='rgba(92, 88, 187, 0.1)', showgrid=True, zeroline=False, row=i, col=1)
        
        # === PHẦN SỬA LỖI LỖ TRỐNG (TỰ ĐỘNG CHO CẢ NGÀY LỄ) ===
        # Lấy ra danh sách tất cả các ngày có trong dữ liệu đang hiển thị
        all_present_dates = pd.to_datetime(stock_data['<DTYYYYMMDD>'])
        
        # Chỉ thực hiện nếu có dữ liệu
        if not all_present_dates.empty:
            # Tạo ra một chuỗi ngày liên tục từ ngày đầu đến ngày cuối
            full_date_range = pd.date_range(start=all_present_dates.min(), end=all_present_dates.max())
            
            # Tìm những ngày không có trong dữ liệu (chính là ngày nghỉ T7, CN, Lễ)
            missing_dates = full_date_range.difference(all_present_dates)
            
            # Cập nhật trục X để "bỏ qua" (ẩn đi) những ngày không có dữ liệu này
            fig.update_xaxes(rangebreaks=[dict(values=missing_dates)])
        
        fig.update_yaxes(title_text="Giá (VNĐ)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        if show_rsi:
            fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        # === KẾT THÚC PHẦN SỬA LỖI ===

        st.markdown("---")
        
        # BẢNG DỮ LIỆU
        st.markdown('<div class="data-table-container">', unsafe_allow_html=True)
        st.markdown("### 📈 DỮ LIỆU CHI TIẾT & THỐNG KÊ")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="stats-card">
                    <h4>📊 Thống kê giá</h4>
                    <p>TB: {stock_data['<Close>'].mean():,.2f}</p>
                    <p>Std: {stock_data['<Close>'].std():,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="stats-card">
                    <h4>📈 Biên độ</h4>
                    <p>Max: {stock_data['<Close>'].max():,.2f}</p>
                    <p>Min: {stock_data['<Close>'].min():,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="stats-card">
                    <h4>💹 Volume TB</h4>
                    <p>20 ngày: {stock_data['<Volume>'].tail(20).mean():,.2f}</p>
                    <p>Tổng: {stock_data['<Volume>'].mean():,.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        
        display_df = stock_data[['<DTYYYYMMDD>', '<Open>', '<High>', '<Low>', '<Close>', '<Volume>']].copy()
        display_df.columns = ['📅 Ngày', '🔵 Mở', '🔺 Cao', '🔻 Thấp', '⭕ Đóng', '📊 Volume']
        
        for col in ['🔵 Mở', '🔺 Cao', '🔻 Thấp', '⭕ Đóng']:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.2f}")
        display_df['📊 Volume'] = display_df['📊 Volume'].apply(lambda x: f"{x:,.2f}")
        
        st.dataframe(display_df.sort_values(by='📅 Ngày', ascending=False).reset_index(drop=True), use_container_width=True, height=450)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Không tìm thấy dữ liệu cho {stock_code}")
else:
    st.markdown("""
        <div class="data-table-container">
            <h3>🚀 Hướng dẫn sử dụng</h3>
            <ul>
                <li><strong>Bước 1:</strong> Chọn nguồn dữ liệu (vnstock3 API hoặc CafeF Auto)</li>
                <li><strong>Bước 2:</strong> Chọn chế độ tải (1 mã hoặc toàn thị trường)</li>
                <li><strong>Bước 3:</strong> Nhấn nút tải dữ liệu</li>
                <li><strong>Bước 4:</strong> Phân tích với các chỉ báo kỹ thuật</li>
            </ul>
            <br>
            <h3>✨ Tính năng nổi bật</h3>
            <ul>
                <li>📡 <strong>vnstock3 API:</strong> Dữ liệu real-time từ TCBS</li>
                <li>📦 <strong>CafeF Auto:</strong> Tự động tìm ngày có dữ liệu gần nhất (lùi tối đa 10 ngày)</li>
                <li>🔄 <strong>Auto fallback:</strong> Chuyển nguồn tự động khi API lỗi</li>
                <li>📊 <strong>Biểu đồ:</strong> Nến Nhật & Line Chart với hiệu ứng đẹp mắt</li>
                <li>📈 <strong>Chỉ báo:</strong> MA, EMA, Bollinger Bands, RSI</li>
                <li>🔬 <strong>Outliers:</strong> Phát hiện bằng IQR hoặc Z-Score</li>
                <li>🎨 <strong>UI/UX:</strong> Glassmorphism với gradient động</li>
            </ul>
            <br>
            <h3>💡 Lựa chọn nguồn dữ liệu</h3>
            <table style="width:100%; color: white;">
                <tr style="background: rgba(92, 88, 187, 0.3);">
                    <th style="padding: 0.5rem;">Tình huống</th>
                    <th style="padding: 0.5rem;">Nguồn đề xuất</th>
                    <th style="padding: 0.5rem;">Ưu điểm</th>
                </tr>
                <tr>
                    <td style="padding: 0.5rem;">Phân tích 1 mã cụ thể</td>
                    <td style="padding: 0.5rem;">📡 vnstock3</td>
                    <td style="padding: 0.5rem;">Nhanh, real-time</td>
                </tr>
                <tr>
                    <td style="padding: 0.5rem;">So sánh nhiều mã</td>
                    <td style="padding: 0.5rem;">📦 CafeF</td>
                    <td style="padding: 0.5rem;">Toàn thị trường</td>
                </tr>
                <tr>
                    <td style="padding: 0.5rem;">Phân tích lịch sử</td>
                    <td style="padding: 0.5rem;">📦 CafeF</td>
                    <td style="padding: 0.5rem;">Dữ liệu điều chỉnh</td>
                </tr>
                <tr>
                    <td style="padding: 0.5rem;">API bị lỗi</td>
                    <td style="padding: 0.5rem;">📦 CafeF</td>
                    <td style="padding: 0.5rem;">Luôn sẵn sàng</td>
                </tr>
            </table>
            <br>
            <h3>🎯 CafeF Auto - Cách hoạt động</h3>
            <p>Hệ thống sẽ tự động:</p>
            <ol>
                <li>🔍 Quét ngược 10 ngày gần nhất</li>
                <li>✅ Tìm ngày có dữ liệu khả dụng</li>
                <li>📥 Tải file ZIP từ CafeF CDN</li>
                <li>📦 Giải nén và xử lý CSV</li>
                <li>🧹 Làm sạch và chuẩn hóa dữ liệu</li>
                <li>✨ Trả về DataFrame sẵn sàng phân tích</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)

