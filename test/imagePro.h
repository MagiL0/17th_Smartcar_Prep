/*
 * @Author: FYB
 * @Description: GitHub: https://github.com/magil0
 */
#ifndef __IMAGEPRO_H
#define __IMAGEPRO_H


#define IMGH 120
#define IMGW 160
#define uint8_t unsigned char
#define uint32_t unsigned long

typedef struct image {
    uint8_t *data;
    uint32_t width;
    uint32_t height;
    uint32_t step;
} image_t;


//AT_IMAGE，img为一维图片数据指针 ，x,y为所查找像素点的位置
#define AT_IMAGE(img, x, y)          ((img)->data[((img)->step) * (y)+(x)])
//img为一维图片数据指针 ，x,y为所查找像素点的位置，该宏可以避免越界
#define AT_IMAGE_CLIP(img, x, y)     AT_IMAGE(img, clip(x, 0, (img)->width-1), clip(y, 0, (img)->height-1))

#define AT                  AT_IMAGE
//img为一维图片数据指针 ，x,y为所查找像素点的位置，该宏可以避免越界
#define AT_CLIP(img, x, y)  AT_IMAGE((img), clip((x), 0, (img)->width-1), clip((y), 0, (img)->height-1));

void adaptive_threshold(image_t *img0, image_t *img1, int block_size, int down_value, uint8_t low_value, uint8_t high_value) ;
void findline_lefthand_adaptive(image_t *img, int block_size, int clip_value, int x, int y, uint8_t pts[][2], int *num) ;
void findline_righthand_adaptive(image_t *img, int block_size, int clip_value, int x, int y, uint8_t pts[][2], int *num) ;
void resample_points(uint8_t pts_in[][2], uint8_t num1, float pts_out[][2], uint8_t *num2, float dist);
void local_angle_points(float pts_in[][2], uint8_t num, float angle_out[], int dist);
void nms_angle(float angle_in[], uint8_t num, float angle_out[], int kernel);
int clip(int x, int low, int up);
void track_rightline(float pts_in[][2], unsigned char num, float pts_out[][2], int approx_num, unsigned char* num1, float dist);
void track_leftline(float pts_in[][2], unsigned char num, float pts_out[][2], int approx_num, unsigned char* num1, float dist);

#endif