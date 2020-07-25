
# Zabbix术语

## Host（主机）
一台你想监控的网络设备，用IP或域名表示。

## Item（监控项）
你想要接收的主机的特定数据，一个度量数据。

## Trigger（触发器）
一个被用于定义问题阈值和“评估”监控项接收到的数据的逻辑表达式。

## Action（动作）
一个对事件做出反应的预定义的操作，比如邮件通知。

# Zabbix使用测试

## web切换中文
![](assets/markdown-img-paste-20200725143056698.png)
![](assets/markdown-img-paste-20200725143119680.png)

![](assets/markdown-img-paste-20200725143204518.png)

## 创建Host
1）点击Configuration/Hosts/Create host
![](assets/markdown-img-paste-2020072514331670.png)

![](assets/markdown-img-paste-20200725143408796.png)

2）配置Host
![](assets/markdown-img-paste-20200725143646703.png)
![](assets/markdown-img-paste-20200725143752351.png)
添加3个
![](assets/markdown-img-paste-2020072514404777.png)

默认的主机有报错是ip地址的原因，点击名称修改一下
![](assets/markdown-img-paste-20200725144204740.png)
![](assets/markdown-img-paste-20200725144326515.png)

过一会就好了：

## 创建Item
Item必须在host中配置

1）点击Items
![](assets/markdown-img-paste-20200725144605194.png)
![](assets/markdown-img-paste-20200725144627860.png)

2）点击Create item
![](assets/markdown-img-paste-20200725144649196.png)

3）配置Item
![](assets/markdown-img-paste-20200725144733768.png)
使用监控进程数的这个键值
![](assets/markdown-img-paste-20200725145016660.png)
```
name:进程的名称，user：用户，state：进程的状态，cmdline：启动进程的命令。
proc.num[<name>,<user>,<state>,<cmdline>]

# 我使用这个，启动datanode的命令包含datanode
proc.num[,,all,datanode]
```

看看启动datanode的命令
```sh
[hadoop@hadoop101 app-script]$ ps -ef | grep datanode
hadoop    12184      1 11 22:54 ?        00:00:04 /opt/module/jdk1.8.0_144/bin/java -Dproc_datanode -Xmx1000m -Djava.net.preferIPv4Stack=true -Dhadoop.log.dir=/opt/module/hadoop-2.7.2/logs -Dhadoop.log.file=hadoop.log -Dhadoop.home.dir=/opt/module/hadoop-2.7.2 -Dhadoop.id.str=hadoop -Dhadoop.root.logger=INFO,console -Djava.library.path=/opt/module/hadoop-2.7.2/lib/native -Dhadoop.policy.file=hadoop-policy.xml -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv4Stack=true -Dhadoop.log.dir=/opt/module/hadoop-2.7.2/logs -Dhadoop.log.file=hadoop-hadoop-datanode-hadoop101.log -Dhadoop.home.dir=/opt/module/hadoop-2.7.2 -Dhadoop.id.str=hadoop -Dhadoop.root.logger=INFO,RFA -Djava.library.path=/opt/module/hadoop-2.7.2/lib/native -Dhadoop.policy.file=hadoop-policy.xml -Djava.net.preferIPv4Stack=true -server -Dhadoop.security.logger=ERROR,RFAS -Dhadoop.security.logger=ERROR,RFAS -Dhadoop.security.logger=ERROR,RFAS -Dhadoop.security.logger=INFO,RFAS org.apache.hadoop.hdfs.server.datanode.DataNode
hadoop    12418   1251  0 22:55 pts/2    00:00:00 grep datanode
```
![](assets/markdown-img-paste-20200725145720515.png)

4）查看创建的Item
![](assets/markdown-img-paste-20200725145937744.png)
![](assets/markdown-img-paste-20200725145821826.png)

5）查看Item最新数据
![](assets/markdown-img-paste-20200725150001394.png)
![](assets/markdown-img-paste-20200725150112552.png)

停止进程测试;
```
[hadoop@hadoop101 app-script]$ stop-dfs.sh 
```
![](assets/markdown-img-paste-20200725150237731.png)

## 创建Trigger

1）点击Conguration/Hosts/Triggers
![](assets/markdown-img-paste-20200725150431340.png)
![](assets/markdown-img-paste-20200725150518291.png)

2）点击Create Trigger
![](assets/markdown-img-paste-20200725150600821.png)
![](assets/markdown-img-paste-20200725150637972.png)

3）编辑Trigger
![](assets/markdown-img-paste-20200725150739610.png)
![](assets/markdown-img-paste-20200725150950802.png)

4）测试Trigger
关闭集群中的HDFS，会有如下效果
![](assets/markdown-img-paste-20200725151228661.png)

## 创建Action
1）点击Configuration/Actions/Create action
![](assets/markdown-img-paste-20200725151304514.png)
![](assets/markdown-img-paste-20200725151351907.png)

2）编辑Action
![](assets/markdown-img-paste-20200725151412776.png)
![](assets/markdown-img-paste-20200725151554168.png)

配置操作：
![](assets/markdown-img-paste-20200725151721272.png)
![](assets/markdown-img-paste-20200725151939497.png)
![](assets/markdown-img-paste-20200725152008170.png)

## 创建Media type
1）点击Administration/Media types/Email
![](assets/markdown-img-paste-20200725152206595.png)
![](assets/markdown-img-paste-20200725152255975.png)
这里是直接修改默认的，我们也可以添加自定义。

2）编辑Email
![](assets/markdown-img-paste-20200725152753265.png)
![](assets/markdown-img-paste-20200725152737146.png)

3）测试Email
![](assets/markdown-img-paste-20200725152812334.png)
![](assets/markdown-img-paste-2020072515294738.png)

4）Email绑定收件人
![](assets/markdown-img-paste-20200725153057145.png)
![](assets/markdown-img-paste-20200725153251793.png)

## 监控发邮件测试
配置完没法邮件是应为只有监控到从正常到不正常才会触发
![](assets/markdown-img-paste-20200725153418768.png)

启动dfs
```
[hadoop@hadoop101 app-script]$ start-dfs.sh
```

关闭dfs
```
[hadoop@hadoop101 app-script]$ stop-dfs.sh 
```

不知道为啥收件人配置qq邮箱没收到，又配置成163收到了
![](assets/markdown-img-paste-20200725155304257.png)

# 模板使用测试
一个一个host配置太过麻烦，实际中都是使用模板。

## 创建模板

![](assets/markdown-img-paste-2020072515594486.png)

![](assets/markdown-img-paste-20200725160230888.png)

配置监控项
![](assets/markdown-img-paste-20200725160440416.png)

配置触发器
![](assets/markdown-img-paste-20200725160641341.png)
![](assets/markdown-img-paste-20200725160953863.png)

## 应用模板
![](assets/markdown-img-paste-20200725161228211.png)
![](assets/markdown-img-paste-20200725161302534.png)
![](assets/markdown-img-paste-20200725161400943.png)
![](assets/markdown-img-paste-20200725161458608.png)

## 配置模板的动作
![](assets/markdown-img-paste-20200725161624457.png)
![](assets/markdown-img-paste-20200725161647719.png)
![](assets/markdown-img-paste-20200725161713679.png)

## 测试
启动dfs
```
[hadoop@hadoop101 app-script]$ start-dfs.sh
```

关闭dfs
```
[hadoop@hadoop101 app-script]$ stop-dfs.sh 
```

3个邮件都发出去了。1是单独定义的，2、3是用的一个模本，实际中记得都使用模板。
![](assets/markdown-img-paste-20200725162045346.png)



```

```