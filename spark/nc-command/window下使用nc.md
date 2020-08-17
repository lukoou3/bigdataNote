
总结：
```sh
linux: nc -lk 9999
windows: nc -l -p 9999
```


spark streaming官方教程有个NetworkWordCount例子，通过 TCP 套接字连接，从流数据中创建了一个 DStream，然后进行处理，时间窗口大小为10s 。

不过nc这个命令默认在window中没有，测试学习不是很方便。下载一个nc.exe，放到环境变量中后就可以使用了。

**下载nc**：

下载netcat,地址：https://eternallybored.org/misc/netcat/

下载1.12，1.11都行。

**放到环境变量中**：

把nc.exe放到`C:\Windows`即可。

windows cmd中使用`nc -l -p 9999`命令即可。



