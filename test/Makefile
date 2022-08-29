# main:getRoad.o imgproc.o
# 	gcc imgproc.o getRoad.o -o main
# getRoad.o:getRoad.c
# 	gcc -c getRoad.c
# imgproc.o:imgproc.c
# 	gcc -c imgproc.c 

main: test.o map.o imagePro.o
	gcc test.o map.o imagePro.o -o main
test.o: test.c
	gcc -c test.c
map.o: map.c
	gcc -c map.c
imagePro.o: imagePro.c
	gcc -c imagePro.c

.PHONY:clean

clean:
	;