# การแก้ปัญหา

## `No Green cameras detected`

ตรวจชื่อ sensor, camera label และชื่อไฟล์ ต้องมีคำว่า `green`, `_MS_G` หรือ `MS_G.`
ถ้ารูปแบบชื่อไม่ตรง ให้ปรับฟังก์ชัน `is_green_camera()` ใน `Py/05.py`

## `Green with RTK` น้อยกว่าที่คาด

ตรวจว่า import reference สำเร็จ ชื่อใน CSV ตรงกับ camera label และเลือก CRS ถูกต้อง
กล้องต้องมี `camera.reference.location`

## ตรวจไม่พบแนวบินหรือแบ่งแนวบินผิด

- ตรวจพิกัดสลับ Longitude/Latitude
- ตรวจ outliers ใน PPK
- ปรับ `STRIP_TOLERANCE_FACTOR` ทีละน้อย
- ปรับ `MIN_CAMERAS_PER_STRIP` ให้เหมาะกับจำนวนภาพจริง
- PCA อาจเลือกแกนผิดเมื่อรูปทรงแผนบินกว้างกว่ายาวหรือมีหลายทิศบิน ควรแบ่ง chunk
  ตามชุดแนวบินก่อนรัน

## กล้องถูก force แล้วหันผิดทิศ

หยุดและ Undo จากนั้นตรวจ:

- convention ของมุมเป็น Yaw/Pitch/Roll จริงหรือไม่
- หน่วยมุมเป็นองศา
- orientation จากกิมบอลหรือจากลำตัวโดรน
- antenna/lever-arm offset ใน Camera Calibration
- CRS และ vertical datum

## Orthomosaic มีช่องว่างบนผิวน้ำ

ตรวจว่า DEM ครอบคลุม Region และกล้องทุกตัวมี transform หาก tie points บนน้ำไม่
เสถียร ให้ใช้ DEM ภายนอกที่มีระดับผิวน้ำน่าเชื่อถือแทนการเพิ่ม keypoint limit อย่างเดียว

## ภาพซ้อน รอยต่อ หรือคลื่นผิดรูป

ผิวน้ำไม่ใช่วัตถุคงที่ระหว่างการถ่ายภาพ จึงไม่ควรตีความรายละเอียดคลื่นว่าเป็นตำแหน่ง
จริงเสมอไป ตรวจ seamlines และเลือกภาพต้นทางที่เหมาะสม หรือกำหนดขอบเขตส่งมอบให้
สอดคล้องกับคุณภาพข้อมูล
