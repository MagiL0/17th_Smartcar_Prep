<!--
 * @Author: FYB
 * @Description: GitHub: https://github.com/magil0
-->
**该文件用于测试图像算法**
- `image.h` 储存产生的二进制灰度文件
- `imagePro` `imagePro.c`储存图像算法
- `test.c` 产生最终输出的 `line.txt` 文件，可供 `opencv` 读取
- `map.c` 是映射表，将每个像素点投射到仿射变换后的效果
增加 .c 文件请修改 makefile