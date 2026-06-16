import duckdb

con = duckdb.connect('./props/dev.duckdb')

print("Tablas en la base de datos:")
con.sql("SHOW TABLES").show()

# 2. Ver la estructura de una tabla
print("\nEstructura de la tabla:")
con.sql("SUMMARIZE staging_props").show()

print("\nContenido de la tabla:")
con.sql("SELECT * FROM staging_props").show()