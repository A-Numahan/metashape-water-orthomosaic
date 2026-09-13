# คู่มือประมวลผล Orthomosaic พื้นที่น้ำ

## 1. เตรียมโครงการร่วมกันทั้งสองกรณี

1. สร้าง project/chunk ใหม่และเพิ่มภาพ โดยตรวจว่าภาพ multispectral ถูกจัดกลุ่ม
   ถูกต้องตามวิธีนำเข้าของ DJI Mavic 3 Multispectral
2. ตั้ง Coordinate Reference System ให้ตรงกับข้อมูล PPK และผลลัพธ์ที่ต้องการ
3. นำเข้าพิกัดจาก Reference pane ให้ label ตรงกับชื่อกล้อง รวม extension หาก camera
   label ในโครงการมี extension
4. ตรวจค่าตำแหน่งและมุมจาก EXIF/PPK โดยเปิดใช้งาน location และ rotation ที่ต้องใช้
5. ตั้ง Camera Accuracy ตามรายงาน PPK เช่น `0.02 m` แนวราบและ `0.05 m` แนวดิ่ง
6. บันทึก project เป็น checkpoint ก่อนเริ่ม align

อย่าสรุปว่า `Elevation` ใน CSV เป็นระดับพื้นหรือระดับน้ำ ค่านี้เป็นตำแหน่งกล้อง
และอาจอ้างอิง ellipsoidal height หรือ orthometric height ตามกระบวนการ PPK

## 2. กรณีที่ 1 — มีชายฝั่งหรือวัตถุให้จับคู่

เหมาะเมื่อภาพมีพื้นดิน อาคาร พืช ทุ่น หรือรายละเอียดคงที่ซึ่งปรากฏซ้ำระหว่างภาพ

1. ใช้ `Workflow > Align Photos`
   - เริ่มจาก High accuracy ตามทรัพยากรเครื่อง
   - ใช้ Generic preselection และ Reference preselection เมื่อพิกัดน่าเชื่อถือ
   - ตรวจ tie points ว่าอยู่บนวัตถุคงที่ ไม่กระจุกบนคลื่นหรือแสงสะท้อน
2. ตรวจจำนวน aligned/unaligned cameras และ camera error
3. รัน `Py/force_camera_position.py` เฉพาะภาพที่ไม่ align
   - ตั้ง `TARGET_LABELS` เพื่อทดลอง 1–2 กล้องก่อน
   - ตรวจทิศการมองใน Model view เทียบกับกล้องข้างเคียง
4. ปรับ Region ให้ครอบคลุมพื้นที่ต้องการและมีระยะเผื่อรอบขอบงาน
5. สร้าง Depth Maps และ Point Cloud หากยังไม่มีแหล่งข้อมูลระดับความสูงที่เหมาะสม
6. Build DEM จากแหล่งข้อมูลที่ตรวจแล้ว
   - ลบ/กรองจุดผิดปกติจากผิวน้ำก่อน
   - ตรวจช่องว่างและค่าระดับที่กระโดดผิดจริง
7. Build Orthomosaic โดยเลือก DEM ที่สร้างขึ้นเป็น surface
8. ตรวจขอบเขต ช่องว่าง seamline ภาพซ้ำ และ ghosting ก่อน export GeoTIFF

ถ้า DEM ภายในมีช่องว่างกว้างบนผิวน้ำ ให้เปลี่ยนไปใช้ DEM ภายนอกตามกรณีที่ 2
แทนการ interpolate แบบไม่มีข้อมูลควบคุม

## 3. กรณีที่ 2 — มีแต่น้ำหรือ texture ต่ำมาก

เหมาะเมื่อ standard alignment ไม่สามารถสร้างเครือข่าย tie points ที่เสถียรได้

1. ตรวจว่าภาพ Green band มี RTK location และชื่อมี `Green`, `_MS_G` หรือ `MS_G.`
2. บันทึกสำเนา project เพราะ `Py/05.py` ล้าง alignment เดิมทั้งหมด
3. รัน `Py/05.py`
   - สคริปต์ประมาณทิศบินและแบ่งแนวบินจากตำแหน่ง RTK
   - จับคู่เฉพาะภาพข้างเคียงในแนวเดียวกัน
   - align Green band ทีละแนวและรายงานจำนวน tracks/aligned cameras
4. ตรวจว่า flight lines ที่รายงานตรงกับแผนบินจริง หากไม่ตรงให้หยุดและปรับค่า
   clustering ก่อนดำเนินการต่อ
5. รัน `Py/force_camera_position.py` สำหรับกล้องที่ยังไม่มี transform
6. ปรับ Region ให้ครอบคลุมทุก footprint ที่ต้องการ รวมขอบเผื่อเล็กน้อย
7. สร้าง DEM ภายนอก
   - ใช้ระดับผิวน้ำจากงานสำรวจ เกจวัดระดับ แบบจำลองภูมิประเทศ หรือข้อมูลอื่นที่
     อ้างอิง datum ชัดเจน
   - ถ้าสมมติผิวน้ำราบ ให้สร้าง raster ระดับคงที่ใน projected CRS
   - ห้ามใช้ระดับความสูงกล้องจาก CSV เป็นค่าระดับน้ำ
   - raster ต้องครอบคลุม Region ทั้งหมดและมี NoData/ความละเอียดที่เหมาะสม
8. นำ DEM เข้า Metashape ผ่านคำสั่ง Import DEM และตรวจตำแหน่ง/ระดับใน Ortho view
9. Build Orthomosaic โดยเลือก DEM ที่นำเข้าเป็น surface
10. ตรวจ coverage และ positional consistency กับแนวชายฝั่ง จุดควบคุม หรือข้อมูล GIS

## 4. Quality control ก่อนส่งมอบ

- รายงานจำนวนกล้องทั้งหมด กล้องที่ align จริง และกล้องที่ถูก force transform
- แยกผล bundle-adjusted ออกจากผลที่พึ่ง GPS/INS เท่านั้น
- ตรวจ RMSE ด้วย check points อิสระเมื่อมี
- ตรวจ CRS ทั้งแนวราบและ vertical datum
- ตรวจขอบเขต orthomosaic ว่าครบตามพื้นที่เป้าหมาย
- ตรวจรอยต่อ สีสะท้อน คลื่น เรือ และวัตถุเคลื่อนที่
- เก็บ processing report ของ Metashape พร้อมค่าพารามิเตอร์และเวอร์ชันซอฟต์แวร์
