# รูปแบบข้อมูลตำแหน่งอ้างอิง

## CSV ที่มีอยู่

```text
image_name,camera_band,Longitude,Latitude,Elevation
DJI_..._D.JPG,RGB,98.93993468,7.853135269,141.26119
DJI_..._MS_G.TIF,Green,98.9399348118,7.8531354409,141.2703240
```

การ map ในหน้าต่าง Import CSV ของ Metashape:

| CSV | Metashape |
|---|---|
| `image_name` | Label |
| `Longitude` | Longitude/X |
| `Latitude` | Latitude/Y |
| `Elevation` | Altitude/Z |
| `camera_band` | ไม่ต้องนำเข้าเป็นพิกัด |

เลือก CRS ตามกระบวนการ PPK จริง ไฟล์ GeoPackage ที่มีอยู่ระบุ EPSG:4326 สำหรับ
พิกัดแนวราบ แต่ EPSG:4326 เพียงอย่างเดียวไม่ได้ยืนยัน vertical datum ของ Elevation

## ข้อมูล rotation ที่จำเป็นต่อสคริปต์ force

`force_camera_position.py` ต้องมีทั้ง location และ rotation ใน Reference pane
ไฟล์ CSV ที่มีอยู่ไม่มีคอลัมน์ Yaw/Pitch/Roll ดังนั้น rotation ต้องมาจาก metadata
ของภาพ หรือไฟล์ PPK/INS เพิ่มเติม หากไม่มี rotation กล้องนั้นจะถูกข้าม

ถ้าจะนำเข้ามุมจากไฟล์ ให้ยืนยัน convention ให้ถูกต้อง เช่น Yaw/Pitch/Roll หรือ
Omega/Phi/Kappa สคริปต์ force ปัจจุบันรองรับเฉพาะ `Metashape.EulerAnglesYPR`

## การตั้ง accuracy

ค่าความแม่นยำต้องสะท้อน uncertainty จริงหลังประมวลผล PPK ไม่ใช่เพียงค่าที่ดีที่สุด
ในสเปกอุปกรณ์ ตัวอย่างเมื่อรายงานระบุ H = 2 cm และ V = 5 cm:

- X accuracy = `0.02 m`
- Y accuracy = `0.02 m`
- Z accuracy = `0.05 m`

หาก Metashape แสดงหน่วยเป็นเมตร การกรอก `0.02 cm` จะเท่ากับ `0.0002 m` และให้
น้ำหนักตำแหน่งสูงเกินจริงอย่างมาก
