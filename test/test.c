

#include <stdio.h>
#include "image.h"
#include "imagePro.h"
#include "math.h"
#define IMGH 120
#define IMGW 160
#define uint8_t unsigned char
#define uint32_t unsigned long

unsigned char img_blk[160*120] = {0};
unsigned char rimg[280 * 180] = {0};

#define ABS(x)  (x>=0?x:-x)
extern unsigned char mapx[160][100];
extern unsigned char mapy[160][100];
/* 前进方向定义：
 *   0
 * 3   1
 *   2
 * 引用格式：点 (x,y) 朝左前方前进一步: x = dir_frontleft[0][0], y =  dir_frontleft[0][1]
 * front为标准上下左右，frontleft为方向逆时针旋转 45°，frontright为顺时针旋转 45°
 */
const int dir_front[4][2] = {{0,  -1},
                            {1,  0},
                            {0,  1},
                            {-1, 0}};
const int dir_frontleft[4][2] = {{-1, -1},
                                {1,  -1},
                                {1,  1},
                                {-1, 1}};
const int dir_frontright[4][2] = {{1,  -1},
                                {1,  1},
                                {-1, 1},
                                {-1, -1}};

 



image_t img_raw = {img, IMGW, IMGH, IMGW};
image_t img_blank = {img_blk, IMGW, IMGH, IMGW};
image_t img_rp = {rimg, 280, 180, 280};
uint8_t pts[IMGH][2] =  {0};
float angles0[IMGH];
float angles1[IMGH];
float angle_out0[IMGH];
float angle_out1[IMGH];


//清零为白色
void draw_paper(image_t *img){
    int i = 0, j = 0;
    for (i = 0; i < img ->width; i++){
        for (j = 0; j < img ->height; j++){
            AT(img,i,j) = 255;
        }
    }
}

//在白纸上画黑线
void draw_line(image_t *img, uint8_t pts[][2], int length){
    int i = 0;
    for (i = 0; i < length; i++){
        AT(img, pts[i][0], pts[i][1]) = 0; 
    }
}


//写入文件
void write_img(image_t *img, char* filename)
{
    int i ,j;
    FILE * fp = fopen(filename,"w");
    for (i = 0; i < img ->height; i++){
        for (j = 0; j < img ->width; j++){
            fprintf(fp,"%u ",AT(img,j,i));
        }
        fprintf(fp, "\n");
    }
}




