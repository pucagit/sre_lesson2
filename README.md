# Containerize Flask website + MySQL + Gunicorn + Nginx-proxy + Acme-companion (for enabling HTTPS) using docker-compose

## 0) Chuẩn bị
**Cấu hình DNS**

Cấu hình bản ghi A cho domain web1.pucavv.io.vn tương ứng với public IP của EC2. Nhớ cài Security Group của EC2 cho phép inbound HTTP/HTTPS traffic từ mọi nơi.

**Setup docker**
  ```
  sudo apt update
  sudo apt install -y ca-certificates curl gnupg lsb-release
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg

  echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  sudo apt update
  sudo apt install -y docker-compose-plugin docker.io
  ```
**Thêm user để chạy docker**
  ```
  sudo groupadd docker   # ignore if exists
  sudo usermod -aG docker $USER
  ```

## 1) Cấu hình Dockerfile (dùng cho container `web1`)
- `FROM python:3.11-slim` → Khởi tạo base image với Python 3.11.
- `WORKDIR /app` → Đặt thư mục default cho mọi thao tác, nếu không có Docker sẽ tạo nó.
- `RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*` → Update danh sách package, upgrade các package đã tải, dọn `apt` cache metadata và dọn dẹp thử mục list.
-  `COPY requirements.txt .` → Copy file chứa dependency vào Docker trước (sau này khi build lại docker, phần này sẽ được cache và bỏ qua, chỉ chạy lại nếu có sự thay đổi).
-  `RUN pip install --no-cache-dir -r requirements.txt` → Tải các dependency trong file `requirements.txt`
-  `COPY . .` → Copy tất cả code vào `/app`.
-  `EXPOSE 8888` → Thông báo container đang nghe trên port 8888 (chỉ thông báo, không expose).
-  `CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8888", "app:app"]` → Command mặc định khi chạy container:
   -  `gunicorn` → WSGI server cho app Python.
   -  `-w 4` → 4 tiến trình worker.
   -  `-b 0.0.0.0:8888` → chạy trên mọi interface ở cổng 8888 để container khác có thể truy cập được.
   -  `app:app` → `module:callable` (ví dụ file app.py với WSGI `app` object)


## 2) Cấu hình các service bằng docker-compose.yaml
`db:` (MySQL database container)
- `image: mysql:8`
  
  Pin sẵn version để tránh bị update xong gây lỗi không tương thích.

- `restart: always`

  Nếu container crash, Docker tự động restart lại container đó.

- `environment:`

  Các biến MySQL cần ở lần boot đầu tiên:
  - `MYSQL_ROOT_PASSWORD: root` → mật khẩu cho tài khoản root.
  - `MYSQL_DATABASE: web1_db` → tạo database `web1_db`.
  - `MYSQL_USER: web1_user` → tạo user cho app...
  - `MYSQL_PASSWORD: web1_password` → ...với mật khẩu này.

- `volumes:`

  - `db_data:/var/lib/mysql`

    Lưu data của MySQL trên volume `db_data` để không bị mất dữ liệu khi build lại container.

- `networks: [backend]`

  Đặt MySQL trên mạng private `backend`. Chỉ những service trên mạng này mới có thể kết nối tới.

`web1:` (Python app chạy bằng Gunicorn)
- `build: .`

  Sử dụng file Dockerfile trong cùng thư mục đề build image.

- `restart: always`

  Nếu container crash, Docker tự động restart lại container đó.

- `environment:`

  - `DB_HOST: db` → hostname để Docker DNS trỏ tới đúng `db` container.
  - `DB_USER/DB_PASSWORD/DB_NAME` → tương ứng với các biến khai báo ở MySQL để kết nối tới database.

- `expose:`

  - `8888`

    Quảng bá port 8888 cho các container khác, cụ thể để `nginx-proxy` dùng.

- `depends_on:`

  - `- db`

    Khởi tạo container `db` trước `web1` (chỉ là thứ tự khởi tạo, không phải đợi đến khi khởi tạo xong `db` mới khởi tạo `web1`)

- `networks: [backend, proxy]`
  
  Gắn vào 2 mạng private:
  - `backend` để kết nối tới `db`
  - `proxy` để `nginx-proxy` có thể kết nối tới

`nginx-proxy:` (reverse proxy) 
- `build: ./nginx`

  Build container từ Dockerfile trong thư mục `./nginx`.

- `container_name: nginx-proxy`

  Gắn tên cho container để `acme-companion` sử dụng tạo SSL.

- `restart: always`

  Nếu container crash, Docker tự động restart lại container đó.

- `ports:`
  - `"80:80"` và `"443:443"`
  
    Expose HTTP và HTTPS từ container ra tới host.

- `volumes:`
  - `certbot:/etc/letsencrypt`

    Mount volume `cerbot` vào thư mục `/etc/letsencrypt` trong container để lưu trữ thông tin cert được cấp bởi Let's Encrypt (không phải cấp mới cert mỗi khi build lại container). 

  - `./nginx:/etc/nginx`

    Bind mount thư mục `./nginx` vào thư mục `/etc/nginx` trong container để áp dụng cấu hình nginx ở host vào trong container.

- `networks: [proxy]`

  Đặt vào mạng `proxy` để có thể kết nối tới `web1`.

`volumes:` (khai báo volume được quản lý bới Docker)
- `db_data:` → lưu trữ MySQL data.
- `certbot` → lưu trữ cert/key để sử dụng HTTPS.
  
`networks:` (khai báo các bridged-networks)
- `proxy:` 
- `backend:` 

## 3) Chạy container chứa Flask app
```
git clone https://github.com/pucagit/sre_lesson2
cd sre_lesson2/web_3
docker compose up -d --build
```

Test truy cập:
```
curl https://web3.pucavv.io.vn

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
  </head>
  <body>
    <title>Hello from Flask</title>
    <h1>Bạn là lượt truy cập thứ 1.</h1>
  </body>
</html>
```
---

Tham khảo: 
- https://nginx.org/en/docs/example.html
- https://viblo.asia/p/tai-sao-nen-chay-ung-dung-container-voi-non-root-user-jvEla3VNKkw