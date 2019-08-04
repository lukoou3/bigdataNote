## 一、Sqoop 简介
Sqoop是一款开源的工具，主要用于在Hadoop(Hive)与传统的数据库(mysql、postgresql...)间进行数据的传递，可以将一个关系型数据库（例如 ： MySQL ,Oracle ,Postgres等）中的数据导进到Hadoop的HDFS中，也可以将HDFS的数据导进到关系型数据库中。

Sqoop项目开始于2009年，最早是作为Hadoop的一个第三方模块存在，后来为了让使用者能够快速部署，也为了让开发人员能够更快速的迭代开发，Sqoop独立成为一个Apache项目。

Sqoop2的最新版本是1.99.7。请注意，2与1不兼容，且特征不完整，它并不打算用于生产部署。
## 二、Sqoop 原理
将导入或导出命令翻译成 mapreduce 程序来实现。
在翻译出的 mapreduce 中主要是对 inputformat 和 outputformat 进行定制。

## 三、Sqoop 安装
安装 Sqoop 的前提是已经具备 Java 和 Hadoop 的环境。


**将来sqoop在使用的时候有可能会跟那些系统或者组件打交道？**

HDFS， MapReduce， YARN， ZooKeeper， Hive， HBase， MySQL

**sqoop就是一个工具， 只需要在一个节点上进行安装即可。**

 
```
补充一点： 如果你的sqoop工具将来要进行hive或者hbase等等的系统和MySQL之间的交互
你安装的SQOOP软件的节点一定要包含以上你要使用的集群或者软件系统的安装包

补充一点： 将来要使用的azakban这个软件 除了会调度 hadoop的任务或者hbase或者hive的任务之外， 还会调度sqoop的任务
azkaban这个软件的安装节点也必须包含以上这些软件系统的客户端
```
#### 下载并解压
解压：
```
tar -zxvf sqoop-1.4.6.bin__hadoop-2.0.4-alpha.tar.gz -C apps/
```

#### 修改配置文件
Sqoop 的配置文件与大多数大数据框架类似，在 sqoop 根目录下的 conf 目录中。

重命名配置文件
```shell
$ mv sqoop-env-template.sh sqoop-env.sh
$ mv sqoop-site-template.xml sqoop-site.xml
```


修改配置文件`sqoop-env.sh`

```
#Set path to where bin/hadoop is available
export HADOOP_COMMON_HOME=/home/hadoop/apps/hadoop-2.6.4

#Set path to where hadoop-*-core.jar is available
export HADOOP_MAPRED_HOME=/home/hadoop/apps/hadoop-2.6.4

#set the path to where bin/hbase is available
#export HBASE_HOME=/home/hadoop/apps/hbase-1.3.1

#Set the path to where bin/hive is available
export HIVE_HOME=/home/hadoop/apps/hive-1.2.1

#Set the path for where zookeper config dir is
#export ZOOCFGDIR=
```
由于hbase和zookeper还没安装暂时没设置

为什么在sqoop-env.sh 文件中会要求分别进行 common和mapreduce的配置呢？？？
```
在apache的hadoop的安装中；四大组件都是安装在同一个hadoop_home中的
但是在CDH, HDP中， 这些组件都是可选的。
在安装hadoop的时候，可以选择性的只安装HDFS或者YARN，
CDH,HDP在安装hadoop的时候，会把HDFS和MapReduce有可能分别安装在不同的地方。
```
#### 拷贝 JDBC 驱动
拷贝 jdbc 驱动到 sqoop 的 lib 目录下，如：
```
cp hive-1.2.1/lib/mysql-connector-java-5.1.27-bin.jar  sqoop-1.4.6/lib/
```

#### 验证 Sqoop
我们可以通过某一个 command 来验证 sqoop 配置是否正确：
```
$ bin/sqoop help
出现一些 Warning 警告（警告信息已省略），并伴随着帮助命令的输出：
Available commands:
  codegen            Generate code to interact with database records
  create-hive-table  Import a table definition into Hive
  eval               Evaluate a SQL statement and display the results
  export             Export an HDFS directory to a database table
  help               List available commands
  import             Import a table from a database to HDFS
  import-all-tables  Import tables from a database to HDFS
  import-mainframe   Import datasets from a mainframe server to HDFS
  job                Work with saved jobs
  list-databases     List available databases on a server
  list-tables        List available tables in a database
  merge              Merge results of incremental imports
  metastore          Run a standalone Sqoop metastore
  version            Display version information

See 'sqoop help COMMAND' for information on a specific command.
```

#### 测试 Sqoop 是否能够成功连接数据库
查询mysql中的数据库:
```
sqoop list-databases --connect jdbc:mysql://localhost:3306/ --username root --password 123456
```

## 四、sqoop中的报错解决
#### The last packet sent successfully to the server was 0 milliseconds ago. The driver has not received any packets from the server.
修改bind-address = 127.0.0.1
为 bind-address = 0.0.0.0
```
sudo find / -name my.cnf
sudo vi /usr/my.cnf
sudo service mysql restart
```
不行，主机名就不写localhost写其它的试试

#### ERROR tool.ImportTool:Import failed: java.io.IOException: java.lang.ClassNotFoundException: org.apache.hadoop.hive.conf.HiveConf

这是因为sqoop需要一个hive的包，将hive/lib中的hive-common-2.3.3.jar拷贝到sqoop的lib目录中

#### java.lang.ClassNotFoundException: org.apache.hadoop.hive.shims.ShimLoader
解决办法：
拷贝 hive lib 包下 hive-exec-1.2.2.jar 至 sqoop 的lib包下
```
cp hive-1.2.2/lib/hive-exec-1.2.2.jar sqoop-1.4.6/lib/
```