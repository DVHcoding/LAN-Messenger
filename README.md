
# Tài liệu: Lý thuyết cơ chế hoạt động của ứng dụng Chat LAN

## 1. Tổng quan về ứng dụng

Ứng dụng Chat LAN là một hệ thống giao tiếp thời gian thực dựa trên mô hình client-server, sử dụng giao thức TCP/IP để truyền tải tin nhắn giữa các client thông qua một máy chủ trung tâm. Ứng dụng bao gồm hai thành phần chính:

-   **Server**: Chạy trên một máy tính trong mạng LAN, chịu trách nhiệm quản lý kết nối và chuyển tiếp tin nhắn giữa các client.
-   **Client**: Ứng dụng giao diện đồ họa (GUI) được cài đặt trên máy người dùng, cho phép gửi và nhận tin nhắn.

Ứng dụng sử dụng thư viện socket của Python để xử lý kết nối mạng và threading để quản lý nhiều client đồng thời, cùng với tkinter để tạo giao diện người dùng phía client.

----------

## 2. Lý thuyết cơ chế hoạt động

### 2.1. Mô hình hoạt động

-   **Mô hình Client-Server**:
    -   Server lắng nghe các kết nối từ client trên một địa chỉ IP và cổng cố định (mặc định: 0.0.0.0:5555).
    -   Client kết nối đến server bằng địa chỉ IP của server trong mạng LAN và cổng tương ứng.
-   **Giao thức TCP**: Đảm bảo dữ liệu được truyền tải chính xác, không bị mất mát và theo thứ tự.
-   **Đa luồng (Multi-threading)**: Server sử dụng các luồng (threads) riêng biệt để xử lý từng client, cho phép nhiều người dùng chat đồng thời.

### 2.2. Cơ chế truyền tin

-   **Broadcast**: Khi một client gửi tin nhắn, server nhận tin nhắn và chuyển tiếp (broadcast) đến tất cả các client đang kết nối.
-   **Nickname**: Mỗi client được yêu cầu cung cấp một nickname duy nhất khi kết nối, giúp nhận diện người gửi trong nhóm chat.

### 2.3. Quản lý kết nối

-   Server duy trì danh sách các client (socket) và nickname tương ứng.
-   Khi client ngắt kết nối (do lỗi hoặc thoát), server tự động xóa client đó khỏi danh sách và thông báo cho các client còn lại.

----------

## 3. Các chức năng chính

### 3.1. Chức năng của Server

-   **Khởi động server**:
    -   Liên kết (bind) socket với địa chỉ IP và cổng.
    -   Lắng nghe kết nối từ client (tối đa 5 kết nối chờ).
-   **Quản lý client**:
    -   Chấp nhận kết nối từ client mới.
    -   Yêu cầu và lưu trữ nickname của client.
    -   Tạo luồng riêng để xử lý từng client.
-   **Chuyển tiếp tin nhắn**:
    -   Nhận tin nhắn từ một client và gửi đến tất cả client khác (broadcast).
-   **Hiển thị thông tin mạng**:
    -   In danh sách địa chỉ IP của máy chủ để client dễ dàng kết nối.
-   **Xử lý lỗi**:
    -   Đóng socket khi có lỗi hoặc khi server dừng.
    -   Xóa client khỏi danh sách khi mất kết nối.

### 3.2. Chức năng của Client

-   **Kết nối đến server**:
    -   Yêu cầu người dùng nhập nickname trước khi kết nối.
    -   Thiết lập kết nối TCP với server thông qua địa chỉ IP và cổng.
-   **Gửi tin nhắn**:
    -   Người dùng nhập tin nhắn vào ô nhập liệu và gửi đến server.
    -   Tin nhắn được định dạng: <nickname>: <nội dung tin nhắn>.
-   **Nhận tin nhắn**:
    -   Hiển thị tin nhắn từ server trong khu vực chat (scrolled text).
