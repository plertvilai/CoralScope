import tsys01

sensor = tsys01.TSYS01() # Use default I2C bus 1
sensor.init()
sensor.read()

print("%.2f C"%sensor.temperature())