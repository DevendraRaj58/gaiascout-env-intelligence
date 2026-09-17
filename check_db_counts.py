import sqlite3
conn = sqlite3.connect('data/gaiaScout.db')
c = conn.cursor()
tables = ['metric_thresholds', 'ecosystem_interventions', 'biome_profiles', 'study_refs']
for table in tables:
    c.execute(f"SELECT COUNT(*) FROM {table}")
    count = c.fetchone()[0]
    print(f"{table}: {count} rows")
conn.close()