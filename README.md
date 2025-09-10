# Triển khai 2 Flask app với Gunicorn + Nginx + HTTPS + Giới hạn IP

## Mục tiêu

* `web1.pucavv.io.vn` → app **web\_1**
* `web2.pucavv.io.vn` → app **web\_2** (chỉ cho phép truy cập từ IP chỉ định)
* Chạy Gunicorn dưới systemd, Nginx reverse proxy qua **Unix socket**, cài Let’s Encrypt (HTTPS).

---

## 0) Chuẩn bị

1.  **Packages**
  ```
  sudo apt update
  sudo apt install -y nginx certbot python3-certbot-nginx
  ```
2. **Setup docker**
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
  sudo apt install docker-compose-plugin
  ```
- Thêm user để chạy docker:
  ```
  sudo groupadd docker   # ignore if exists
  sudo usermod -aG docker $USER
  ```
3. **Chạy 2 container `web` và `db`**
  ```
  git pull https://github.com/pucagit/sre_lesson2
  cd sre_lesson2/web_1
  docker compose up -d --build
  ```

---

## 1) Cấu hình Nginx (2 server blocks)

### web1.pucavv.io.vn → web_1

`/etc/nginx/sites-available/web_1`

```nginx
server {
    listen 80;
    server_name web1.pucavv.io.vn;

    location / {
        include proxy_params;
        proxy_pass http://localhost:8888;
        proxy_read_timeout 120s;
    }
}
```

Bật site & reload:

```
sudo ln -sf /etc/nginx/sites-available/web_1/etc/nginx/sites-enabled/web_1
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

---

## 4) Bật HTTPS (Let’s Encrypt)
**Cấp cert cho cả 2 domain cùng lúc:**

```
sudo certbot --nginx -d web1.pucavv.io.vn --redirect
```

---
