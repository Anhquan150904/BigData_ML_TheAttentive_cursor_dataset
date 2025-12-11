# --- 1. Thư viện hệ thống và xử lý file ---
import os  # Tương tác với hệ điều hành (quản lý đường dẫn, biến môi trường...)
# --- 3. PySpark: Machine Learning (ML) ---
from pyspark.ml import Pipeline  # Tạo chuỗi quy trình xử lý (workflow) tự động
# Các thuật toán phân loại (Classification Models)
from pyspark.ml.classification import (GBTClassifier,        # Gradient Boosted Tree
                                       LogisticRegression,   # Hồi quy Logistic
                                       RandomForestClassifier) # Rừng ngẫu nhiên

# Đánh giá mô hình
from pyspark.ml.evaluation import BinaryClassificationEvaluator # Đánh giá phân loại nhị phân (Đúng/Sai)

# Xử lý đặc trưng (Feature Engineering)
from pyspark.ml.feature import StandardScaler, StringIndexer, VectorAssembler
# StandardScaler: Chuẩn hóa dữ liệu (về cùng thang đo)
# StringIndexer: Chuyển biến phân loại dạng chữ sang số
# VectorAssembler: Gom các cột đặc trưng (feature) thành một vector duy nhất để đưa vào mô hình
from pyspark.ml.functions import vector_to_array # Chuyển đổi cột vector thành mảng
# Tinh chỉnh tham số (Tuning)
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder 
# CrossValidator: Kiểm định chéo để tránh overfitting
# ParamGridBuilder: Tạo lưới tham số để tìm bộ tham số tốt nhất
from pyspark.sql import SparkSession # Điểm khởi đầu để tạo ứng dụng Spark
from pyspark.sql.functions import * # Import tất cả hàm xử lý dữ liệu có sẵn
from pyspark.sql.functions import col # col: chọn cột, udf: hàm tự định nghĩa
from pyspark.sql.types import DoubleType   # Định nghĩa kiểu dữ liệu số thực
from pyspark.sql.window import Window      # Dùng cho các hàm cửa sổ trượt (rolling, ranking)



# Cấu hình Cassandra
CASSANDRA_HOST = "127.0.0.1"
KEYSPACE = "attentive"                     # tương đương với "Database" trong SQL (chứa các bảng).
TABLE = "cursor_events"                    # tên bảng dữ liệu 


OUTPUT_DIR = "D:/Workspace/DDL/output_analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)


PYTHON_EXECUTABLE = r"C:\Users\acer\cassandra_env\Scripts\python.exe" 

spark = (
    SparkSession.builder
    .appName("Attentive Cursor - Advanced ML")
    .master("local[*]")
    .config("spark.cassandra.connection.host", CASSANDRA_HOST)
    .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.4.0")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")
print("Spark khởi động thành công")



# đọc dữ liệu từ cassandra
df = spark.read.format("org.apache.spark.sql.cassandra") \
    .options(table=TABLE, keyspace=KEYSPACE).load()

# loại bỏ các cột không cần thiết - tập trung vào dữ liệu hành vi chuột
df = df.drop('country', 'education', 'age', 'income', 'gender', 'serp_id', 'query')

# Làm sạch dữ liệu
# bỏ các cột có trạng thái click quảng cáo là null
# bỏ tọa độ xpos - ypos quá lớn và tọa độ (0, 0) và các giá trị thiếu của tọa độ (điền 0 vào cột thiếu)
# chuyển cột attention sang kiểu int và timestamp sang kiểu long
# 
df_clean = df.filter(col("ad_clicked").isNotNull()) \
    .filter((col("xpos") < 5000) & (col("ypos") < 5000)) \
    .filter(~((col("xpos") == 0) & (col("ypos") == 0))) \
    .na.fill(0, subset=['xpos', 'ypos', 'attention']) \
    .withColumn("attention_int", col("attention").cast("int")) \
    .withColumn("timestamp_sec", col("timestamp").cast("long"))

print(f"Tổng số bản ghi sau làm sạch: {df_clean.count():,}")

# tạo features 
print("Bắt đầu tạo features...")

