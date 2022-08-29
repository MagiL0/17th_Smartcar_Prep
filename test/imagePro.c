/*
 * @Author: 28x wither1260407765@outlook.com
 * @Date: 2022-08-12 15:30:27
 * @LastEditors: Please set LastEditors
 * @LastEditTime: 2022-08-13 19:11:42
 * @FilePath: \Geese\test\imagePro.c
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */

#include "imagePro.h"
#include "stdio.h"
#include "math.h"

extern const int dir_front[4][2];
extern const int dir_frontleft[4][2];
extern const int dir_frontright[4][2];



int clip(int x, int low, int up) {
    return x > up ? up : x < low ? low : x;
}

//自适应阈值二值化
void adaptive_threshold(image_t *img0, image_t *img1, int block_size, int down_value, uint8_t low_value, uint8_t high_value) {
    // assert(img0 && img0->data);
    // assert(img1 && img1->data);
    // assert(img0->data != img1->data);
    // assert(img0->width == img1->width && img0->height == img1->height);
    // assert(block_size > 1 && block_size % 2 == 1);

    int half = block_size / 2;
    // 先遍历y后遍历x比较cache-friendly
    for (int y = 0; y < img0->height; y ++) {
        for (int x = 0; x < img0->width; x++) {
            int thres_value = 0;
            for (int dy = -half; dy <= half; dy++) {
                for (int dx = -half; dx <= half; dx++) {
                    thres_value += AT_CLIP(img0, x + dx, y + dy);
                }
            }
            thres_value /= block_size * block_size;
            thres_value -= down_value;
            AT(img1, x, y) = AT(img0, x, y) < thres_value ? low_value : high_value;
        }
    }
}

// 左手迷宫巡线
void findline_lefthand_adaptive(image_t *img, int block_size, int clip_value, int x, int y, uint8_t pts[][2], int *num) {
    // assert(img && img->data);
    // assert(num && *num >= 0);
    // assert(block_size > 1 && block_size % 2 == 1);
    int half = block_size / 2;
    int step = 0, dir = 0, turn = 0, count_white = 0;

    //debug
    printf("%d,%d,%d,%d,%d,%d\n",
            step < *num ,
            half < x ,
            x < img->width - half - 1 ,
            half < y ,
            y < img->height - half - 1 ,
            turn < 4);

    
    while (step < *num 
            && half < x 
            && x < img->width - half - 1 
            && half < y 
            && y < img->height - half - 1 
            && turn < 4) 
    {
        int local_thres = 0;
        //求自区域适应阈值，大小为 block_size * block_size，结果为 local_thres
        for (int dy = -half; dy <= half; dy++) {
            for (int dx = -half; dx <= half; dx++) {
                local_thres += AT(img, x + dx, y + dy);
            }
        }
        local_thres /= block_size * block_size;
        local_thres -= clip_value;


        //计算该点前方，左前方，右前方的点是否是黑的
        int current_value = AT(img, x, y);
        int front_value = AT(img, x + dir_front[dir][0], y + dir_front[dir][1]);
        int frontleft_value = AT(img, x + dir_frontleft[dir][0], y + dir_frontleft[dir][1]);

        //添加修正，使用count_white如果周围都是白线就向右找
        if (count_white >= 4) {
            step =0; //没找到黑线，清零
            x -= 1; //向左走
            if(x >= IMGW || x < 0 || y >= IMGH || y < 0) {
                return;
            }
            count_white = 0;
            printf("5");
            turn = 0;
            dir = 0;
        }


        if (front_value < local_thres) {//如果前面是黑色需要右转一次
            dir = (dir + 1) % 4;//防止大于3，方向为 0123
            turn++;
            count_white = 0;
            printf("1");
        } else if (frontleft_value < local_thres) {//如果前方像素为白色，且左前方像素为黑色
            x += dir_front[dir][0];
            y += dir_front[dir][1];
            pts[step][0] = x;//重写黑边
            pts[step][1] = y;
            step++;
            turn = 0;
            count_white = 0;
            printf("2");
        } else {//前方为白色，左前方为白色（墙角）
            x += dir_frontleft[dir][0];// 遇到墙角要斜着走
            y += dir_frontleft[dir][1];
            dir = (dir + 3) % 4;// 遇到墙角要左转一次
            pts[step][0] = x;
            pts[step][1] = y;
            step++;
            turn = 0;
            count_white ++;
            printf("3");
        }
    }
    *num = step;

}

