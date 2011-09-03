import os
import time
from multipart import MultipartParser

def main():
    filename = os.getcwd() + "/data-multipart-form-data-chrome.txt"
    filesize = os.path.getsize(filename)
    
    with open(filename) as f:
        
        content_type = "multipart/form-data; boundary=------WebKitFormBoundaryy68h9UzzE0zpkUU7"
        index        = content_type.rfind("=") + 1
        boundary     = content_type[index:]
        
        start        = time.clock() * 1000
        machine      = MultipartParser(boundary, f)
        
        print("\nElapsed time: " + str(time.clock() * 1000 - start) + "ms")
        
        print("\n----------- Files:")
        print(machine.files )
        print("\n----------- Params:")
        print(machine.params)

if __name__ == "__main__":
    main()