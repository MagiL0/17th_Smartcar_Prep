import serial
import cv2
import numpy as np

file_name = "tran"
isget =4
pic_size = (188,120)


if __name__== "__main__":
    # 直接读图像
    if isget == 1:
        frame = cv2.imread("2")
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame, pic_size)
        np.savetxt("line" + ".txt", frame, fmt="%d", newline=",",delimiter=',')
    
    # 读文本，注意数字之间用空格隔开，不能用逗号
    if isget == 2:
        # frame = np.loadtxt("result" + file_name + ".txt", dtype= np.uint8)
        frame = np.loadtxt(file_name + ".txt" , dtype= np.uint8)
        frame = np.resize(frame, pic_size)
        # print(frame.shape)
        cv2.imshow("l",frame)
        cv2.waitKey(0)

    # 从串口读取图像数据，保存在 "filename.txt"
    if isget == 3:
        f = open(file_name, "w")
        count = 0
        stream = b''
        first = -1  
        last = -1  
        ser = serial.Serial("COM6",9600,timeout=0)
        while True:
            ch= ser.readall()
            f = open(file_name, "w")
            stream += ch
            if ch:
                print(ch)
                first = stream.find(b'\xfe\xef')	
                if first != -1:#检测到帧头就接受一整个图像
                    stream = stream[first:]
                    for i in stream:
                        count += 1
                        f.write(str(i) + " ")
                    print(count)
                    last = pic_size[1] * pic_size[0] + 2
                    while len(stream) <= last:#直到接收到一整个图像为止
                        ch= ser.readall()
                        if ch:
                            stream += ch
                            # if ch:#debubg
                            print(ch)
                            for i in ch:
                                count += 1
                                f.write(str(i) + " ")
                            print(count)
                    num = []
                    for i in stream[2:pic_size[1] * pic_size[0] + 2]:#这是一整个图像，转化为int的list
                        num.append(i)
                    frame = np.array(num, dtype = np.uint8)
                    frame = np.resize(frame, pic_size)
                    print(frame.shape)
                    print(frame)
                    cv2.imshow("l",frame)
                    cv2.waitKey(0)
                    f.close()
                    np.savetxt(file_name + ".txt", frame, fmt="%d", newline=" ",delimiter=' ')
                    exit(0)


    if isget == 5:
        f = open(file_name, "w")
        count = 0
        stream = b''
        first = -1  
        last = -1  
        ser = serial.Serial("COM15",460800,timeout=0)
        # while True:
        #     ch = ser.readall()
        #     if ch:
        #         print(ch)
        #         for i in ch:
        #             # ch = int.from_bytes(ch,"little");
        #             f.write(str(i) + ' ')
        while True:
            ch= ser.readall()
            f = open(file_name, "w")
            stream += ch
            if ch:
                print(ch)
                first = stream.find(b'\xfe\xef')	
                for i in ch:
                    f.write(str(i) + " ")				# 检测帧头位置
                # last = stream.find(b'\xef\xfe')
                if first != -1:#检测到帧头就接受一整个图像
                    stream = stream[first:]
                    for i in ch:
                        count += 1
                        f.write(str(i) + " ")
                    print(count)
                    last = 60 * 94 + 2
                    while len(stream) <= last:#直到接收到一整个图像为止
                        ch= ser.readall()
                        if ch:
                            stream += ch
                            # if ch:#debubg
                            print(ch)
                            for i in ch:
                                count += 1
                                f.write(str(i) + " ")
                                
                            print(count)
                    # print('\n',first,last,len(stream))#debug
                    num = []
                    for i in stream[2:60 * 94 + 2]:#这是一整个图像，转化为int的list
                        num.append(i)
                    frame = np.array(num, dtype = np.uint8)
                    frame = np.resize(frame, (60,94))
                    print(frame.shape)
                    print(frame)
                    cv2.imshow("l",frame)
                    cv2.waitKey(0)
                    f.close()
                    exit(0)     

    # 貌似当时整的畸变矫正，不用了
    if isget == 6:
        K = np.array([154.00609349,0,250.35551657,
                0,150.50327175,101.67642477,
                0, 0,          1.])
        K = np.reshape(K,[3,3])
        R = np.array([0.64807946,-0.70527128,-0.2873768,
                -0.08730985,0.30605274,-0.94800249,
                0.75655139,0.63947177,0.13676936])
        R =np.reshape(R,[3,3])
        H = np.matmul(K, R, np.linalg.inv(K))
        print(H)
        frame = np.loadtxt(file_name + ".txt", dtype= np.uint8)
        frame = np.resize(frame, (120,188))
        print(frame.shape)
        blank = np.zeros([1000,1000],dtype=np.uint8)
        P = np.zeros([120,188,2],dtype = np.uint8)
        # print(np.array([1,2,3]).T)
        for i in range(120):
            for j in range(188):
                temp = np.matmul(H, np.array([i,j,1]))
                temp = temp.astype(np.uint8)
                # print("temp:",temp)
                blank[temp[0]][temp[1]] = frame[i][j]
        cv2.imshow("l",blank)
        cv2.waitKey(0)
