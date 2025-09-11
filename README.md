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
  - `VIRTUAL_HOST: web1.pucavv.io.vn` → để container `nginx-proxy` route hostname tới container này.
  - `VIRTUAL_PORT: 8888` -> để container `nginx-proxy` biết để route traffic tới port này.
  - `LETSENCRYPT_HOST: web1.pucavv.io.vn` → để container `acme-companion` request/renew cert cho host này.

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
- `image: nginxproxy/nginx-proxy:1.8-alpine`

  Chạy nginx cùng với docker-gen (tự động tạo file config dựa trên metada của Docker container)

- `container_name: nginx-proxy`

  Gắn tên cho container để `acme-companion` sử dụng tạo SSL.

- `restart: always`

  Nếu container crash, Docker tự động restart lại container đó.

- `ports:`
  - `"80:80"` và `"443:443"`
  
    Expose HTTP và HTTPS từ container ra tới host.

- `volumes:`
  - `proxy_certs:/etc/nginx/certs:ro`
  
    Mount cert được tạo bởi `acme_companion` vào `proxy_certs` với quyền read-only, Nginx sẽ đọc được cert này trong  `/etc/nginx/certs` của container `nginx-proxy`.

  - `proxy_html:/usr/share/nginx/html`

    Thư mục tĩnh cho challenge và default page của ACME HTTP-01.

  - `/var/run/docker.sock:/tmp/docker.sock:ro`

    Mount socket để `nginx-proxy` (thông qua `docker-gen`) đọc được các biến `env` và events của các container khác để tự động config routing.
    
    Cụ thể, khi `web1` khởi động, `nginx-proxy` đọc biến `env` (`VIRTUAL_HOST`, `VIRTUAL_PORT`) và tạo block Nginx server để proxy `web1.pucavv.io.vn` → `web1:8888`.

  - `networks: [proxy]`

    Đặt vào mạng `proxy` để có thể kết nối tới `web1`.

`acme-companion:` (Tự động Let's Encrypt bằng acme.sh)
- `image: nginxproxy/acme-companion:2.6.1`

  Image tự động khởi tạo/làm mới certs và thông báo cho `nginx-proxy` reload nếu có thay đổi.

- `restart: always`

  Nếu container crash, Docker tự động restart lại container đó.

- `environment:`
  - `DEFAUL_EMAIL: admin@pucavv.io.vn`

    Email dùng để đăng kí ACME account với Let's Encrypt.

  - `NGINX_PROXY_CONTAINER: nginx-proxy`

    Pointer tới `nginx-proxy` container để companion có thể xác định chỗ để viết cert và thông báo Nginx reload sau khi khởi tạo/làm mới cert.

  - `volumes:`

    - `proxy_certs:/etc/nginx/certs`
  
      Sử dụng cùng volume với `nginx-proxy` nhưng với quyển read-write để companion viết certs/keys.

  - `proxy_html:/usr/share/nginx/html`

    Cùng thư mục webroot cho HTTP-01 challenges để viết các file challenge vào đây.

  - `/var/run/docker.sock:/tmp/docker.sock:ro`

    Để phát hiện container chứa `LETSENCRYPT_HOST` và thông báo `nginx-proxy` reload.

    Cụ thể, `acme-companion` theo dõi container với `LETSENCRYPT_HOST`. Nó chứng minh quyền sở hữu của `web1.pucavv.io.vn` thông qua HTTP-01 (sử dụng thư mục tĩnh `proxy-html`), lấy cert từ Let's Encrypt, lưu ở `proxy-certs` và thông báo `nginx-proxy` reload. `nginx-proxy` lúc này có thể cung cấp HTTPS sử dụng cert được tạo ở volume dùng chung.

  - `acme:/etc/acme.sh`

    Lưu trạng thái của `acme.sh` (ACME account, metadata khởi tạo/làm mới). Không có cái này, thì mỗi lần tạo lại container sẽ phải khởi tạo lại cert mới → có thể bị rate limit bởi Let's Encrypt.

  - `depends_on:`
    - `- nginx-proxy` → khởi tạo sau `nginx-proxy`.
  - `networks: [proxy]`

    Đặt chung mạng với `nginx-proxy` để giao tiếp. 

`volumes:` (khai báo volume được quản lý bới Docker)
- `db_data:` → lưu trừ MySQL data.
- `proxy_certs` → thư mục cert/key dùng chung giữa `nginx-proxy` (ro) và `acme-companion` (rw).
- `proxy_html` → thử mục webroot dùng chung cho HTTP-01 challenges.
- `acme:` → lưu trạng thái `acme.sh`.

`networks:` (khai báo các bridged-networks)
- `proxy:` 
- `backend:` 

## 3) Chạy container chứa Flask app
```
git clone https://github.com/pucagit/sre_lesson2
cd sre_lesson2/web_1
docker compose up -d --build
```

Test truy cập:
```
curl https://web1.pucavv.io.vn

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

Tham khảo: https://github.com/nginx-proxy/acme-companion/wiki/Docker-Compose