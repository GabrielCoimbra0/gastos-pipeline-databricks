# Databricks notebook source
df_bronze = spark.read.table("gastos_prj.bronze.transacoes")

display(df_bronze)

# COMMAND ----------

df_silver = df_bronze.withColumn(
    "descricao",
    regexp_replace(col("descricao"), '^"|"$', '')  # remove aspas no início e no fim
)

df_silver = df_silver.withColumn(
    "descricao",
    regexp_replace(col("descricao"), '""', '"')  # transforma aspas duplas em uma só
)

# COMMAND ----------

from pyspark.sql.functions import when, col

df_silver = df_silver.withColumn(
    "tipo_transacao",
    when(col("descricao").startswith("IOF de volta de"), "estorno_imposto")
    .when(col("descricao").startswith("IOF de"), "imposto")
    .otherwise("compra")
)

display(df_silver)

# COMMAND ----------

from pyspark.sql.functions import regexp_replace, col

df_silver = df_silver.withColumn(
    "valor_str_limpo",
    regexp_replace(col("valor_str"), " ", "")  # remove espaço
)

df_silver = df_silver.withColumn(
    "valor_str_limpo",
    regexp_replace(col("valor_str_limpo"), "\\.", "")  # remove ponto de milhar
)

df_silver = df_silver.withColumn(
    "valor_str_limpo",
    regexp_replace(col("valor_str_limpo"), ",", ".")  # troca vírgula decimal por ponto
)

display(df_silver)

# COMMAND ----------

from pyspark.sql.types import DecimalType

df_silver = df_silver.withColumn(
    "valor",
    col("valor_str_limpo").cast(DecimalType(10, 2))
)

display(df_silver)

# COMMAND ----------

df_silver_final = df_silver.select("data", "descricao", "tipo_transacao", "valor")

display(df_silver_final)

# COMMAND ----------

df_silver_final.write.mode("overwrite").saveAsTable("gastos_prj.silver.transacoes")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM gastos_prj.silver.transacoes LIMIT 10