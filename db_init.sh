rm -f data.db
sqlite3 data.db "CREATE TABLE cards (id INTEGER, question TEXT, answer TEXT, level INTEGER, time_created REAL, last_reviewed REAL);"
sqlite3 data.db "CREATE TABLE metadata (key TEXT, value TEXT)"
sqlite3 data.db "INSERT INTO metadata VALUES ('next_id', 0)"
echo "Done."
