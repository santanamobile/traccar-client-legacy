# Traccar Client

Python script to use with traccar platform (legacy protocol).

## Disclaimer

This protocol is used only by old versions of Traccar Client. New versions use the [OsmAnd protocol](https://www.traccar.org/osmand/).

## Requirements

- A working GPSDd instalation (not covered in this documentation).
- Python: python3-urllib3

## Configure

Configure this variables on traccar-client-legacy.py

- Rename settings.json.example to settings.json and fill the parameters
    - IP Address of the traccar server: TRACCAR_SERVER
    - Port of the traccar server: TRACCAR_PORT
    - IMEI or identificator of device: DEVICE_ID
    - IP Address of gpsd server: GPSD_HOST

## Reference

- [Modern GPS Tracking Platform](https://www.traccar.org/)
- [Traccar Client Protocol](https://www.traccar.org/traccar-client-protocol/)
- [NMEA Checksum Calculator](https://nmeachecksum.eqth.net/)

## Author

- [@santanamobile](https://www.github.com/santanamobile)

## License

[MIT](https://choosealicense.com/licenses/mit/)
