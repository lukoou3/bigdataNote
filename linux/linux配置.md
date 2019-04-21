#### Linux开机界面设置
让Linux启动时自动进入图形化界面方法：编辑/etc/inittab文件，找到这行代码：id:3:initdefault:，它定义Linux进入系统后执行的init动作级别，共有以下6个级别：

　　级别0，挂起、关机模式;

　　级别1，单用户模式;

　　级别2，多用户模式，但没有网络功能;

　　级别3，全功能的单用户模式;

　　级别4，没用到;

　　级别5，X11模式，也就是图形化界面模式;

　　级别6，重起模式。

很明显，要自动进入图形化界面，将3改成5即可。注意千万不要设成0或6，否则Linux开机后进入系统就会自动关机或自动重起。


Linux/Centos中修改为无界面模式（命令行模式）：
···
vim /etc/inittab
···
在默认的 run level 设置中,找到这行代码：id:5:initdefault:(默认的 run level 等级为 5,即图形界面)将 5 修改为 3 即可。

#### centos安装tree命令
```
sudo yum -y install tree
```