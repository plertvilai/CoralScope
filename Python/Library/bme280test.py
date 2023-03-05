import bme280

data = bme280.readBME280All()

print('Temp = %f C'%data[0])
print('Press = %f mbar'%data[1])
print('Gauge press = %f mbar'%data[2])
print('RH =%f'%data[3])