// 右手迷宫巡线
void findline_righthand_adaptive(image_t *img, int block_size, int clip_value, int x, int y, uint8_t pts[][2], int *num) {
    // assert(img && img->data);
    // assert(num && *num >= 0);
    // assert(block_size > 1 && block_size % 2 == 1);
    int half = block_size / 2;
    int step = 0, dir = 0, turn = 0, count_white = 0;

     //debug
    printf("%d,%d,%d,%d,%d,%d\n",
            step < *num ,
            half < x ,
            x < img->width - half - 1 ,
            half < y ,
            y < img->height - half - 1 ,
            turn < 4);

    //求自区域适应阈值，大小为 block_size * block_size
    while (step < *num 
            && 0 < x 
            && x < img->width - 1 
            && 0 < y 
            && y < img->height - 1 
            && turn < 4) 
    {
        int local_thres = 0;
        for (int dy = -half; dy <= half; dy++) {
            for (int dx = -half; dx <= half; dx++) {
                local_thres += AT(img, x + dx, y + dy);
            }
        }
        local_thres /= block_size * block_size;
        local_thres -= clip_value;

        int current_value = AT(img, x, y);
        int front_value = AT(img, x + dir_front[dir][0], y + dir_front[dir][1]);
        int frontright_value = AT(img, x + dir_frontright[dir][0], y + dir_frontright[dir][1]);

        //添加修正，使用count_white如果周围都是白线就向右找
        if (count_white >= 4) {
            step =0; //没找到黑线，清零
            x += 1; //向右走
            if(x >= IMGW || x < 0 || y >= IMGH || y < 0) {
                return;
            }
            count_white = 0;
            printf("5");
            turn = 0;
            dir = 0;
        }

        if (front_value < local_thres) {
            dir = (dir + 3) % 4;
            turn++;
            printf("1");
            count_white  = 0;
        } else if (frontright_value < local_thres) {
            x += dir_front[dir][0];
            y += dir_front[dir][1];
            pts[step][0] = x;
            pts[step][1] = y;
            step++;
            turn = 0;
            count_white  = 0;
            printf("2");
        } else {
            x += dir_frontright[dir][0];
            y += dir_frontright[dir][1];
            dir = (dir + 1) % 4;
            pts[step][0] = x;
            pts[step][1] = y;
            step++;
            turn = 0;
            printf("3");
            count_white ++;
        }
    }
    *num = step;
}



/**
 * @description: 等距采样，使采样后的点几何距离相等
 * @param {uint8_t} pts_in[][2] 需要采样的线
 * @param {uint8_t} num1            被采样线长度
 * @param {float} pts_out[][2]  采样结果
 * @param {uint8_t} *num2          采样出的线的长度的返回值
 * @param {float} dist          指定的采样点间隔
 * @return {*}
 */
void resample_points(uint8_t pts_in[][2], uint8_t num1, float pts_out[][2], uint8_t *num2, float dist)
{
    int remain = 0, len = 0;
    for(int i=0; i<num1-1 && len < *num2; i++){
        float x0 = pts_in[i][0];
        float y0 = pts_in[i][1];
        float dx = pts_in[i+1][0] - x0;
        float dy = pts_in[i+1][1] - y0;
        float dn = sqrt(dx*dx+dy*dy);
        dx /= dn;
        dy /= dn;

        while(remain < dn && len < *num2){
            x0 += dx * remain;
            pts_out[len][0] = x0;
            y0 += dy * remain;
            pts_out[len][1] = y0;
            
            len++;
            dn -= remain;
            remain = dist;
        }
        remain -= dn;
    }
    *num2 = len;
}

/**
 * @description: 局部角度变化率计算
 * @param {float} pts_in[][2]   等距采样后的线
 * @param {uint8_t} num             等距采样后线的长度
 * @param {float} angle_out[]     输出的角度集合
 * @param {int} dist            用于计算角度的点之间间隔dist - 1个点
 * @return {*}
 */
