import socket
import threading


class Server:
    # Hàm __init__
    # Tác dụng: Khởi tạo đối tượng Server với các thuộc tính cơ bản.
    # Mục đích: Thiết lập socket, danh sách client và nickname để quản lý kết nối.
    def __init__(self, host="0.0.0.0", port=5555):
        self.host = host  # Địa chỉ IP mà server sẽ lắng nghe (0.0.0.0 nghĩa là tất cả giao diện mạng)
        self.port = port  # Cổng mà server sẽ sử dụng (mặc định: 5555)
        # Tạo socket TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Cho phép tái sử dụng cổng ngay sau khi đóng
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Danh sách lưu trữ các socket của client
        self.clients = []
        # Danh sách lưu trữ nickname của client
        self.nicknames = []

    # Hàm start
    # Tác dụng: Khởi động server và xử lý các kết nối từ client.
    # Mục đích: Liên kết socket với địa chỉ, lắng nghe kết nối và quản lý client mới.
    def start(self):
        try:
            # Liên kết socket với host và port
            self.server_socket.bind((self.host, self.port))
            # Lắng nghe tối đa 5 kết nối chờ
            self.server_socket.listen(5)
            # Thông báo server đã chạy
            print(f"Server đang chạy tại {self.host}:{self.port}")
            # Hướng dẫn người dùng
            print(
                f"IP của máy chủ trong mạng LAN: (các client sẽ kết nối đến địa chỉ này)"
            )

            # Hiển thị tất cả địa chỉ IP của máy chủ để dễ dàng cấu hình
            self.display_server_ips()

            # Vòng lặp vô hạn để chấp nhận kết nối mới
            while True:
                # Chấp nhận kết nối từ client, trả về socket và địa chỉ
                client, address = self.server_socket.accept()
                # Thông báo kết nối mới
                print(f"Kết nối mới từ {address}")

                # Gửi yêu cầu client cung cấp nickname
                client.send("NICK".encode("utf-8"))
                try:
                    # Nhận nickname từ client
                    nickname = client.recv(1024).decode("utf-8")
                    # Thêm nickname vào danh sách
                    self.nicknames.append(nickname)
                    # Thêm socket của client vào danh sách
                    self.clients.append(client)

                    # Thông báo nickname của client
                    print(f"Nickname của client là {nickname}")
                    # Thông báo đến tất cả client
                    self.broadcast(f"{nickname} đã tham gia chat!".encode("utf-8"))
                    # Gửi xác nhận đến client
                    client.send("Kết nối thành công!".encode("utf-8"))

                    # Tạo luồng xử lý client
                    thread = threading.Thread(target=self.handle_client, args=(client,))
                    # Đặt luồng là daemon để tự động dừng khi chương trình chính kết thúc
                    thread.daemon = True
                    # Bắt đầu luồng
                    thread.start()
                except Exception as e:
                    print(f"Lỗi khi xử lý client mới: {e}")
                    client.close()
        except Exception as e:
            print(f"Lỗi khởi động server: {e}")
            # Đóng socket server nếu lỗi
            self.server_socket.close()

    # Hàm display_server_ips
    # Tác dụng: Hiển thị tất cả địa chỉ IP của máy chủ trong mạng LAN.
    # Mục đích: Giúp người dùng biết địa chỉ IP để client kết nối.
    def display_server_ips(self):
        """Hiển thị tất cả các địa chỉ IP của máy chủ"""
        import socket

        try:
            # Lấy tên máy chủ
            hostname = socket.gethostname()
            # Lấy danh sách IP từ hostname
            ip_list = socket.gethostbyname_ex(hostname)[2]
            # Thông báo danh sách IP
            print("Các địa chỉ IP có thể kết nối:")
            # Duyệt qua từng IP
            for ip in ip_list:
                if ip != "127.0.0.1":  # Bỏ qua localhost
                    print(f"  - {ip}")
            print("---------------------------------------")
        except:
            print("Không thể xác định địa chỉ IP của máy chủ")

    # Hàm handle_client
    # Tác dụng: Xử lý tin nhắn từ một client cụ thể trong luồng riêng.
    # Mục đích: Nhận và chuyển tiếp tin nhắn, đồng thời xử lý khi client thoát.
    def handle_client(self, client):
        # Vòng lặp để nhận tin nhắn liên tục
        while True:
            try:
                # Nhận tin nhắn từ client (tối đa 1024 byte)
                message = client.recv(1024)
                if message:
                    # Chuyển tiếp tin nhắn đến tất cả client
                    self.broadcast(message)
            except:
                try:
                    # Tìm vị trí của client trong danh sách
                    index = self.clients.index(client)
                    # Xóa client khỏi danh sách
                    self.clients.remove(client)
                    # Đóng kết nối client
                    client.close()
                    # Lấy nickname tương ứng
                    nickname = self.nicknames[index]
                    # Thông báo client thoát
                    self.broadcast(f"{nickname} đã thoát khỏi chat!".encode("utf-8"))
                    # Xóa nickname khỏi danh sách
                    self.nicknames.remove(nickname)
                except:
                    pass
                break

    # Hàm broadcast
    # Tác dụng: Gửi tin nhắn đến tất cả client đang kết nối.
    # Mục đích: Đảm bảo mọi client đều nhận được thông báo hoặc tin nhắn.
    def broadcast(self, message):
        # Duyệt qua danh sách client
        for client in self.clients:
            try:
                # Gửi tin nhắn đến client
                client.send(message)
            except:
                # Bỏ qua lỗi nếu client không nhận được
                pass


# Khởi động server
if __name__ == "__main__":
    try:
        server = Server()
        server.start()
    except KeyboardInterrupt:
        print("Server đã dừng lại.")
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
