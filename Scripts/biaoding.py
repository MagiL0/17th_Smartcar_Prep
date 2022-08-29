from winreg import REG_OPTION_NON_VOLATILE
import cv2
import numpy as np
import glob

# 找棋盘格角点
# 阈值
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
#棋盘格模板规格
w = 6   #内角点个数，内角点是和其他格子连着的点
h = 4

# 世界坐标系中的棋盘格点,例如(0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)，去掉Z坐标，记为二维矩阵
objp = np.zeros((w*h,3), np.float32)
objp[:,:2] = np.mgrid[0:w,0:h].T.reshape(-1,2)
# 储存棋盘格角点的世界坐标和图像坐标对
objpoints = [] # 在世界坐标系中的三维点
imgpoints = [] # 在图像平面的二维点
gray = np.array([])
images = glob.glob('biaoding/a*')
for fname in images:
    # img = cv2.imread(fname)
    # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    image = np.loadtxt(fname, dtype= np.uint8)
    image = np.resize(image, (120,160))
    img = image
    gray = img
    # 找到棋盘格角点
    # 棋盘图像(8位灰度或彩色图像)  棋盘尺寸  存放角点的位置
    ret, corners = cv2.findChessboardCorners(gray, (w,h),None)
    # 如果找到足够点对，将其存储起来
    print(ret)
    if ret == True:
        # 角点精确检测
        # 输入图像 角点初始坐标 搜索窗口为2*winsize+1 死区 求角点的迭代终止条件
        cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        objpoints.append(objp)
        imgpoints.append(corners)
        # 将角点在图像上显示
        cv2.drawChessboardCorners(img, (w,h), corners, ret)
        cv2.imshow('findCorners',img)
        cv2.waitKey(1000)
cv2.destroyAllWindows()
#标定、去畸变
# 输入：世界坐标系里的位置 像素坐标 图像的像素尺寸大小 3*3矩阵，相机内参数矩阵 畸变矩阵
# 输出：标定结果 相机的内参数矩阵 畸变系数 旋转矩阵 平移向量
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
# mtx：内参数矩阵
# dist：畸变系数
# rvecs：旋转向量 （外参数）
# tvecs ：平移向量 （外参数）
print (("ret:"),ret)
print (("mtx:\n"),mtx)        # 内参数矩阵
print (("dist:\n"),dist)      # 畸变系数   distortion cofficients = (k_1,k_2,p_1,p_2,k_3)
print (("rvecs:\n"),rvecs)    # 旋转向量  # 外参数
print (("tvecs:\n"),tvecs)    # 平移向量  # 外参数
np.save("mtx.npy",mtx)
np.save("dist.npy",dist)
# 去畸变
img2 = cv2.imread('111.jpg')
h,w = img2.shape[:2]
# 我们已经得到了相机内参和畸变系数，在将图像去畸变之前，
# 我们还可以使用cv.getOptimalNewCameraMatrix()优化内参数和畸变系数，
# 通过设定自由自由比例因子alpha。当alpha设为0的时候，
# 将会返回一个剪裁过的将去畸变后不想要的像素去掉的内参数和畸变系数；
# 当alpha设为1的时候，将会返回一个包含额外黑色像素点的内参数和畸变系数，并返回一个ROI用于将其剪裁掉
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h)) # 自由比例参数

dst = cv2.undistort(img2, mtx, dist, None, newcameramtx)
# 根据前面ROI区域裁剪图片
x,y,w,h = roi
dst = dst[y:y+h, x:x+w]
# print(roi)
# print(dst)
cv2.imwrite('calibresult.jpg',dst)

# 反投影误差
# 通过反投影误差，我们可以来评估结果的好坏。越接近0，说明结果越理想。
# 通过之前计算的内参数矩阵、畸变系数、旋转矩阵和平移向量，使用cv2.projectPoints()计算三维点到二维图像的投影，
# 然后计算反投影得到的点与图像上检测到的点的误差，最后计算一个对于所有标定图像的平均误差，这个值就是反投影误差。
total_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    total_error += error
print (("total error: "), total_error/len(objpoints))





