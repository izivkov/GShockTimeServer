from oled_simulator import MockOLEDDisplay

def main():
    oled = MockOLEDDisplay()
    oled.show_status(
        watch_name="G-SHOCK",
        battery="73%",
        temperature="22°C",
        last_sync="15:10",
        alarm="07:00",
        reminder="Fri 9AM",
        auto_sync="On"
    )

if __name__ == "__main__":
    main()
    