-   **Giao diện đồ họa (GUI)**:
    -   Cung cấp cửa sổ chat với khu vực hiển thị tin nhắn, ô nhập liệu và nút gửi.
    -   Hiển thị cửa sổ nhập nickname khi khởi động.
-   **Quản lý trạng thái**:
    -   Thông báo lỗi kết nối hoặc gửi tin nhắn thất bại.
    -   Đóng kết nối và thoát ứng dụng khi người dùng đóng cửa sổ.

----------

## 4. Luồng hoạt động chi tiết

### 4.1. Luồng hoạt động của Server

1.  **Khởi tạo Server**:
    -   Tạo đối tượng socket TCP (socket.socket(socket.AF_INET, socket.SOCK_STREAM)).
    -   Gắn socket với địa chỉ host (mặc định: 0.0.0.0) và port (mặc định: 5555).
    -   Bật tùy chọn SO_REUSEADDR để tái sử dụng cổng nếu server khởi động lại.
2.  **Khởi động Server**:
    -   Bắt đầu lắng nghe kết nối (listen(5)).
    -   Hiển thị các địa chỉ IP của máy chủ trong mạng LAN (trừ 127.0.0.1).
3.  **Chấp nhận kết nối từ Client**:
    -   Vòng lặp vô hạn (while True) để chấp nhận kết nối mới (accept()).
    -   Gửi yêu cầu nhập nickname ("NICK") đến client.
    -   Nhận nickname từ client và lưu vào danh sách nicknames và clients.
    -   Thông báo đến tất cả client rằng có người mới tham gia (broadcast).
    -   Tạo luồng xử lý riêng cho client (threading.Thread).
4.  **Xử lý tin nhắn từ Client**:
    -   Trong luồng riêng (handle_client):
        -   Nhận tin nhắn từ client (recv(1024)).
        -   Chuyển tiếp tin nhắn đến tất cả client khác (broadcast).
    -   Nếu xảy ra lỗi (mất kết nối):
        -   Xóa client khỏi danh sách.
        -   Thông báo client đã thoát.
5.  **Dừng Server**:
    -   Khi người dùng nhấn Ctrl+C hoặc xảy ra lỗi nghiêm trọng, đóng socket và thoát.

### 4.2. Luồng hoạt động của Client

1.  **Khởi tạo Client**:
    -   Tạo giao diện GUI bằng tkinter.
    -   Hiển thị cửa sổ nhập nickname trước khi kết nối.
2.  **Kết nối đến Server**:
    -   Người dùng nhập nickname và nhấn "Kết nối".
    -   Tạo socket TCP và kết nối đến server (connect((host, port))).
    -   Nếu kết nối thành công:
        -   Gửi nickname đến server.
        -   Tạo luồng nhận tin nhắn (receive).
    -   Nếu thất bại, hiển thị thông báo lỗi.
3.  **Gửi tin nhắn**:
    -   Người dùng nhập tin nhắn và nhấn nút "Gửi" hoặc phím Enter.
    -   Định dạng tin nhắn: <nickname>: <message>.
    -   Gửi tin nhắn qua socket (send()).
    -   Xóa nội dung ô nhập liệu sau khi gửi.
4.  **Nhận tin nhắn**:
    -   Trong luồng receive:
        -   Nhận dữ liệu từ server (recv(1024)).
        -   Nếu dữ liệu là "NICK", gửi nickname.
        -   Nếu là tin nhắn, hiển thị trong khu vực chat.
    -   Xử lý lỗi kết nối: hiển thị thông báo và dừng luồng.
5.  **Dừng Client**:
    -   Khi đóng cửa sổ, ngắt kết nối socket và thoát ứng dụng.

## 5. Lưu ý triển khai

-   **Server**: Cần chạy trước client và cung cấp địa chỉ IP chính xác trong mạng LAN.
-   **Client**: Thay đổi biến HOST trong client.py thành IP của server (ví dụ: 192.168.1.5 thay vì localhost).
-   **Cổng**: Đảm bảo cổng 5555 (hoặc cổng tùy chỉnh) không bị chặn bởi firewall.