window_session = Window.partitionBy("log_id", "user_id").orderBy("timestamp_sec")

df_feat = df_clean \
    .withColumn("hour", hour("timestamp")) \
    .withColumn("is_night", when(col("hour").between(0, 6), 1).otherwise(0)) \
    .withColumn("speed_x", abs(col("xpos") - lag("xpos", 1).over(window_session))) \
    .withColumn("speed_y", abs(col("ypos") - lag("ypos", 1).over(window_session))) \
    .withColumn("distance", sqrt(col("speed_x")**2 + col("speed_y")**2)) \
    .withColumn("acceleration", col("distance") - lag("distance", 1).over(window_session)) \
    .withColumn("jerk", col("acceleration") - lag("acceleration", 1).over(window_session)) \
    .withColumn("time_diff", col("timestamp_sec") - lag("timestamp_sec", 1).over(window_session)) \
    .withColumn("velocity", when(col("time_diff") > 0, col("distance") / col("time_diff")).otherwise(0))

# Group by log_id + user_id để tạo session-level features
session_features = df_feat.groupBy("log_id", "user_id").agg(
    # Cơ bản
    count("*").alias("total_events"),
    avg("attention_int").alias("avg_attention"),
    stddev("attention_int").alias("std_attention"),
    max("attention_int").alias("max_attention"),
    
    # Hành vi di chuyển
    avg("distance").alias("avg_distance_per_move"),
    max("distance").alias("max_jump"),
    avg("velocity").alias("avg_speed"),
    stddev("velocity").alias("speed_variation"),
    avg("jerk").alias("avg_jerk"),
    
    # Thời gian & nhịp độ
    (max("timestamp_sec") - min("timestamp_sec")).alias("session_duration"),
    avg("time_diff").alias("avg_time_between_events"),
    
    # Tương tác
    sum(when(col("event").like("%click%"), 1).otherwise(0)).alias("total_clicks_any"),
    sum(when(col("event").like("%hover%"), 1).otherwise(0)).alias("total_hovers"),
    
    # Vị trí & vùng nóng
    avg("xpos").alias("avg_x"),
    avg("ypos").alias("avg_y"),
    stddev("xpos").alias("std_x"),
    stddev("ypos").alias("std_y"),
    
    # Giờ + hành vi theo thời gian
    avg("is_night").alias("night_session_ratio"),
    sum(when(col("hour").between(18, 23), 1).otherwise(0)).alias("evening_events"),
    
    # Meta
    first("ad_category").alias("ad_category"),
    first("ad_position").alias("ad_position"),
    
    # TARGET
    max("ad_clicked").alias("label_ad_clicked")
).na.fill(0)

# Xử lý class imbalance
total = session_features.count()
pos = session_features.filter(col("label_ad_clicked") == 1).count()
neg = total - pos
weight_ratio = neg / pos

session_features = session_features.withColumn("class_weight",
    when(col("label_ad_clicked") == 1, weight_ratio).otherwise(1.0)
)

print(f"Class distribution: Click = {pos:,} | No Click = {neg:,} | Ratio = {weight_ratio:.2f}")


# chuẩn bị PIPELINE
# Index các cột categorical
indexers = [
    StringIndexer(inputCol="ad_category", outputCol="cat_idx", handleInvalid="keep"),
    StringIndexer(inputCol="ad_position", outputCol="pos_idx", handleInvalid="keep")
]

# Các feature số
num_cols = [
    "total_events", "avg_attention", "std_attention", "max_attention",
    "avg_distance_per_move", "max_jump", "avg_speed", "speed_variation", "avg_jerk",
    "session_duration", "avg_time_between_events", "total_clicks_any", "total_hovers",
    "avg_x", "avg_y", "std_x", "std_y", "night_session_ratio", "evening_events"
]

feature_cols = [c + "_idx" if c in ["ad_category", "ad_position"] else c for c in ["ad_category", "ad_position"] + num_cols]

assembler = VectorAssembler(inputCols=num_cols + ["cat_idx", "pos_idx"], outputCol="raw_features")
scaler = StandardScaler(inputCol="raw_features", outputCol="features", withStd=True, withMean=True)

