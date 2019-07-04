## Flume安装
1、Flume的安装非常简单，只需要解压即可，当然，前提是已有hadoop环境
上传安装包到数据源所在节点上
然后解压  tar -zxvf apache-flume-1.6.0-bin.tar.gz
然后进入flume的目录，修改conf下的flume-env.sh，在里面配置JAVA_HOME

2、根据数据采集的需求配置采集方案，描述在配置文件中(文件名可任意自定义)

3、指定采集方案配置文件，在相应的节点上启动flume agent


### Flume官网地址
1） Flume官网地址
http://flume.apache.org/

2）文档查看地址
http://flume.apache.org/FlumeUserGuide.html

3）下载地址
http://archive.apache.org/dist/flume/

### Flume安装部署
解压apache-flume-1.7.0-bin.tar.gz
```shell
tar -zxvf apache-flume-1.7.0-bin.tar.gz  -C apps/
```

配置环境变量
```
mv apache-flume-1.7.0-bin/ flume-1.7.0

sudo vi /etc/profile

source /etc/profile
```

**将flume/conf下的flume-env.sh.template文件修改为flume-env.sh，并配置flume-env.sh文件（配置JAVA_HOME）**
```
cp flume-env.sh.template flume-env.sh

vi flume-env.sh

export JAVA_HOME=/usr/local/jdk1.7.0_79
```







