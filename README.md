📘 Hướng Dẫn Thiết Lập Môi Trường Phân Tích Dữ Liệu (Spark & Cassandra)
Tài liệu này hướng dẫn chi tiết cách cài đặt môi trường để chạy dự án phân tích hành vi người dùng (Attentive Cursor Dataset) sử dụng PySpark, Cassandra (Docker) và Python 3.10 trên Windows.

📋 Mục lục
Yêu cầu hệ thống & Tải phần mềm

Cài đặt & Cấu hình Biến môi trường (Quan trọng)

Cài đặt Database Cassandra (Docker)

Thiết lập Môi trường Python

Dữ liệu dự án

1. Yêu cầu hệ thống & Tải phần mềm
Vui lòng tải xuống các thành phần sau (chưa cần cài đặt ngay, chỉ cần tải về):

A. Java Development Kit (JDK)
Spark yêu cầu Java để chạy.

Phiên bản: Java 11 (LTS)

Link tải: Adoptium Temurin OpenJDK 11

Lưu ý: Chọn file cài đặt .msi cho Windows (x64).

B. Apache Spark
Phiên bản: 3.5.1 (Pre-built for Hadoop 3.3)

Link tải: Huawei Cloud Repo - spark-3.5.1-bin-hadoop3.tgz

Lưu ý: File này tải về cần giải nén, không cần chạy cài đặt.

C. Hadoop Winutils (Cho Windows)
Windows cần file này để giả lập môi trường Hadoop.

Phiên bản: Hadoop 3.3.6

Link tải: Winutils GitHub (winutils.exe)

Cần tải thêm: hadoop.dll (cùng thư mục trong link trên nếu có, hoặc tìm trong repo đó).

D. Python
Phiên bản: 3.10.x

Link tải: Python 3.10.11 Download

2. Cài đặt & Cấu hình Biến môi trường (Quan trọng)
Đây là bước quan trọng nhất, nếu làm sai Spark sẽ không chạy.

Bước 2.1: Cài đặt Java
Chạy file cài đặt JDK 11 đã tải.

Ghi nhớ đường dẫn cài đặt (Ví dụ: C:\Program Files\Eclipse Adoptium\jdk-11.0.18.10-hotspot).

Bước 2.2: Giải nén Spark
Giải nén file spark-3.5.1-bin-hadoop3.tgz (dùng WinRAR hoặc 7-Zip).

Di chuyển thư mục đã giải nén ra ổ đĩa gốc để tên ngắn gọn.

Ví dụ: D:\Spark\spark-3.5.1-bin-hadoop3

Bước 2.3: Cài đặt Winutils (Hadoop Home)
Tạo thư mục: D:\Hadoop

Trong thư mục đó, tạo tiếp thư mục bin -> D:\Hadoop\bin

Copy file winutils.exe (và hadoop.dll nếu có) vào thư mục D:\Hadoop\bin.

Bước 2.4: Cấu hình Environment Variables
Mở Edit the system environment variables trên Windows -> Bấm Environment Variables.

Tạo các biến mới (System Variables - Phần bên dưới):

JAVA_HOME: C:\Program Files\Eclipse Adoptium\jdk-11... (đường dẫn cài Java).

HADOOP_HOME: D:\Hadoop (Thư mục chứa folder bin).

SPARK_HOME: D:\Spark\spark-3.5.1-bin-hadoop3

Cập nhật biến PATH:

Tìm biến Path trong System Variables -> Bấm Edit.

Thêm mới (New) các dòng sau:

%JAVA_HOME%\bin

%HADOOP_HOME%\bin

%SPARK_HOME%\bin

3. Cài đặt Database Cassandra (Docker)
Sử dụng Docker để chạy Cassandra server nhanh chóng.

Mở CMD hoặc PowerShell.

Tải ảnh (Image):

Bash

docker pull cassandra:4.1
Chạy Container:

Bash

docker run --name cass-node -d -p 9042:9042 cassandra:4.1
Kiểm tra:

Bash

docker ps
(Nếu thấy trạng thái Up là thành công).

(Tùy chọn) Truy cập dòng lệnh CQLSH:

Bash

docker exec -it cass-node cqlsh
Gõ exit để thoát.

4. Thiết lập Môi trường Python
Sử dụng venv để quản lý thư viện, tránh xung đột với hệ thống.

Bước 4.1: Tạo Virtual Environment
Mở PowerShell tại thư mục dự án của bạn (Ví dụ: C:\Users\acer\MyProject):

PowerShell

# Kiểm tra phiên bản Python 3.10
py -3.10 --version

# Tạo môi trường ảo tên là 'cassandra_env'
py -3.10 -m venv cassandra_env
Bước 4.2: Kích hoạt môi trường
PowerShell

# Windows PowerShell
cassandra_env\Scripts\activate
Sau khi chạy, bạn sẽ thấy (cassandra_env) ở đầu dòng lệnh.

Bước 4.3: Cài đặt thư viện
Copy và chạy lệnh sau để cài đặt toàn bộ thư viện cần thiết:

PowerShell

pip install pyspark cassandra-driver pandas matplotlib seaborn numpy
5. Dữ liệu dự án
Dataset
Tải bộ dữ liệu The Attentive Cursor Dataset tại link sau:

GitLab: The Attentive Cursor Dataset

Cấu trúc thư mục dự án (Gợi ý)
Sau khi hoàn tất, thư mục dự án của bạn nên trông như sau để dễ quản lý:

Plaintext

MyProject/
├── cassandra_env/          # Môi trường ảo Python
├── data/                   # Chứa dữ liệu tải từ GitLab
│   └── cursor_data.csv
├── src/                    # Chứa code Python
│   └── analysis.py
└── README.md
Chạy thử Code
Trong file Python (src/analysis.py), đoạn code đầu tiên cần có để kiểm tra kết nối:

Python

import os
from pyspark.sql import SparkSession

# Test Spark
spark = SparkSession.builder \
    .appName("TestSetup") \
    .master("local[*]") \
    .getOrCreate()

print("Spark Version:", spark.version)
print("Environment Setup Successful!")