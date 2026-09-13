# Metashape scripts

สคริปต์ในโฟลเดอร์นี้ต้องรันจาก Agisoft Metashape Professional ผ่าน
`Tools > Run Script` หรือ Python Console ไม่ใช่ Python ทั่วไป

## `align_water_sequential_flightlines.py`

ใช้กับกรณีพื้นที่มีแต่น้ำหรือ texture ต่ำมาก โดยทำงานดังนี้:

1. เลือกกล้องที่เปิดใช้งาน มีไฟล์ภาพ และมี reference location
2. ใช้ระยะห่างระหว่างกล้องที่อยู่ติดกันในลำดับของ chunk เพื่อหา spacing ปกติ
3. แบ่งแนวบินเมื่อระยะระหว่างกล้องต่อเนื่องมากกว่าค่ามัธยฐาน 2.5 เท่า
4. สร้างคู่ภาพกับภาพถัดไปไม่เกิน `NEIGHBOR` ภาพภายในแนวเดียวกัน
5. Match Photos แล้ว Align Cameras ทีละแนวบิน

> [!CAUTION]
> สคริปต์ตั้ง `camera.transform = None` ให้กล้องทุกตัวก่อนเริ่ม จึงล้าง alignment
> เดิมทั้งหมด ควรบันทึกสำเนา `.psx` ก่อนรัน และอย่ารันใน chunk ที่ต้องการรักษา
> alignment เดิม

> [!IMPORTANT]
> วิธีนี้ถือว่าลำดับ `chunk.cameras` เป็นลำดับการถ่ายจริง และช่วงเปลี่ยนแนวบินมี
> ระยะกระโดดชัดเจน หากภาพถูกเรียงตามชื่อ/แบนด์ในรูปแบบอื่นหรือแต่ละสถานีมีกล้อง
> หลายแบนด์ที่พิกัดเกือบซ้ำกัน ต้องตรวจรายงาน flight lines ก่อนเชื่อถือผล

ค่าที่มักปรับ:

- `NEIGHBOR` — จำนวนภาพถัดไปในแนวบินที่นำมาจับคู่
- `DOWNSCALE` — `0` = Highest, `1` = High, `2` = Medium
- `KEYPOINT_LIMIT` — จำนวน key points สูงสุด
- `LINE_BREAK_DISTANCE` — สคริปต์คำนวณจาก median spacing × 2.5

## `force_camera_position.py`

สร้าง `camera.transform` ให้กล้อง Regular ที่ยังไม่ align โดยใช้ตำแหน่งและมุม
Yaw/Pitch/Roll ใน Reference pane กล้องที่ align แล้วหรือไม่มี reference data จะถูกข้าม

ข้อสมมติที่ต้องตรวจ:

- `chunk.euler_angles` เป็น `Yaw/Pitch/Roll`
- มีทั้ง `camera.reference.location` และ `camera.reference.rotation`
- ไม่มี antenna offset ที่ต้องนำมาคำนวณเพิ่ม
- CRS และ vertical datum ถูกต้อง

เริ่มทดสอบกับกล้อง 1–2 ตัวโดยกำหนด `TARGET_LABELS` ก่อนใช้กับทุกภาพ
