# Metashape scripts

สคริปต์ในโฟลเดอร์นี้ต้องรันจาก Agisoft Metashape Professional ผ่าน
`Tools > Run Script` หรือ Python Console ไม่ใช่ Python ทั่วไป

## `05.py`

ใช้กับกรณีพื้นที่มีแต่น้ำหรือ texture ต่ำมาก โดยทำงานดังนี้:

1. หาเฉพาะกล้อง Green band จากชื่อ sensor/camera/file
2. ใช้ตำแหน่ง RTK แบ่งภาพเป็นแนวบินด้วย PCA
3. สร้างคู่ภาพกับภาพข้างเคียงในแนวเดียวกัน
4. Match Photos และ Align Cameras ทีละแนวบิน
5. ลอง align ภาพ Green ที่ยังเหลืออีกครั้ง

> [!CAUTION]
> สคริปต์ตั้ง `camera.transform = None` ให้กล้องทุกตัวก่อนเริ่ม จึงล้าง alignment
> เดิมทั้งหมด ควรบันทึกสำเนา `.psx` ก่อนรัน และอย่ารันใน chunk ที่ต้องการรักษา
> alignment เดิม

ค่าที่มักปรับ:

- `NEIGHBOR_COUNT` — จำนวนภาพถัดไปในแนวบินที่นำมาจับคู่
- `DOWNSCALE` — `1` = High, `2` = Medium
- `STRIP_TOLERANCE_FACTOR` — tolerance ในการแยกแนวบิน
- `MIN_CAMERAS_PER_STRIP` — จำนวนภาพขั้นต่ำต่อแนวบิน

## `force_camera_position.py`

สร้าง `camera.transform` ให้กล้อง Regular ที่ยังไม่ align โดยใช้ตำแหน่งและมุม
Yaw/Pitch/Roll ใน Reference pane กล้องที่ align แล้วหรือไม่มี reference data จะถูกข้าม

ข้อสมมติที่ต้องตรวจ:

- `chunk.euler_angles` เป็น `Yaw/Pitch/Roll`
- มีทั้ง `camera.reference.location` และ `camera.reference.rotation`
- ไม่มี antenna offset ที่ต้องนำมาคำนวณเพิ่ม
- CRS และ vertical datum ถูกต้อง

เริ่มทดสอบกับกล้อง 1–2 ตัวโดยกำหนด `TARGET_LABELS` ก่อนใช้กับทุกภาพ
