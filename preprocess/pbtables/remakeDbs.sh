rm -rf pbtables
rmrf pbtables.db

ij import-derby.sql
sqlite3 pbtables.db < import-sqlite3.sql