# import cv2
# import numpy as np
# import glob



# # 找棋盘格角点
# # 设置寻找亚像素角点的参数，采用的停止准则是最大循环次数30和最大误差容限0.001
# criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001) # 阈值
# #棋盘格模板规格
# w = 6   # 10 - 1
# h = 4   # 7  - 1
# # 世界坐标系中的棋盘格点,例如(0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)，去掉Z坐标，记为二维矩阵
# objp = np.zeros((w*h,3), np.float32)
# objp[:,:2] = np.mgrid[0:w,0:h].T.reshape(-1,2)
# objp = objp*18.1  # 18.1 mm

# # 储存棋盘格角点的世界坐标和图像坐标对
# objpoints = [] # 在世界坐标系中的三维点
# imgpoints = [] # 在图像平面的二维点
# #加载pic文件夹下所有的jpg图像
# image = np.loadtxt("6" + "", dtype= np.uint8)
# image = np.resize(image, (120,188))
# img = image
# gray =img
# images = [image]
# gray = image
# i=0
# for fname in images:

#     # img = cv2.imread(fname)
#     # 获取画面中心点
#     #获取图像的长宽
#     h1, w1 = img.shape[0], img.shape[1]
#     # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#     u, v = img.shape[:2]
#     # 找到棋盘格角点
#     ret, corners = cv2.findChessboardCorners(gray, (w,h),None)
#     # 如果找到足够点对，将其存储起来
#     if ret == True:
#         print("i:", i)
#         i = i+1
#         # 在原角点的基础上寻找亚像素角点
#         cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
#         #追加进入世界三维点和平面二维点中
#         objpoints.append(objp)
#         imgpoints.append(corners)
#         # 将角点在图像上显示
#         cv2.drawChessboardCorners(img, (w,h), corners, ret)
#         cv2.namedWindow('findCorners', cv2.WINDOW_NORMAL)
#         cv2.resizeWindow('findCorners', 640, 480)
#         cv2.imshow('findCorners',img)
#         cv2.waitKey(200)
# cv2.destroyAllWindows()

# print('正在计算')
# #标定
# ret, mtx, dist, rvecs, tvecs = \
#     cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)


# print("ret:",ret  )
# print("mtx:\n",mtx)      # 内参数矩阵
# print("dist畸变值:\n",dist   )   # 畸变系数   distortion cofficients = (k_1,k_2,p_1,p_2,k_3)
# print("rvecs旋转（向量）外参:\n",rvecs)   # 旋转向量  # 外参数
# print("tvecs平移（向量）外参:\n",tvecs  )  # 平移向量  # 外参数
# newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0, (u, v))
# print('newcameramtx外参',newcameramtx)
# #打开摄像机
# camera=cv2.VideoCapture(0)
# while True:
#     (grabbed,frame)=camera.read()
#     h1, w1 = frame.shape[:2]
#     newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0, (u, v))
#     # 纠正畸变
#     dst1 = cv2.undistort(frame, mtx, dist, None, newcameramtx)
#     #dst2 = cv2.undistort(frame, mtx, dist, None, newcameramtx)
#     mapx,mapy=cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w1,h1),5)
#     dst2=cv2.remap(frame,mapx,mapy,cv2.INTER_LINEAR)
#     # 裁剪图像，输出纠正畸变以后的图片
#     x, y, w1, h1 = roi
#     dst1 = dst1[y:y + h1, x:x + w1]

#     #cv2.imshow('frame',dst2)
#     #cv2.imshow('dst1',dst1)
#     cv2.imshow('dst2', dst2)
#     if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q保存一张图片
#         cv2.imwrite("frame.jpg", dst1)
#         break

# camera.release()
# cv2.destroyAllWindows()
