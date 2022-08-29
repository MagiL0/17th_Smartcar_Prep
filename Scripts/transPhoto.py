import cv2
import numpy as np
import glob


'''
description: 该函数当点击图片是被 OpenCV 调用，返回点击点的像素位置，用于修改 src 中的坐标值
param {*} event
param {*} x
param {*} y
param {*} flags
param {*} param
return {*}
'''
def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("x:",x/2,"y:",y/2)

if __name__ == "__main__":
    #src为原像素点位置，dst为在新图像中像素点位置，该坐标由标定的图像决定
    src = np.float32([[66, 66], [103, 66],[58, 96], [113, 96]])
    dst = np.float32([[0, 0], [15, 0], [0, 15], [15, 15]])

    #使用 numpy 读取图片
    frame = np.loadtxt("tran" + ".txt", dtype= np.uint8)
    frame = np.resize(frame, (120,160))
    img = frame
    #金字塔放大，放大为原来的四倍，可以图片显示的更大，方便点击
    img_up = cv2.pyrUp(img)
    cv2.imshow("2",img_up)
    cv2.setMouseCallback("2", on_EVENT_LBUTTONDOWN)
    #按任意键退出
    cv2.waitKey(0)
    

    # 生成透视变换矩阵；进行透视变换
    m = cv2.getPerspectiveTransform(src, dst)
    print(m)

    #定义变量，方便后续计算测试
    M00 = m[0][0]
    M01 = m[0][1]
    M02 = m[0][2]
    M10 = m[1][0]
    M11 = m[1][1]
    M12 = m[1][2]
    M20 = m[2][0]
    M21 = m[2][1]
    M22 = m[2][2]
    #定义 max_x，max_y 等，方便确定变换后 x,y 的值的范围
    max_x = max_y = 0
    min_x = min_y = 500

    #黑色背景图像显示效果不佳，因此创建空白白色图像，用于显示变换后的图像，如果是在测试透视变换新的src数据，可以设大一点
    img_blank = np.full([1000,1000],255,dtype= np.uint8)

    #设定模式，之前测试时增加了很多无用模式，现在都已删去
    usem = 5


    if usem == 5:#直接读取矩阵 m，计算输出值，储存数组，转换为表，生成图像

        #读取文件
        fx = open("resultX.txt", "w")
        fy = open("resultY.txt", "w")

        #生成列表储存数据
        a = np.array([],dtype= np.int)
        b = np.array([],dtype= np.int)
        
        #计数，计算计算了几次
        count = 0

        #主循环
        for j in range(0, 160):
            for i in range(0,120):
                # 因较远点透视变换漂移严重，无价值，所以删除i<20的点，同时为了让数组是个整数，令i < 23 && i >= 20 的点为 0
                # 之后建议直接删去较远点，不再置零，同时数组大小会变，勿忘
                if i >= 20 and i < 23:
                    x = 0
                    y = 0

                    #写入文件
                    fx.write("%3d "%(int(x)))
                    fy.write("%3d "%(int(y)))
                    #写入数组
                    a = np.append(a, int(x))
                    b = np.append(b, int(y))
                    #计数+1
                    count += 1

                #保留 i >= 23 的有价值点
                if i < 23:
                    continue

                # 计算透视变换
                # 最后的常数用于将生成的变换矩阵移到图片中心，方便单片机显示，根据max_x，max_y等数据对应，x中心为0，y最下方为0
                x = (m[0][0] * j + m[0][1] * i + m[0][2]) / (m[2][0] * j + m[2][1] * i + m[2][2]) + 82 + 22
                y = (m[1][0] * j + m[1][1] * i + m[1][2]) / (m[2][0] * j + m[2][1] * i + m[2][2]) + 88 + 18
                
                # 变换后位置在图像上显示
                img_blank[int(y)][int(x)] = img[i][j]

                # 保存 x,y
                fx.write("%3d "%(int(x)))
                fy.write("%3d "%(int(y)))
                a = np.append(a, int(x))
                b = np.append(b, int(y))
                #计数+1
                count += 1

                # 计算x，y最大最小值
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
        # 保存数据
        np.savetxt("X.txt",a,  fmt="%d", newline=",",delimiter=',')
        np.savetxt("Y.txt",b,  fmt="%d", newline=",",delimiter=',')
        print(count)
        print("max_x:",max_x,"max_y:",max_y)
        print("min_x:",min_x,"min_y:",min_y)
        print(max_x - min_x, max_y- min_y)
        
    elif usem == 6:#检验输出集
        mapx = np.reshape(np.loadtxt("X.txt"),[160,100])
        mapy = np.reshape(np.loadtxt("Y.txt"),[160,100])
        
        # mapx = np.reshape(np.loadtxt("resultX.txt"),[120,160])
        # mapy = np.reshape(np.loadtxt("resultY.txt"),[120,160])
        for j in range(160):
            for i in range(20, 120):
                x = int(mapx[j][i - 20])
                y = int(mapy[j][i - 20])
                img_blank[y][x] = img[i][j]
        

    # 显示
    result = cv2.warpPerspective(img, m, (15, 15))
    result = cv2.pyrUp(result)
    print(max)
    cv2.imshow("1",img_blank)
    # cv2.imshow("1",result)
    cv2.waitKey(0)
    exit(0)