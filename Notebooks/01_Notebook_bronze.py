# Databricks notebook source
from pyspark.sql.types import StructType, StructField, StringType

# COMMAND ----------

schema = StructType([

    StructField("data", StringType(), True),

    StructField("descricao", StringType(), True),

    StructField("valor_str", StringType(), True),

])

# COMMAND ----------

df_bronze = spark.read.csv(
    "/Volumes/gastos_prj/bronze/raw/GastoAgosto.csv",
    schema=schema,
    header=True
)

display(df_bronze)

# COMMAND ----------

df_bronze.write.mode("overwrite").saveAsTable("gastos_prj.bronze.transacoes")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM gastos_prj.bronze.transacoes LIMIT 10