void main () {
    //初始化数据
    //左右边线
    uint8_t ipts0[120][2];
    uint8_t ipts1[120][2];
    int ipts0_num= 120, ipts1_num= 120;

    int findRoad=1;

    //左右复变换后边线
    uint8_t rpts0[120][2];
    uint8_t rpts1[120][2];
    uint8_t   rpts0_num= 120, rpts1_num= 120;
    //左右等距采样
    float rpta0[120][2];
    float rpta1[120][2];
    uint8_t rpta0_num= 120, rpta1_num= 120;
    //左右等距采样后的中线
    float rptm0[120][2];
    float rptm1[120][2];
    uint8_t rptm0_num= 120, rptm1_num= 120;

    //赋初值 
    int i = 0;
    for (i = 0;  i < IMGH; i ++){
        rpts1[i][0] = rpts0[i][0] = ipts1[i][0] = ipts0[i][0] = i;
        rpts1[i][1] = rpts0[i][1] = ipts1[i][1] = ipts0[i][1] = i;
    }
    
    int num = 128;
    draw_paper(&img_blank);
    draw_paper(&img_rp);

    if (findRoad) {
        findline_lefthand_adaptive(&img_raw,7,25,60,100,ipts0,&ipts0_num);
        printf("\nend\n");
        findline_righthand_adaptive(&img_raw,7,25,110,100,ipts1,&ipts1_num);
        // blur_points();
        draw_line(&img_blank, ipts0, IMGH);
        draw_line(&img_blank, ipts1, IMGH);
    } else {
        adaptive_threshold(&img_raw,&img_blank,7,25,0,255);
    }
  
    for (short i = 0; i < ipts0_num; i++) {
        if (ipts0[i][1] < 23) continue;
        unsigned char x = mapx[ipts0[i][0]][ipts0[i][1] - 20];
        unsigned char y = mapy[ipts0[i][0]][ipts0[i][1] - 20];
        // printf("%u,%u",x,y);
        rpts0[i][0] = x;
        rpts0[i][1] = y;
        rpts0_num = i + 1;
    }
    for (short i = 0; i < ipts1_num; i++) {
        if (ipts1[i][1] < 23) continue;
        unsigned char x = mapx[ipts1[i][0]][ipts1[i][1] - 20];
        unsigned char y = mapy[ipts1[i][0]][ipts1[i][1] - 20];
        // printf("%u,%u",x,y);
        // AT_IMAGE(&img_rp, x,y) = 0;
        rpts1[i][0] = x;
        rpts1[i][1] = y;
        rpts1_num = i + 1;
    }
    int index_max = 0;
    uint8_t temp1[120][2];
    uint8_t temp0[120][2];
    {
        resample_points(rpts1, rpts1_num, rpta1, &rpta1_num, 4);
        local_angle_points(rpta1, rpta1_num, angles1, 4);
        nms_angle(angles1, rpta1_num, angle_out1, 5);
        
        for (i = 0; i < rpta1_num; i++) {
            // printf("\n%f,%f", rpta1[i][0], rpta1[i][0]);
            temp1[i][0] = round(rpta1[i][0]) + 10;
            temp1[i][1] = round(rpta1[i][1]) + 10;
        }
        // printf("\n%d\n",i);
        for (i = 0; i < rpta1_num; i++) {
            printf("\n%f", angles1[i]);
        }

        float max = 0;
        for (i = 0; i < rpta1_num; i++) {
            if (ABS(max) < ABS(angles1[i])) {
                max = angle_out1[i];
                index_max = i;
            }
        }
        printf("\nmax: %f, index: %d\n", max, index_max);
    }
    index_max = 0;
    {
        resample_points(rpts0, rpts0_num, rpta0, &rpta0_num, 3);
        local_angle_points(rpta0, rpta0_num, angles0, 4);
        nms_angle(angles0, rpta0_num, angle_out0, 4);

        for (i = 0; i < rpta0_num; i++) {
            // printf("\n%f,%f", rpta0[i][0], rpta0[i][0]);
            temp0[i][0] = round(rpta0[i][0]) + 10;
            temp0[i][1] = round(rpta0[i][1]) + 10;
        }
        // printf("\n%d\n",i);
        for (i = 0; i < rpta0_num; i++) {
            printf("\n%f", angles0[i]);
        }

        
        float max = 0;
        for (i = 0; i < rpta0_num; i++) {
            if (ABS(max) < ABS(angle_out0[i])) {
                max = angle_out0[i];
                index_max = i;
            }
        }
       
        printf("\nmax: %f, index: %d\n", max, index_max);
    }
    
    uint8_t tempm1[120][2];
    uint8_t tempm0[120][2];
    {
        track_leftline(rpta0, rpta0_num, rptm0,5,&rptm0_num,15);
        for (i = 0; i < rptm0_num; i++) {
            // printf("\n%f,%f", rpta0[i][0], rpta0[i][0]);
            tempm0[i][0] = round(rptm0[i][0]) + 10;
            tempm0[i][1] = round(rptm0[i][1]) + 10;
        }
        printf("\n%d\n",i);
    }
    {
        track_rightline(rpta1, rpta1_num, rptm1,5,&rptm1_num,15);
        for (i = 0; i < rptm1_num; i++) {
            
            // printf("\n%f,%f", rpta0[i][0], rpta0[i][0]);
            tempm1[i][0] = round(rptm1[i][0]) + 10;
            tempm1[i][1] = round(rptm1[i][1]) + 10;
           
        }
        printf("\n%d\n",i);
        
    }

    printf("rptm1_num: %d\n",rptm1_num);
    printf("rptm0_num: %d\n",rptm0_num);
    draw_line(&img_rp, tempm0, rptm0_num);
    draw_line(&img_rp, temp0, rpta0_num);
    draw_line(&img_rp, tempm1, rptm1_num);
    draw_line(&img_rp, temp1, rpta1_num);
    
    AT(&img_rp, temp0[index_max][0], temp0[index_max][1]) = 120;
    write_img(&img_rp, "line.txt");
    printf("ok\n");
}




