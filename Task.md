# Bài tập số 2

# Đặc tả yêu cầu

## Yêu cầu kiến thức

- Làm quen với Docker và khái niệm ảo hóa, hiểu rõ các level ảo hóa, lợi thế của docker với VM
- Biết được cấu trúc của Dockerfile và docker-compose.yml

## Yêu cầu kỹ năng

- Sử dụng nhuần nhuyễn các câu lệnh docker phổ biến: docker ps, docker images, docker logs, docker build, docker exec…
- Viết được Dockerfile và docker-compose.yml hoàn chỉnh để đóng gói toàn bộ một hệ thống có ít nhất 2 service

# Đề bài

## Yêu cầu đề bài

1. Từ ứng dụng web thứ nhất ở tuần 1, viết Dockerfile đóng gói ứng dụng web. Container cố gắng không chạy dưới quyền root
2. Viết file docker-compose.yml để chạy đồng thời cả web service và database service, sau đó port mapping web service ra máy thật.
3. Config Nginx vẫn giữ nguyên

## Thời gian làm bài: 7 ngày

## Yêu cầu bài làm

- Đối với project:
    - Sau khi hoàn thành bài tập, sử dụng 1 câu lệnh **docker-compose up** để chạy ứng dụng, kết quả cuối cùng y hệt như cách chạy truyền thống
    - Push bài tập lên Gitlab, sử dụng Git Terminal **(không sử dụng Git Desktop)**

## Yêu cầu và hướng dẫn nộp bài

- Sử dụng Gitlab để lưu trữ bài tập
    - Tạo 1 private group trên [Gitlab](https://gitlab.com/) có tên `cs_<your_name>`, chẳng hạn `cs_nguyen_huu_trung`
    - Nếu tên group bị trùng thì thêm một chữ số theo thứ tự Alphabet phía sau, chẳng hạn `cs_nguyen_huu_trung_1`
    - Nếu group đã được tạo trước đó thì không cần tạo lại
    - Thêm member cho group: [@trungngh](https://www.notion.so/trungngh), @dangvu99 với role `Reporter`
    - Tạo 1 private project bên trong private group vừa được tạo, có tên `devops_week2`
    - Download [GIT client](https://git-scm.com/downloads/guis) và sử dụng nó để push kết quả bải tập lên Gitlab
    
- Thông báo hoàn thành bài tập và trao đổi với người hướng dẫn Vũ Hải Đăng theo địa chỉ email `dangvh@cystack.net`, CC cho anh **Nguyễn Hữu Trung** theo địa chỉ `trungnh@cystack.net` với tiêu đề là `HomeworkDevopsX-<Hoten>` (X là số thứ tự của tuần). Phần nội dung thư không để trống, có ghi một số thông tin vắn tắt liên quan. Ví dụ:

```
Chào anh,

Em là xxx, 
    
Bài tập tuần X đã được em push lên gitlab tại địa chỉ https://gitlab.com/cs_nguyen_huu_trung/weekX/
    
Rất mong nhận được sự phản hồi từ anh.
    
Em cảm ơn.
```

## Lưu ý

- Bài bị phát hiện copy từ người khác, không hiểu nội dung thì TTS sẽ chịu hình thức kỷ luật ở mức cao nhất.
- Mọi nguồn tham khảo đều phải được ghi chú rõ ràng trong báo cáo
- Bài nộp không theo chuẩn nêu trên sẽ không được công nhận.

# Tài liệu tham khảo

## Liên quan trực tiếp tới nội dung chính

### Lý thuyết

- [Docker](https://www.youtube.com/watch?v=3c-iBn73dDE)
- [Docker compose](https://docs.docker.com/compose/)

### Kỹ năng

- [Docker compose](https://docs.docker.com/compose/)

## Tham khảo thêm

- DM cho người hướng dẫn @Dang Vu