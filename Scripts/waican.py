import cv2
import numpy as np
 
#读取相机内参

 
def draw(img, corners, imgpts):
    corners.astype(np.int)
    corner = tuple(corners[0].ravel())
    print(corner)
    
    print(type(tuple(imgpts[0].ravel())))
    print(tuple(imgpts[1].ravel()))
    print(tuple(imgpts[2].ravel()))
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
    return img
 
#标定图像保存路径
photo_path = "C:\\Users\\wlx\\Documents\\py_study\\camera calibration\\image\\6.jpg"
#标定图像
def calibration_photo(photo_path):
    #设置要标定的角点个数
    x_nums = 6                                                          #x方向上的角点个数
    y_nums = 4
    #设置(生成)标定图在世界坐标中的坐标
    world_point = np.zeros((x_nums * y_nums,3),np.float32)            #生成x_nums*y_nums个坐标，每个坐标包含x,y,z三个元素
    world_point[:,:2] = np.mgrid[:x_nums,:y_nums].T.reshape(-1, 2)    #mgrid[]生成包含两个二维矩阵的矩阵，每个矩阵都有x_nums列,y_nums行
                                                                        #.T矩阵的转置
                                                                        #reshape()重新规划矩阵，但不改变矩阵元素
    #设置世界坐标的坐标
    axis = np.float32([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)
    #设置角点查找限制
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,30,0.001)
    
    # image = cv2.imread("123.jpg",0)
    image = np.loadtxt("2" + ".txt", dtype= np.uint8)
    image = np.resize(image, (120,188))
    
    gray = image
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    #查找角点
    # cv2.imshow("1",gray)
    # cv2.waitKey(0)
    ok,corners = cv2.findChessboardCorners(gray,(x_nums,y_nums),None)
    print(ok)
    if ok:
        #获取更精确的角点位置
        exact_corners = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
 
        #获取外参
        _,rvec, tvec, inliers = cv2.solvePnPRansac(world_point, exact_corners, mtx, dist)
 
        # imgpts, jac = cv2.projectPoints(axis, rvec, tvec, mtx, dist)
        #可视化角点
        # imgpts = imgpts.astype(np.int)
        R,_ = cv2.Rodrigues(rvec)
        print("R:",R)
        T,_ =
        print("tvec:",tvec)
        # img = draw(image, corners, imgpts)
        # cv2.imshow('img', img)
 
 
 
if __name__ == '__main__':
    mtx = np.array([154.00609349,0.,250.35551657,0.,150.50327175,101.67642477,0.,0.,1.])
    mtx = np.reshape(mtx,[3,3])
    dist = np.array([-0.40289857,0.35526741,-0.00649092,-0.04668408,-0.1285067])
    calibration_photo(photo_path)
    cv2.waitKey()
    cv2.destroyAllWindows()