# 📘 Hướng Dẫn Thiết Lập Môi Trường Phân Tích Dữ Liệu (Spark & Cassandra)

Tài liệu này hướng dẫn chi tiết cách thiết lập môi trường để chạy dự án phân tích hành vi người dùng (Attentive Cursor Dataset) sử dụng **PySpark**, **Cassandra (Docker)** và **Python 3.10** trên Windows.

---

## 📋 Mục lục

1. [Yêu cầu hệ thống & Tải phần mềm](#1-yêu-cầu-hệ-thống--tải-phần-mềm)
2. [Cài đặt & Cấu hình biến môi trường](#2-cài-đặt--cấu-hình-biến-môi-trường-quan-trọng)
3. [Cài đặt Database Cassandra bằng Docker](#3-cài-đặt-database-cassandra-docker)
4. [Thiết lập môi trường Python](#4-thiết-lập-môi-trường-python)
5. [Dữ liệu dự án](#5-dữ-liệu-dự-án)
6. [Chạy thử Spark](#️⃣-chạy-thử-code)

---

## 1. Yêu cầu hệ thống & Tải phần mềm

Vui lòng tải các thành phần sau (chưa cần cài đặt ngay):

### **A. Java Development Kit (JDK)**

* Phiên bản: **OpenJDK 11 (LTS)**
* Link: *https://adoptium.net/fr/temurin/releases?version=11&os=any&arch=any*
* Chọn file **.msi**, hệ điều hành **Windows x64**.

### **B. Apache Spark**

* Phiên bản: **Spark 3.5.1** (Pre-built for Hadoop 3.3)
* Link: *https://repo.huaweicloud.com/apache/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz*
* Lưu ý: File tải về chỉ cần **giải nén**, không cần cài đặt.

### **C. Hadoop Winutils (Windows Only)**

* Phiên bản: **Hadoop 3.3.6**
* Tải từ repo Winutils: *https://github.com/cdarlint/winutils/blob/master/hadoop-3.3.6/bin/winutils.exe*
* (Nếu có) tải thêm **hadoop.dll** (đặt cùng thư mục bin).

### **D. Python**

* Phiên bản: **Python 3.10.x**

---

## 2. Cài đặt & Cấu hình Biến môi trường (Quan trọng)

Nếu làm sai bước này, Spark sẽ không chạy.

### **Bước 2.1: Cài đặt Java**

* Chạy file cài JDK 11.
* Ghi lại đường dẫn cài đặt, ví dụ:

  ```
  C:\Program Files\Eclipse Adoptium\jdk-11.0.x
  ```

### **Bước 2.2: Giải nén Spark**

* Giải nén file Spark.
* Đặt vào thư mục gọn gàng, ví dụ:

  ```
  D:\Spark\spark-3.5.1-bin-hadoop3
  ```

### **Bước 2.3: Cài Winutils (Hadoop Home)**

1. Tạo thư mục:

   ```
   D:\Hadoop
   ```
2. Tạo tiếp:

   ```
   D:\Hadoop\bin
   ```
3. Copy **winutils.exe** (và hadoop.dll nếu có) vào thư mục `bin`.

### **Bước 2.4: Cấu hình Environment Variables**

Mở: **Edit the system environment variables** → **Environment Variables**.

#### **Tạo System Variables mới**:

| Variable    | Value                                      |
| ----------- | ------------------------------------------ |
| JAVA_HOME   | C:\Program Files\Eclipse Adoptium\jdk-11.x |
| HADOOP_HOME | D:\Hadoop                                  |
| SPARK_HOME  | D:\Spark\spark-3.5.1-bin-hadoop3           |

#### **Cập nhật PATH**:

Thêm 3 dòng sau:

```
%JAVA_HOME%\bin
%HADOOP_HOME%\bin
%SPARK_HOME%\bin
```

---

## 3. Cài đặt Database Cassandra (Docker)

### **Kéo image Cassandra**

```bash
docker pull cassandra:4.1
```

### **Chạy container**

```bash
docker run --name cass-node -d -p 9042:9042 cassandra:4.1
```

### **Kiểm tra container**

```bash
docker ps
```

Nếu thấy trạng thái **Up**, nghĩa là Cassandra đã chạy.

### **(Tùy chọn) Mở CQLSH**

```bash
docker exec -it cass-node cqlsh
```

Thoát:

```
exit
```

---

## 4. Thiết lập Môi trường Python

### **Bước 4.1: Tạo môi trường ảo**

Mở PowerShell tại thư mục dự án:

```powershell
py -3.10 --version
py -3.10 -m venv cassandra_env
```

### **Bước 4.2: Kích hoạt môi trường ảo**

```powershell
cassandra_env\Scripts\activate
```

### **Bước 4.3: Cài đặt thư viện Python**

```powershell
pip install pyspark cassandra-driver pandas matplotlib seaborn numpy
```

---

## 5. Dữ liệu dự án

Dataset: **The Attentive Cursor Dataset** (GitLab).

---

## #️⃣ Chạy thử code

Tạo file `src/analysis.py` và chạy thử Spark:

```python
import os
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("TestSetup") \
    .master("local[*]") \
    .getOrCreate()

print("Spark Version:", spark.version)
print("Environment Setup Successful!")
```

---

💡 **Nếu thấy in ra phiên bản Spark → bạn đã setup thành công 100%!**
