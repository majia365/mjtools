# mjtools
majia tool package


## ffmpegbili.py

使用`ffmpeg`处理`bilibili`客户端缓存文件（格式为视频音频分离的`.m4s`文件），单个/批量打包为相应`.mp4`文件。

可通过命令行指定处理目录，或使用配置文件`ffmpegbili.conf`指定缺省目录。以满足个别盘容量不足的情况。

todo: 由于视频文件普遍较大，可考虑加一个删除源文件的选项，在打包处理完成后，自动删除缓存文件，释放磁盘空间。


## ffconcat.sh

由于`bilibili`很多影片以分片方式发布，在使用`ffmpegbili.py`处理后，还是单个`.mp4`文件，使用本脚本进行合并处理。

参数传递需要打包的文件名前缀，支持传入多个前缀一次处理。如，

``` bash
ffconcat.sh "天下" "银魂"

分别处理`天下****.px.mp4`以及`银魂****.px.mp4`
```



