import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Entry, Button, END, messagebox


class Client:
    # Hàm __init__
    # Tác dụng: Khởi tạo đối tượng Client với các thuộc tính cơ bản.
    # Mục đích: Thiết lập thông tin kết nối và giao diện GUI.
    def __init__(self, host, port):
        # Địa chỉ IP của server
        self.host = host
        # Cổng của server
        self.port = port
        # Nickname của client (ban đầu rỗng)
        self.nickname = ""
        # Trạng thái GUI đã hoàn thành khởi tạo chưa
        self.gui_done = False
        # Trạng thái ứng dụng đang chạy
        self.running = True

        # Khởi tạo GUI trước
        # Gọi hàm khởi tạo giao diện GUI
        self.gui_loop()

    # Hàm connect_to_server
    # Tác dụng: Kết nối client đến server.
    # Mục đích: Thiết lập socket TCP và bắt đầu luồng nhận tin nhắn.
    def connect_to_server(self):
        try:
            # Tạo socket TCP
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Kết nối đến server
            self.sock.connect((self.host, self.port))

            # Bắt đầu thread nhận tin nhắn sau khi đã kết nối thành công
            # Tạo luồng nhận tin nhắn
            receive_thread = threading.Thread(target=self.receive)
            # Đặt luồng là daemon
            receive_thread.daemon = (
                True  # Thread sẽ tự động kết thúc khi chương trình chính kết thúc
            )
            # Bắt đầu luồng
            receive_thread.start()

            return True
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến server: {e}")
            return False

    # Hàm gui_loop
    # Tác dụng: Tạo và chạy giao diện đồ họa chính.
    # Mục đích: Cung cấp cửa sổ chat để người dùng tương tác.
    def gui_loop(self):
        # Tạo cửa sổ chính
        self.win = tk.Tk()
        # Đặt tiêu đề
        self.win.title("Ứng dụng Chat LAN")
        # Đặt màu nền
        self.win.configure(bg="lightgray")
        # Không cho phép thay đổi kích thước
        self.win.resizable(False, False)

        # Nhãn "Chat"
        self.chat_label = tk.Label(self.win, text="Chat:", bg="lightgray")
        # Đặt vị trí nhãn
        self.chat_label.grid(row=0, column=0, sticky="W", padx=5, pady=5)

        # Khu vực hiển thị tin nhắn
        self.text_area = scrolledtext.ScrolledText(self.win, width=50, height=15)
        # Đặt vị trí khu vực chat
        self.text_area.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        # Vô hiệu hóa chỉnh sửa trực tiếp
        self.text_area.config(state="disabled")

        # Nhãn "Tin nhắn"
        self.msg_label = tk.Label(self.win, text="Tin nhắn:", bg="lightgray")
        # Đặt vị trí nhãn
        self.msg_label.grid(row=2, column=0, sticky="W", padx=5, pady=5)

        # Ô nhập tin nhắn
        self.input_area = Entry(self.win, width=40)
        # Đặt vị trí ô nhập
        self.input_area.grid(row=3, column=0, padx=5, pady=5)

        # Nút gửi tin nhắn
        self.send_button = Button(self.win, text="Gửi", command=self.write)
        # Đặt vị trí nút
        self.send_button.grid(row=3, column=1, padx=5, pady=5, sticky="W")

        # Gọi hàm stop khi đóng cửa sổ
        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        # Đánh dấu GUI đã hoàn thành
        self.gui_done = True

        # Cập nhật nickname và kết nối server
        # Hiển thị cửa sổ nhập nickname
        self.show_nickname_window()

        # Chạy vòng lặp chính của GUI
        self.win.mainloop()

    # Hàm show_nickname_window
    # Tác dụng: Hiển thị cửa sổ nhập nickname trước khi kết nối.
    # Mục đích: Thu thập nickname từ người dùng và bắt đầu kết nối.
    def show_nickname_window(self):
        # Tạo cửa sổ con
        nickname_window = tk.Toplevel(self.win)
        # Đặt tiêu đề
        nickname_window.title("Kết nối")
        # Đặt kích thước
        nickname_window.geometry("300x150")
        # Không cho thay đổi kích thước
        nickname_window.resizable(False, False)

        # Đặt ở giữa màn hình
        # Cập nhật trạng thái cửa sổ
        nickname_window.update_idletasks()
        # Lấy chiều rộng
        width = nickname_window.winfo_width()
        # Lấy chiều cao
        height = nickname_window.winfo_height()
        # Tính tọa độ x
        x = (nickname_window.winfo_screenwidth() // 2) - (width // 2)
        # Tính tọa độ y
        y = (nickname_window.winfo_screenheight() // 2) - (height // 2)
        # Đặt vị trí
        nickname_window.geometry("{}x{}+{}+{}".format(width, height, x, y))

        # Nhãn hướng dẫn
        nickname_label = tk.Label(nickname_window, text="Nhập nickname của bạn:")
        # Đặt nhãn
        nickname_label.pack(pady=5)

        # Ô nhập nickname
        nickname_entry = Entry(nickname_window, width=30)
        # Đặt ô nhập
        nickname_entry.pack(pady=5)
        # Đặt con trỏ vào ô nhập
        nickname_entry.focus()

        # Nhãn trạng thái
        status_label = tk.Label(nickname_window, text="", fg="red")
        # Đặt nhãn trạng thái
        status_label.pack(pady=5)

        # Hàm xử lý khi nhấn nút "Kết nối"
        def set_nickname():
            # Lấy nickname và xóa khoảng trắng
            nickname = nickname_entry.get().strip()
            # Kiểm tra nếu nickname rỗng
            if not nickname:
                status_label.config(text="Vui lòng nhập nickname")
                return

            # Lưu nickname
            self.nickname = nickname

            # Kết nối đến server
            status_label.config(text="Đang kết nối...", fg="blue")
            # Cập nhật giao diện
            nickname_window.update()

            # Thử kết nối đến server
            if self.connect_to_server():
                # Gửi nickname đến server sau khi kết nối thành công
                try:
                    self.sock.send(self.nickname.encode("utf-8"))
                    nickname_window.destroy()
                except Exception as e:
                    status_label.config(text=f"Lỗi: {e}", fg="red")
            else:
                status_label.config(text="Không thể kết nối đến server", fg="red")

        # Nút kết nối
        nickname_button = Button(nickname_window, text="Kết nối", command=set_nickname)
        # Đặt nút
        nickname_button.pack(pady=5)

        # Bind Enter key
        # Gán phím Enter để kết nối
        nickname_entry.bind("<Return>", lambda event: set_nickname())

        # Đặt cửa sổ con phụ thuộc cửa sổ chính
        nickname_window.transient(self.win)
        # Tập trung vào cửa sổ con
        nickname_window.grab_set()

    # Hàm write
    # Tác dụng: Gửi tin nhắn từ người dùng đến server.
    # Mục đích: Xử lý sự kiện khi người dùng nhấn nút "Gửi".
    def write(self):
        # Lấy nội dung tin nhắn từ ô nhập
        message = self.input_area.get()
        # Kiểm tra tin nhắn không rỗng và socket tồn tại
        if message and hasattr(self, "sock"):
            try:
                # Định dạng tin nhắn
                full_message = f"{self.nickname}: {message}"
                # Gửi tin nhắn đến server
                self.sock.send(full_message.encode("utf-8"))
                # Xóa ô nhập sau khi gửi
                self.input_area.delete(0, END)
            except:
                # Cho phép chỉnh sửa khu vực chat
                self.text_area.config(state="normal")
                # Thêm thông báo lỗi
                self.text_area.insert(END, "Lỗi kết nối! Không thể gửi tin nhắn.\n")
                # Cuộn xuống cuối
                self.text_area.yview(END)
                # Vô hiệu hóa chỉnh sửa
                self.text_area.config(state="disabled")

    # Hàm stop
    # Tác dụng: Dừng ứng dụng khi đóng cửa sổ.
    # Mục đích: Đảm bảo thoát sạch sẽ và đóng kết nối.
    def stop(self):
        # Đặt trạng thái dừng
        self.running = False
        # Kiểm tra socket tồn tại
        if hasattr(self, "sock"):
            try:
                # Đóng socket
                self.sock.close()
            except:
                # Bỏ qua lỗi nếu không đóng được
                pass
        # Đóng cửa sổ GUI
        self.win.destroy()
        # Thoát chương trình
        exit(0)

    # Hàm receive
    # Tác dụng: Nhận tin nhắn từ server trong luồng riêng.
    # Mục đích: Hiển thị tin nhắn hoặc xử lý yêu cầu từ server.
    def receive(self):
        # Vòng lặp chạy khi ứng dụng còn hoạt động
        while self.running:
            try:
                # Nhận tin nhắn từ server
                message = self.sock.recv(1024).decode("utf-8")
                # Nếu server yêu cầu nickname
                if message == "NICK":
                    # Gửi nickname
                    self.sock.send(self.nickname.encode("utf-8"))
                else:
                    # Nếu GUI đã sẵn sàng
                    if self.gui_done:
                        # Cho phép chỉnh sửa khu vực chat
                        self.text_area.config(state="normal")
                        # Thêm tin nhắn vào khu vực chat
                        self.text_area.insert(END, message + "\n")
                        # Cuộn xuống cuối
                        self.text_area.yview(END)
                        # Vô hiệu hóa chỉnh sửa
                        self.text_area.config(state="disabled")
            except ConnectionAbortedError:
                # Thoát nếu kết nối bị ngắt
                break
            except Exception as e:
                # Nếu ứng dụng còn chạy
                if self.running:
                    # Cho phép chỉnh sửa
                    self.text_area.config(state="normal")
                    self.text_area.insert(END, f"Lỗi kết nối: {e}\n")
                    # Cuộn xuống cuối
                    self.text_area.yview(END)
                    # Vô hiệu hóa chỉnh sửa
                    self.text_area.config(state="disabled")
                # Thoát vòng lặp nếu có lỗi
                break


# Chạy client
if __name__ == "__main__":
    # Thay đổi host thành địa chỉ IP của máy chủ trong mạng LAN
    # Ví dụ: '192.168.1.5'
    HOST = "localhost"  # Thay đổi thành IP của máy chủ khi chạy thực tế
    PORT = 5555

    client = Client(HOST, PORT)
