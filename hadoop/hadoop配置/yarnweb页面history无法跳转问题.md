yarnweb页面history无法跳转问题：需要配置历史服务器和日志的聚集

## 配置历史服务器和日志的聚集

#### 配置历史服务器
1）配置mapred-site.xml
```
<property>
<name>mapreduce.jobhistory.address</name>
<value>hadoop01:10020</value>
</property>
<property>
    <name>mapreduce.jobhistory.webapp.address</name>
    <value>hadoop01:19888</value>
</property>
```

```
<property>
        <name>mapreduce.jobhistory.address</name>
        <value>master:10020</value>
        <description>MR JobHistory Server管理的日志的存放位置</description>
</property>
<property>
        <name>mapreduce.jobhistory.webapp.address</name>
        <value>master:19888</value>
        <description>查看历史服务器已经运行完的Mapreduce作业记录的web地址，需要启动该服务才行</description>
</property>
<property>
        <name>mapreduce.jobhistory.done-dir</name>
        <value>/mr-history/done</value>
        <description>MR JobHistory Server管理的日志的存放位置,默认:/mr-history/done</description>
</property>
<property>
        <name>mapreduce.jobhistory.intermediate-done-dir</name>
        <value>/mr-history/mapred/tmp</value>
        <description>MapReduce作业产生的日志存放位置，默认值:/mr-history/tmp</description>
</property>
```
2）查看启动历史服务器文件目录：
```
[root@hadoop101 hadoop-2.7.2]# ls sbin/ |grep mr
mr-jobhistory-daemon.sh
```

3）启动历史服务器
```
sbin/mr-jobhistory-daemon.sh start historyserver
```

4）查看历史服务器是否启动
jps

5）查看jobhistory
http://hadoop01:19888/jobhistory

#### 日志的聚集
日志聚集概念：应用运行完成以后，将日志信息上传到HDFS系统上

开启日志聚集功能步骤：

（1）配置yarn-site.xml
```
<!-- 日志聚集功能使能 -->
<property>
<name>yarn.log-aggregation-enable</name>
<value>true</value>
</property>
<!-- 日志保留时间设置7天 -->
<property>
<name>yarn.log-aggregation.retain-seconds</name>
<value>604800</value>
</property>
```

（2）关闭nodemanager 、resourcemanager和historymanager
```
sbin/yarn-daemon.sh stop resourcemanager
sbin/yarn-daemon.sh stop nodemanager
sbin/mr-jobhistory-daemon.sh stop historyserver
```

（3）启动nodemanager 、resourcemanager和historymanager
```
sbin/yarn-daemon.sh start resourcemanager
sbin/yarn-daemon.sh start nodemanager
sbin/mr-jobhistory-daemon.sh start historyserver
```

（4）查看日志
http://192.168.1.101:19888/jobhistory













