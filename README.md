# NET_262701303_03-UDM_16

**Đồ án môn Lập trình mạng**  
Nhóm NET_262701303_03 · Đề tài UDM_16: **Game Caro trực tuyến**

## Danh sách thành viên

| STT | Họ và tên | MSSV |
| ---: | --- | ---: |
| 1 | Lê Văn Khải | 051206008834 |
| 2 | Trần Nguyễn Hoàng Minh | 083206001369 |
| 3 | Phạm Minh Hiếu | 054206004641 |
| 4 | Trần Quang Huy | 054206009272 |
| 5 | Trần Gia Khiêm | 054206009756 |
| 6 | Lê Minh Như | 077306006704 |

## Giới thiệu đề tài

Đề tài xây dựng trò chơi Caro trực tuyến theo mô hình **Client–Server**. Người chơi có thể kết nối qua mạng, đăng nhập, tạo hoặc tham gia phòng đấu và chơi theo lượt. Hệ thống đồng bộ trạng thái bàn cờ theo thời gian thực, đồng thời xử lý các tình huống mất kết nối.

### Thành phần hệ thống

- **Server:** Tiếp nhận kết nối, quản lý người chơi trực tuyến và các phòng đấu, đồng bộ trạng thái trận đấu giữa các Client, đồng thời kiểm tra tính hợp lệ của trò chơi.
- **Client:** Cung cấp giao diện để đăng nhập, xem sảnh chờ (Lobby), tạo hoặc tham gia phòng đấu, thực hiện nước đi và nhận kết quả.

### Chức năng chính

- Kết nối Client–Server, gửi và nhận thông điệp, xử lý lỗi mạng hoặc tình huống người chơi mất kết nối.
- Đăng nhập, quản lý trạng thái người chơi, xem danh sách người chơi trực tuyến và gửi hoặc nhận lời mời đấu.
- Tạo, tham gia hoặc rời phòng; quản lý trạng thái phòng và tự động phân chia quân X/O.
- Hiển thị bàn cờ, xác thực nước đi, đổi lượt và kiểm tra điều kiện thắng, thua hoặc hòa.
- Đồng bộ bàn cờ, gửi thông báo, hỗ trợ chế độ người xem (Spectator) và lưu lịch sử nước đi.
- Cung cấp giao diện (GUI) cho các màn hình đăng nhập, sảnh chờ, phòng đấu và bàn cờ.
