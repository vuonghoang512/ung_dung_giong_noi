import streamlit as st
import edge_tts
import asyncio
import os
import pandas as pd
import io
import zipfile
from datetime import datetime

# --- 1. CẤU HÌNH BẢO MẬT & THÔNG TIN ---
# BẠN HÃY THAY ĐỔI MẬT KHẨU CỦA MÌNH Ở DÒNG DƯỚI ĐÂY:
MAT_KHAU_DUNG = "051291" 
TEN_TAC_GIA = "Hoàng Vương"

# Cấu hình trang web
st.set_page_config(page_title=f"AI TTS Portal - {TEN_TAC_GIA}", page_icon="🎤", layout="wide")

# --- 2. TÂN TRANG GIAO DIỆN (Đổi màu & Font) ---
# Chúng ta dùng CSS để thay đổi diện mạo ứng dụng chuyên nghiệp hơn
st.markdown(f"""
<style>
    /* Màu nền chính và font chữ */
    .stApp {{
        background-color: #0e1117;
        color: #fafafa;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}
    /* Màu tiêu đề */
    h1, h2, h3 {{
        color: #00a8ff !important;
        font-weight: 700;
    }}
    /* Tùy chỉnh Sidebar (Thanh bên) */
    [data-testid="stSidebar"] {{
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }}
    /* Tùy chỉnh nút bấm chính */
    .stButton>button {{
        background-color: #00a8ff;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }}
    .stButton>button:hover {{
        background-color: #0084cc;
        transform: scale(1.02);
    }}
    /* Khu vực Author Branding */
    .author-box {{
        padding: 15px;
        border-radius: 10px;
        background-color: #1f2937;
        border: 1px solid #374151;
        text-align: center;
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)


# --- 3. HỆ THỐNG ĐĂNG NHẬP (Giữ nguyên security) ---
if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

if not st.session_state.da_dang_nhap:
    # Màn hình khóa được tân trang
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="author-box">
            <h1 style='font-size: 50px;'>🔒</h1>
            <h2>HỆ THỐNG CÁ NHÂN</h2>
            <p>Bản quyền thuộc về: <b>{TEN_TAC_GIA}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        mat_khau_nhap = st.text_input("Nhập mật mã để mở khóa:", type="password")
        
        if st.button("Xác nhận Truy cập"):
            if mat_khau_nhap == MAT_KHAU_DUNG:
                st.session_state.da_dang_nhap = True
                st.rerun()
            else:
                st.error("❌ Mật mã không chính xác!")
        st.markdown("---")
        st.caption("© 2026 - All Rights Reserved.")
    st.stop() 


# --- 4. CÁC HÀM XỬ LÝ KỸ THUẬT (Async & Batch) ---

# Danh sách giọng đọc
VOICES = {
    "Nữ - Miền Nam (Hoài My)": "vi-VN-HoaiMyNeural",
    "Nam - Miền Bắc (Nam Minh)": "vi-VN-NamMinhNeural"
}

# Hàm tạo 1 file âm thanh (dùng bộ nhớ đệm tạo nhanh)
async def process_single_tts(text, voice, rate_str):
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

# Hàm xử lý hàng loạt: Đọc list văn bản và nén ZIP
async def process_batch_tts(text_list, filenames_list, voice, rate):
    rate_str = f"{rate:+d}%"
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (text, fname) in enumerate(zip_file(text_list, filenames_list)):
            # Cập nhật tiến độ
            percent_complete = int((i / len(text_list)) * 100)
            progress_bar.progress(percent_complete)
            status_text.text(f"Đang xử lý file {i+1}/{len(text_list)}: {fname}.mp3...")
            
            # Tạo âm thanh
            audio_content = await process_single_tts(text, voice, rate_str)
            
            # Ghi trực tiếp vào file ZIP trong bộ nhớ
            zip_file.writestr(f"{fname}.mp3", audio_content)
            
        progress_bar.progress(100)
        status_text.text("✅ Đã hoàn thành xử lý toàn bộ!")
        
    return zip_buffer.getvalue()


# --- 5. GIAO DIỆN CHÍNH (Đã nâng cấp) ---

# Sidebar: Nơi chứa Logo và Cấu hình giọng
with st.sidebar:
    st.markdown(f"""
    <div class="author-box" style="border-color: #00a8ff;">
        <h1 style='font-size: 40px; margin:0;'>🎤</h1>
        <h3 style='margin:10px 0 0 0; color:white !important;'>AI TTS Portal</h3>
        <p style='margin:0; opacity:0.8;'>By {TEN_TAC_GIA}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("⚙️ Cấu hình Giọng")
    chon_giong = st.selectbox("1. Chọn Giọng Đọc:", list(VOICES.keys()))
    toc_do = st.slider("2. Tốc độ đọc (%)", min_value=-50, max_value=50, value=0, step=5)
    st.caption("0 là tốc độ chuẩn.")
    
    st.write("---")
    if st.button("🚪 Đăng xuất"):
        st.session_state.da_dang_nhap = False
        st.rerun()

# Khu vực chính: Dùng TAB để chia tính năng
st.title("Hệ thống Chuyển đổi Giọng nói AI Cao cấp")
st.write("Chào mừng bạn đến với cổng xử lý âm thanh chuyên nghiệp.")

tab1, tab2 = st.tabs(["📄 Đọc Văn bản Đơn", "📁 Xử lý Hàng loạt (Excel)"])

# --- TAB 1: Chức năng cơ bản (đã dọn dẹp) ---
with tab1:
    van_ban_nhap = st.text_area("Nhập văn bản cần đọc:", height=200, placeholder="Nhập nội dung vào đây...")
    
    col1, col2 = st.columns([1,3])
    with col1:
        btn_single = st.button("Tạo Giọng Đọc", type="primary", key="btn_single")
        
    if btn_single:
        if van_ban_nhap.strip() == "":
            st.warning("⚠️ Vui lòng nhập nội dung!")
        else:
            with st.spinner("Đang tạo âm thanh..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                giong_da_chon = VOICES[chon_giong]
                rate_str = f"{toc_do:+d}%"
                
                audio_content = loop.run_until_complete(process_single_tts(van_ban_nhap, giong_da_chon, rate_str))
                
                st.success("🎉 Đã tạo xong!")
                st.audio(audio_content, format="audio/mp3")
                st.download_button(label="⬇️ Tải file MP3", data=audio_content, file_name="giong_doc_vuong.mp3", mime="audio/mp3")


# --- TAB 2: Chức năng Xử lý hàng loạt (MỚI) ---
with tab2:
    st.header("Sản xuất Âm thanh Hàng loạt từ Excel")
    st.write("""
    **Hướng dẫn:** Upload file Excel (.xlsx) có ít nhất 2 cột:
    1. Cột **'Tên File'**: Dùng để đặt tên cho file MP3 xuất ra.
    2. Cột **'Nội Dung'**: Chứa văn bản AI sẽ đọc.
    👉 Ứng dụng sẽ nén tất cả file MP3 thành một file ZIP để bạn tải về.
    """)
    
    file_excel = st.file_uploader("Chọn file Excel của bạn:", type=["xlsx"])
    
    if file_excel:
        try:
            # Đọc file Excel dùng pandas
            df = pd.read_excel(file_excel)
            st.write("---")
            st.subheader("Xem trước dữ liệu (5 dòng đầu):")
            st.dataframe(df.head(), use_container_width=True)
            
            # Kiểm tra xem có đúng tên cột yêu cầu không
            columns = df.columns.tolist()
            col_name_fname = st.selectbox("Chọn cột chứa Tên File:", columns, index=0 if 'Tên File' in columns else 0)
            col_name_content = st.selectbox("Chọn cột chứa Nội Dung:", columns, index=1 if 'Nội Dung' in columns else 1)
            
            total_rows = len(df)
            st.info(f"📋 Tìm thấy {total_rows} dòng dữ liệu sẵn sàng xử lý.")
            
            btn_batch = st.button(f"Bắt đầu xử lý {total_rows} file", type="primary", key="btn_batch")
            
            if btn_batch:
                # Trích xuất dữ liệu, loại bỏ dòng trống
                df_clean = df[[col_name_fname, col_name_content]].dropna()
                text_list = df_clean[col_name_content].astype(str).tolist()
                # Tạo tên file an toàn (không dấu, không ký tự lạ)
                fname_list = df_clean[col_name_fname].astype(str).apply(lambda x: "".join([c for c in x if c.isalpha() or c.isdigit() or c==' ']).rstrip()).tolist()
                
                if not text_list:
                    st.error("❌ Không tìm thấy dữ liệu hợp lệ trong các cột đã chọn!")
                else:
                    with st.spinner("Cỗ máy đang hoạt động... Vui lòng không đóng trình duyệt!"):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        giong_da_chon = VOICES[chon_giong]
                        
                        # Chạy xử lý hàng loạt
                        zip_data = loop.run_until_complete(process_batch_tts(text_list, fname_list, giong_da_chon, toc_do))
                        
                        st.success(f"✅ Hoàn tất! Đã tạo xong {len(text_list)} file âm thanh.")
                        
                        # Tạo tên file ZIP theo thời gian hiện tại
                        time_str = datetime.now().strftime("%Y%m%d_%H%M")
                        zip_fname = f"Batch_TTS_{TEN_TAC_GIA}_{time_str}.zip"
                        
                        st.download_button(
                            label=f"⬇️ Tải về File ZIP ({len(text_list)} bản thu)",
                            data=zip_data,
                            file_name=zip_fname,
                            mime="application/zip"
                        )
                        
        except Exception as e:
            st.error(f"❌ Có lỗi khi đọc file Excel: {e}")