# Chia dữ liệu
train, test = session_features.randomSplit([0.75, 0.25], seed=42)

# Evaluator
evaluator = BinaryClassificationEvaluator(
    labelCol="label_ad_clicked",
    rawPredictionCol="probability",
    metricName="areaUnderROC"
)

# huấn luyện với 3 mô hình khác nhau 
best_auc = 0.0
best_model = None
best_name = ""

models = {}

# 1. Logistic Regression + Tuning
lr = LogisticRegression(labelCol="label_ad_clicked", featuresCol="features", weightCol="class_weight", maxIter=30)
pipeline_lr = Pipeline(stages=indexers + [assembler, scaler, lr])

paramGrid_lr = ParamGridBuilder() \
    .addGrid(lr.regParam, [0.01, 0.1]) \
    .addGrid(lr.elasticNetParam, [0.0, 0.5]) \
    .build()

cv_lr = CrossValidator(estimator=pipeline_lr, estimatorParamMaps=paramGrid_lr, evaluator=evaluator, numFolds=3, seed=42)
model_lr = cv_lr.fit(train)
auc_lr = evaluator.evaluate(model_lr.transform(test))
print(f"Logistic Regression + Tuning → AUC: {auc_lr:.4f}")
models["LR"] = (model_lr, auc_lr)

# 2. Random Forest
rf = RandomForestClassifier(labelCol="label_ad_clicked", featuresCol="features", numTrees=100, maxDepth=10, seed=42)
pipeline_rf = Pipeline(stages=indexers + [assembler, scaler, rf])
model_rf = pipeline_rf.fit(train)
auc_rf = evaluator.evaluate(model_rf.transform(test))
print(f"Random Forest → AUC: {auc_rf:.4f}")
models["RF"] = (model_rf, auc_rf)

# 3. GBT (GBTClassifier trên Spark)
gbt = GBTClassifier(labelCol="label_ad_clicked", featuresCol="features", maxIter=100, maxDepth=8, seed=42)
pipeline_gbt = Pipeline(stages=indexers + [assembler, scaler, gbt])
model_gbt = pipeline_gbt.fit(train)
auc_gbt = evaluator.evaluate(model_gbt.transform(test))
print(f"GBT → AUC: {auc_gbt:.4f}")
models["GBT"] = (model_gbt, auc_gbt)

# Chọn mô hình tốt nhất
for name, (model, auc) in models.items():
    if auc > best_auc:
        best_auc = auc
        best_model = model
        best_name = name

print(f"\nMÔ HÌNH TỐT NHẤT: {best_name} | AUC = {best_auc:.4f}")


def save_to_csv(df, filename):
    try:
        path = os.path.join(OUTPUT_DIR, filename)
        df.toPandas().to_csv(path, index=False)
        print(f"Đã lưu {filename}")
    except Exception as e:
        print(f"Lỗi khi lưu {filename}: {e}")

# Dự đoán chi tiết (Trích xuất xác suất)
final_pred = best_model.transform(test) \
    .withColumn("prob_click", vector_to_array(col("probability"))[1])

df_pred_output = final_pred.select("log_id", "user_id", "label_ad_clicked", "prediction", "prob_click")
save_to_csv(df_pred_output, "out_ml_predictions.csv")

# Các file thống kê khác
save_to_csv(
    df_clean.groupBy("ad_clicked").agg(avg("attention_int").alias("avg_attention"), count("*").alias("count")), 
    "out_click_attention.csv"
)

save_to_csv(
    df_clean.groupBy("ad_position").agg(avg("attention_int").alias("avg_attention"), count("*").alias("count")), 
    "out_attention_position.csv"
)

save_to_csv(
    df_clean.withColumn("hour", hour("timestamp")).groupBy("hour").count().orderBy("hour"), 
    "out_activity_hour.csv"
)

save_to_csv(
    df_clean.withColumn("x_group", (col("xpos")/10).cast("int")*10)
            .withColumn("y_group", (col("ypos")/10).cast("int")*10)
            .groupBy("x_group", "y_group").count().orderBy(desc("count")), 
    "out_cursor_density.csv"
)

spark.stop()