void local_angle_points(float pts_in[][2], uint8_t num, float angle_out[], int dist) 
{
    for (int i = 0; i < num; i++) {
        if (i <= 0 || i >= num - 1) {
            angle_out[i] = 0;
            continue;
        }
        float dx1 = pts_in[i][0] - pts_in[clip(i - dist, 0, num - 1)][0];
        float dy1 = pts_in[i][1] - pts_in[clip(i - dist, 0, num - 1)][1];
        float dn1 = sqrtf(dx1 * dx1 + dy1 * dy1);
        float dx2 = pts_in[clip(i + dist, 0, num - 1)][0] - pts_in[i][0];
        float dy2 = pts_in[clip(i + dist, 0, num - 1)][1] - pts_in[i][1];
        float dn2 = sqrtf(dx2 * dx2 + dy2 * dy2);
        float c1 = dx1 / dn1;
        float s1 = dy1 / dn1;
        float c2 = dx2 / dn2;
        float s2 = dy2 / dn2;
        angle_out[i] = (dx1 * dx2 + dy1 * dy2) / (dn1) / dn2;
        // angle_out[i] = atan2f(c1 * s2 - c2 * s1, c2 * c1 + s2 * s1);
    }
}


/**
 * @description: 角度非极大值抑制
 * @param {float} angle_in[]   输入的角度数组
 * @param {uint8_t} num             输入数组长度
 * @param {float} angle_out[]  输出的角度数组
 * @param {int} kernel          非极大值抑制的范围
 * @return {*}
 */
void nms_angle(float angle_in[], uint8_t num, float angle_out[], int kernel) {
    // assert(kernel % 2 == 1);
    int half = kernel / 2;
    for (int i = 0; i < num; i++) {
        angle_out[i] = angle_in[i];
        for (int j = -half; j <= half; j++) {
            if (fabs(angle_in[clip(i + j, 0, num - 1)]) > fabs(angle_out[i])) {
                angle_out[i] = 0;
                break;
            }
        }
    }
}



/**
 * @description: 左边线跟踪中线
 * @param {float} pts_in
 * @param {unsigned char} num
 * @param {float} pts_out
 * @param {int} approx_num  极限大小，代表前后几个点
 * @param (unsigned char) * num1
 * @param {float} dist      距离     
 * @return {*}
 */
void track_leftline(float pts_in[][2], unsigned char num, float pts_out[][2], int approx_num, unsigned char* num1, float dist) {
    for (int i = 0; i < num; i++) {
        float dx = pts_in[clip(i + approx_num, 0, num - 1)][0] - pts_in[clip(i - approx_num, 0, num - 1)][0];
        float dy = pts_in[clip(i + approx_num, 0, num - 1)][1] - pts_in[clip(i - approx_num, 0, num - 1)][1];
        float dn = sqrt(dx * dx + dy * dy);
        dx /= dn;  
        dy /= dn;
        pts_out[i][0] = pts_in[i][0] - dy * dist;
        pts_out[i][1] = pts_in[i][1] + dx * dist;
    }
    *num1 = num;

}

/**
 * @description: 右边线跟踪中线
 * @param {float} pts_in
 * @param {unsigned char} num
 * @param {float} pts_out
 * @param {int} approx_num  极限大小，代表前后几个点
 * @param (unsigned char) * num1
 * @param {float} dist      距离     
 * @return {*}
 */
void track_rightline(float pts_in[][2], unsigned char num, float pts_out[][2], int approx_num, unsigned char* num1, float dist) {
    for (int i = 0; i < num; i++) {
        float dx = pts_in[clip(i + approx_num, 0, num - 1)][0] - pts_in[clip(i - approx_num, 0, num - 1)][0];
        float dy = pts_in[clip(i + approx_num, 0, num - 1)][1] - pts_in[clip(i - approx_num, 0, num - 1)][1];
        float dn = sqrt(dx * dx + dy * dy);
        dx /= dn;
        dy /= dn;
        pts_out[i][0] = pts_in[i][0] + dy * dist;
        pts_out[i][1] = pts_in[i][1] - dx * dist;
    }
    *num1 = num;

}









void find_corners(void);
void process_image(void);