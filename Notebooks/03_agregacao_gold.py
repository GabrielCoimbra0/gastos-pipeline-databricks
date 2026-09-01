# Databricks notebook source
df_silver = spark.read.table("gastos_prj.silver.transacoes")

# COMMAND ----------

from pyspark.sql.functions import sum as spark_sum

df_resumo = df_silver.groupBy("tipo_transacao").agg(
    spark_sum("valor").alias("total")
)

display(df_resumo)

# COMMAND ----------

df_resumo.write.mode("overwrite").saveAsTable("gastos_prj.gold.resumo_por_tipo")

# COMMAND ----------

df_resumo.write.mode("overwrite").saveAsTable("gastos_prj.gold.resumo_por_tipo")