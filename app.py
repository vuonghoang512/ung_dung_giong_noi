import streamlit as st
import edge_tts
import asyncio
import os

# --- CẤU HÌNH BẢO MẬT ---
# BẠN HÃY THAY ĐỔI MẬT KHẨU CỦA MÌNH Ở DÒNG DƯỚI ĐÂY:
MAT_KHAU_DUNG = "05121991"

# Cấu hình trang web
st.set_page_config(page_title="Chuyển Văn Bản Thành Giọng Nói", page_icon="🎤")

# --- HỆ THỐNG ĐĂNG NHẬP ---
# Kiểm tra xem người dùng đã đăng nhập chưa
if "da_dang_nhap" not in st.session_state:
    st.session_state.da_dang_nhap = False

# Nếu chưa đăng nhập, hiện màn hình khóa
if not st.session_state.da_dang_nhap:
    st.title("🔒 Ứng Dụng Nội Bộ")
    st.write("Vui lòng nhập mật mã để truy cập hệ thống.")
    
    mat_khau_nhap = st.text_input("Nhập mật mã:", type="password") # type="password" giúp ẩn ký tự
    
    if st.button("Mở Khóa"):
        if mat_khau_nhap == MAT_KHAU_DUNG:
            st.session_state.da_dang_nhap = True
            st.rerun() # Tải lại trang để vào giao diện chính
        else:
            st.error("❌ Mật mã không chính xác. Vui lòng thử lại!")
    
    # Dừng chạy toàn bộ phần code bên dưới nếu chưa mở khóa thành công
    st.stop() 


# --- GIAO DIỆN ỨNG DỤNG CHÍNH (Chỉ hiện khi đã đăng nhập) ---
# Danh sách giọng đọc tiếng Việt của Microsoft
VOICES = {
    "Nữ - Miền Nam (Hoài My)": "vi-VN-HoaiMyNeural",
    "Nam - Miền Bắc (Nam Minh)": "vi-VN-NamMinhNeural"
}

# Hàm xử lý âm thanh
async def tao_am_thanh(van_ban, giong_doc, toc_do):
    chuoi_toc_do = f"{toc_do:+d}%" 
    ket_noi = edge_tts.Communicate(van_ban, giong_doc, rate=chuoi_toc_do)
    ten_file_xuat = "giong_doc_ai.mp3"
    await ket_noi.save(ten_file_xuat)
    return ten_file_xuat

st.title("🎤 Ứng Dụng Chuyển Văn Bản Thành Giọng Nói")
st.markdown("Được phát triển bởi: Hoàng Vương") 
st.write("---") 

# Ô nhập văn bản
van_ban_nhap = st.text_area("Nhập văn bản cần đọc vào đây:", height=150, placeholder="Xin chào, hôm nay bạn thế nào?")

# Khu vực tùy chỉnh giọng và tốc độ
cot1, cot2 = st.columns(2)
with cot1:
    chon_giong = st.selectbox("1. Chọn Giọng Đọc:", list(VOICES.keys()))
with cot2:
    toc_do = st.slider("2. Tùy chỉnh tốc độ đọc (%)", min_value=-50, max_value=50, value=0, step=5)
    st.caption("0 là tốc độ chuẩn. Kéo sang phải để đọc nhanh hơn, sang trái để đọc chậm lại.")

# Nút bấm tạo âm thanh
if st.button("Tạo Giọng Đọc", type="primary"):
    if van_ban_nhap.strip() == "":
        st.warning("⚠️ Vui lòng nhập nội dung văn bản trước khi tạo!")
    else:
        with st.spinner("Đang tạo âm thanh AI... Bạn đợi vài giây nhé!"):
            giong_da_chon = VOICES[chon_giong]
            
            # Chạy hàm tạo âm thanh
            file_am_thanh = asyncio.run(tao_am_thanh(van_ban_nhap, giong_da_chon, toc_do))
            
            st.success("🎉 Đã tạo xong! Bạn có thể nghe thử hoặc tải về bên dưới.")
            
            # Phát âm thanh ngay trên web
            st.audio(file_am_thanh, format="audio/mp3")
            
            # Nút tải file
            with open(file_am_thanh, "rb") as file:
                st.download_button(
                    label="⬇️ Tải file MP3 xuống máy",
                    data=file,
                    file_name="giong_doc_ai.mp3",
                    mime="audio/mp3"
                )

# Nút Đăng xuất
st.write("---")
if st.button("Đăng xuất (Khóa ứng dụng)"):
    st.session_state.da_dang_nhap = False
    st.rerun()

# Thêm chữ ký ở cuối trang
st.markdown("---")
st.caption("© 2026 - Bản quyền thuộc về Hoàng Vương - Ủy viên UBKT Đảng ủy xã Hàm Thạnh")