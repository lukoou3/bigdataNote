#### 1 安装前的准备

```
1. 安装一个JDK8
2. 安装HDFS的环境
```

#### 2 安装单机节点

```
1. 下载Hbase的镜像
2. 解压到指定的目录中
[root@min1 apps]# mkdir hbase
[root@min1 apps]# cd /home/
[root@min1 home]# tar -zxvf hbase-1.2.1-bin.tar.gz -C /usr/apps/hbase/

3. 修改hbase-env.sh

# The java implementation to use.  Java 1.7+ required.
export JAVA_HOME=/usr/apps/java/jdk1.8.0_45

# Configure PermSize. Only needed in JDK7. You can safely remove it for JDK8+
# export HBASE_MASTER_OPTS="$HBASE_MASTER_OPTS -XX:PermSize=128m -XX:MaxPermSize=128m"
# export HBASE_REGIONSERVER_OPTS="$HBASE_REGIONSERVER_OPTS -XX:PermSize=128m -XX:MaxPermSize=128m"

# Tell HBase whether it should manage it's own instance of Zookeeper or not.
export HBASE_MANAGES_ZK=true

4. 修改hbase-site.xml

<configuration>
        <property>
                <name>hbase.rootdir</name>
                <value>file:///usr/apps/hbase/tmp</value>
        </property>
        <property>
                <name>hbase.zookeeper.property.dataDir</name>
                <value>/usr/apps/hbase/zookeeper</value>
        </property>
</configuration>

5 启动HBase
start-hbase.sh

./hbase shell
SLF4J: Class path contains multiple SLF4J bindings.
SLF4J: Found binding in [jar:file:/usr/apps/hbase/hbase-1.2.1/lib/slf4j-log4j12-1.7.5.jar!/org/slf4j/impl/StaticLoggerBinder.class]
SLF4J: Found binding in [jar:file:/usr/apps/hadoop/hadoop-2.8.1/share/hadoop/common/lib/slf4j-log4j12-1.7.10.jar!/org/slf4j/impl/StaticLoggerBinder.class]
SLF4J: See http://www.slf4j.org/codes.html#multiple_bindings for an explanation.
SLF4J: Actual binding is of type [org.slf4j.impl.Log4jLoggerFactory]
HBase Shell; enter 'help<RETURN>' for list of supported commands.
Type "exit<RETURN>" to leave the HBase Shell
Version 1.2.1, r8d8a7107dc4ccbf36a92f64675dc60392f85c015, Wed Mar 30 11:19:21 CDT 2016

hbase(main):001:0>

```

