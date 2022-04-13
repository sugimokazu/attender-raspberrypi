# -*- coding: utf-8 -*-
 
from __future__ import print_function
from time import sleep
from ctypes import *
import requests
 
# libpafe.hの77行目で定義
FELICA_POLLING_ANY = 0xffff

url = "http://192.168.100.144/att/conn_mongodb.php"

def httpTransmit(idm):
    idm = str(idm)
    print(idm,"の出席を確認しました．")
    param = {'id': idm}
    res = requests.get(url, params=param)
    print(res.status_code)

def main():
    libpafe = cdll.LoadLibrary("/usr/local/lib/libpafe.so")
    libpafe.pasori_open.restype = c_void_p
    pasori = libpafe.pasori_open()
    libpafe.pasori_init(pasori)
    libpafe.felica_polling.restype = c_void_p
    beforeIdm = None
    try:
        while True:
            felica = libpafe.felica_polling(pasori, FELICA_POLLING_ANY, 0, 0)
            idm = c_ulonglong() 
            libpafe.felica_get_idm.restype = c_void_p
            libpafe.felica_get_idm(felica, byref(idm))
            idm_No = "%016X" % idm.value
            
            if idm_No == '0000000000000000' or beforeIdm == idm_No:
                pass
            else:
                # Cのint型配列の定義(長さ16)
                int_array16 = c_uint8 * 16
                felica = libpafe.felica_polling(pasori, FELICA_POLLING_ANY, 0, 0)
                # 応答データ
                data = int_array16()
                result = libpafe.felica_read_single(felica,int(0x200B),0,c_uint8(0), byref(data))
                print("結果：",result)
                d = (data[:8])
                data = bytes(d)
                studentNumber = data.decode("utf-8")
                print(f"IDM  : {idm_No}")
                print(f"学籍番号   :  {studentNumber}")
                httpTransmit(studentNumber)
                print('deny')
                beforeIdm = idm_No
            
            sleep(0.2)
 
    except KeyboardInterrupt:
        print('finished')
        libpafe.free(felica)
        libpafe.pasori_close(pasori)
 
if __name__ == '__main__':
    main()