from pyspark.sql import SparkSession
from pyspark.sql.functions import explode

spark = SparkSession.builder \
    .appName("hl7_process") \
    .getOrCreate()

parquet_file_path = r"udemy_dsa\src\milliman\output_patients.parquet"

df = spark.read.parquet(parquet_file_path)

df.printSchema()

df_exploded = df.withColumn("Address", explode(df.Addresses)) \
                .withColumn("Telecom", explode(df.Telecoms))

df_exploded.show(5, False)

spark.stop()
