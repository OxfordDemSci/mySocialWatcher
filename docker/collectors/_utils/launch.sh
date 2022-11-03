cd /app

echo "----------" >> data/launch.log
echo "[`date '+%F %T %Z'`] Collections launched." >> data/launch.log

for file in specs/specs*.json
do

  echo "[`date '+%F %T %Z'`] ${file}..." >> data/launch.log
  python3 utils/kill.py
  python3 main.py $file

done

echo "[`date '+%F %T %Z'`] Finished." >> data/launch.log
