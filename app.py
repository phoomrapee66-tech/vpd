from flask import Flask, render_template
from tuya_connector import TuyaOpenAPI
import os
import math

app = Flask(__name__)

ACCESS_ID = os.getenv("TUYA_CLIENT_ID")
ACCESS_SECRET = os.getenv("TUYA_CLIENT_SECRET")
ENDPOINT = os.getenv("TUYA_BASE_URL", "https://openapi-sg.iotbing.com")
DEVICE_ID = os.getenv("SOURCE_DEVICE_ID", "a32e7407c610f47336kgoa")

def get_vpd():
    openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_SECRET)
    openapi.connect()
    data = openapi.get(f"/v1.0/devices/{DEVICE_ID}/status")
    status_list = data.get("result", [])

    temp_raw = next((i["value"] for i in status_list if i["code"] == "temp_current"), None)
    humidity = next((i["value"] for i in status_list if i["code"] == "humidity_value"), None)

    if temp_raw is None or humidity is None:
        return None

    T = temp_raw / 10
    SVP = 0.6108 * math.exp(17.27 * T / (T + 237.3))
    AVP = SVP * (humidity / 100)
    VPD = round(SVP - AVP, 3)

    if VPD < 0.4:
        zone = "ชื้นมากเกินไป — เสี่ยงเชื้อรา"
    elif VPD < 0.8:
        zone = "เหมาะสำหรับต้นกล้า"
    elif VPD < 1.2:
        zone = "เหมาะสมที่สุด"
    elif VPD < 1.6:
        zone = "เหมาะสำหรับช่วง Veg/Flower"
    else:
        zone = "แห้งเกินไป — ต้นไม้เครียด"

    return {
        "temp": T,
        "humidity": humidity,
        "vpd": VPD,
        "zone": zone
    }

@app.route("/")
def index():
    data = get_vpd()
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
def get_vpd():
    try:
        openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_SECRET)
        connect_result = openapi.connect()
        print("CONNECT RESULT:", connect_result, flush=True)

        data = openapi.get(f"/v1.0/devices/{DEVICE_ID}/status")
        print("STATUS DATA:", data, flush=True)

        status_list = data.get("result", [])
        temp_raw = next((i["value"] for i in status_list if i["code"] == "temp_current"), None)
        humidity = next((i["value"] for i in status_list if i["code"] == "humidity_value"), None)

        if temp_raw is None or humidity is None:
            print("MISSING temp or humidity in status_list:", status_list, flush=True)
            return None

        T = temp_raw / 10
        SVP = 0.6108 * math.exp(17.27 * T / (T + 237.3))
        AVP = SVP * (humidity / 100)
        VPD = round(SVP - AVP, 3)

        if VPD < 0.4:
            zone = "ชื้นมากเกินไป — เสี่ยงเชื้อรา"
        elif VPD < 0.8:
            zone = "เหมาะสำหรับต้นกล้า"
        elif VPD < 1.2:
            zone = "เหมาะสมที่สุด"
        elif VPD < 1.6:
            zone = "เหมาะสำหรับช่วง Veg/Flower"
        else:
            zone = "แห้งเกินไป — ต้นไม้เครียด"

        return {"temp": T, "humidity": humidity, "vpd": VPD, "zone": zone}

    except Exception as e:
        print("EXCEPTION:", e, flush=True)
        return None