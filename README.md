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

### 📂 The Attentive Cursor Dataset

Bộ dữ liệu bao gồm các bản ghi theo dõi chuyển động chuột được thu thập từ một nghiên cứu crowdsourcing nhằm đo lường **mức độ chú ý của người dùng đối với quảng cáo web**.

---

### 🎯 **1. Mouse Tracking Log Files**

Thư mục `logs/` chứa toàn bộ file log được ghi bởi phần mềm **evtrack**.

Bao gồm:

* File CSV kiểu **space-delimited**, mỗi file có 8 cột:

| Cột       | Kiểu dữ liệu | Mô tả                                                       |
| --------- | ------------ | ----------------------------------------------------------- |
| cursor    | int          | Luôn bằng 0 (tất cả người tham gia dùng chuột máy tính)     |
| timestamp | int          | Thời gian (ms) của sự kiện                                  |
| xpos      | float        | Vị trí X của chuột                                          |
| ypos      | float        | Vị trí Y của chuột                                          |
| event     | string       | Tên sự kiện của trình duyệt (mousemove, click, load, …)     |
| xpath     | string       | Đường dẫn XPath của phần tử HTML liên quan đến sự kiện      |
| attrs     | string       | Thuộc tính của phần tử (nếu có)                             |
| extras    | string       | JSON khoảng cách Euclidean tới các điểm chuẩn của quảng cáo |

📌 Với các sự kiện không liên quan chuột (ví dụ: *load, blur*), `xpos` và `ypos` = **0**.

Ví dụ Dòng CSV:

```
cursor timestamp xpos ypos event xpath attrs extras
0 1405503114382 0 0 load / {}
```

Ngoài ra có các file **XML metadata** chứa thông tin thiết bị và trình duyệt (viewport, user agent, kích thước màn hình...).

Ví dụ file XML:

```xml
<data>
 <date>Tue, 02 Oct 2018 03:31:26 +0200</date>
 <ua>Mozilla/5.0 (Windows NT 10.0; WOW64; rv:62.0)</ua>
 <screen>1366x768</screen>
 <window>1366x632</window>
 <document>1349x2064</document>
 <task>5npsk114ba8hfbj4jr3lt8jhf5-dd-top_left</task>
</data>
```

---

### 🏷️ **2. Ground-truth labels**

File **groundtruth.tsv** (tab-delimited) chứa nhãn:

| Cột        | Ý nghĩa                                       |
| ---------- | --------------------------------------------- |
| user_id    | ID người dùng                                 |
| ad_clicked | 1 nếu người dùng click quảng cáo, 0 nếu không |
| attention  | Điểm chú ý tự báo cáo (1–5)                   |
| log_id     | ID log chuột tương ứng                        |

Ví dụ:

```
user_id    ad_clicked  attention  log_id
5npsk...   0           4          20181002033126
```

---

### 👤 **3. Thông tin nhân khẩu học & thông tin kích thích (stimuli)**

File **participants.tsv** gồm 12 cột về thông tin người dùng và loại quảng cáo được hiển thị.

Các trường chính:

* `country`: Quốc gia (ISO‑3)
* `education`: Bậc học (1–6)
* `age`: Nhóm tuổi (1–9)
* `income`: Nhóm thu nhập (1–8)
* `gender`: Giới tính
* `ad_position`: Vị trí quảng cáo
* `ad_type`: Loại quảng cáo
* `ad_category`: Danh mục quảng cáo
* `serp_id`: ID trang SERP
* `query`: Từ khóa tìm kiếm

📌 Giá trị thiếu được ghi bằng **NA**.

Bảng mã hóa bins:

| Bin | Education   | Age   | Income   |
| --- | ----------- | ----- | -------- |
| 1   | High school | 18–23 | 25K      |
| 2   | College     | 24–29 | 25–34K   |
| 3   | Bachelor's  | 30–35 | 35–49K   |
| 4   | Graduate    | 36–41 | 50–74K   |
| 5   | Master's    | 42–47 | 75–99K   |
| 6   | Doctorate   | 48–53 | 100–149K |
| 7   | —           | 54–59 | 150–249K |
| 8   | —           | 60–65 | 250K+    |
| 9   | —           | 66+   | —        |

Ví dụ:

```
user_id country education age income gender ad_position ad_type ad_category serp_id query log_id
5npsk... PHL 3 3 1 male top-left dd Computers & Electronics tablets tablets 20181002033126
```

---

### 🌐 **4. Stimulus pages (SERP HTML)**

Thư mục `serps/` chứa snapshot HTML của trang tìm kiếm tương ứng với mỗi quảng cáo.
Tên file = `serp_id`.

---

### 📚 **5. Trích dẫn khoa học**

Nếu sử dụng bộ dữ liệu này, hãy trích dẫn:

```
Luis A. Leiva, Ioannis Arapakis. (2020) The Attentive Cursor Dataset.
Front. Hum. Neurosci. 14.
DOI: 10.3389/fnhum.2020.565664
```

---

### 📄 **6. Các bài báo liên quan**

Bộ dữ liệu được sử dụng trong các nghiên cứu sau:

* *A Price-per-attention Auction Scheme Using Mouse Cursor Information* (2020)
* *Learning Efficient Representations of Mouse Movements to Predict User Attention* (SIGIR 2020)
* *My Mouse, My Rules: Privacy Issues of Behavioral User Profiling via Mouse Tracking* (CHIIR 2021)
* *When Choice Happens: Mouse Movement Length and Decision Making in Web Search* (SIGIR 2021)

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
