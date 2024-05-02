cd /app
echo "----------" >> data/launch.log
echo "[`date '+%F %T %Z'`] Collections launched." >> data/launch.log
python3 main.py
echo "[`date '+%F %T %Z'`] Finished." >> data/launch.log
