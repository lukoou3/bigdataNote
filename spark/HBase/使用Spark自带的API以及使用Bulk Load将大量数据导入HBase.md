[toc]

# 使用Spark自带的API以及使用Bulk Load将大量数据导入HBase
摘抄自：`https://cloud.tencent.com/developer/article/1336561`

## 1. 需要的jar包依赖

```xml
<properties>
        <spark.version>2.3.0</spark.version>
        <hbase.version>1.2.6</hbase.version>
        <scala.main.version>2.11</scala.main.version>
</properties>

<dependencies>
    <dependency>
        <groupId>org.apache.spark</groupId>
        <artifactId>spark-core_${scala.main.version}</artifactId>
        <version>${spark.version}</version>
    </dependency>
    <dependency>
        <groupId>org.apache.hbase</groupId>
        <artifactId>hbase</artifactId>
        <version>${hbase.version}</version>
    </dependency>
    <dependency>
        <groupId>org.apache.hbase</groupId>
        <artifactId>hbase-client</artifactId>
        <version>${hbase.version}</version>
    </dependency>
    <dependency>
        <groupId>org.apache.hbase</groupId>
        <artifactId>hbase-server</artifactId>
        <version>${hbase.version}</version>
    </dependency>
    <dependency>
        <groupId>org.apache.hbase</groupId>
        <artifactId>hbase-common</artifactId>
        <version>${hbase.version}</version>
    </dependency>
    
    <!-- 本文处理数据用到的解析json字符串的jar包，非必需 -->
    <dependency>
        <groupId>com.alibaba</groupId>
        <artifactId>fastjson</artifactId>
        <version>1.2.47</version>
    </dependency>
</dependencies>
```

## 2. 写数据到HBase

### (1) 使用saveAsNewAPIHadoopDataset()

```scala
package com.bonc.rdpe.spark.hbase

import com.alibaba.fastjson.JSON
import org.apache.hadoop.hbase.client._
import org.apache.hadoop.hbase.io.ImmutableBytesWritable
import org.apache.hadoop.hbase.mapreduce.TableOutputFormat
import org.apache.hadoop.hbase.util.Bytes
import org.apache.hadoop.hbase._
import org.apache.hadoop.mapred.JobConf
import org.apache.hadoop.mapreduce.Job
import org.apache.spark.{SparkConf, SparkContext}

/**
  * Author: YangYunhe
  * Description: spark 通过内置算子写数据到 HBase：使用saveAsNewAPIHadoopDataset()
  * Create: 2018/7/23 15:49
  */
object WriteHBaseWithNewHadoopAPI {

  def main(args: Array[String]): Unit = {

    val sparkConf = new SparkConf().setAppName(s"${this.getClass.getSimpleName}").setMaster("local")
    val sc = new SparkContext(sparkConf)
    val input = sc.textFile("file:///D:/data/news_profile_data.txt")
    val hbaseConf = HBaseConfiguration.create()
    hbaseConf.set(HConstants.ZOOKEEPER_QUORUM, "172.16.13.185:2181")
    val hbaseConn = ConnectionFactory.createConnection(hbaseConf)
    val admin = hbaseConn.getAdmin
    val jobConf = new JobConf(hbaseConf, this.getClass)
    // 设置表名
    jobConf.set(TableOutputFormat.OUTPUT_TABLE, "news")

    // 如果表不存在则创建表
    if (!admin.tableExists(TableName.valueOf("news"))) {
      val desc = new HTableDescriptor(TableName.valueOf("news"))
      val hcd = new HColumnDescriptor("cf1")
      desc.addFamily(hcd)
      admin.createTable(desc)
    }

    val job = Job.getInstance(jobConf)
    job.setOutputKeyClass(classOf[ImmutableBytesWritable])
    job.setOutputValueClass(classOf[Result])
    job.setOutputFormatClass(classOf[TableOutputFormat[ImmutableBytesWritable]])
    val data = input.map(jsonStr => {
      // 处理数据的逻辑
      val jsonObject = JSON.parseObject(jsonStr)
      val newsId = jsonObject.get("id").toString.trim
      val title = jsonObject.get("title").toString.trim
      val put = new Put(Bytes.toBytes(newsId))
      put.addColumn(Bytes.toBytes("cf1"), Bytes.toBytes("title"), Bytes.toBytes(title))
      (new ImmutableBytesWritable, put)
    })

    data.saveAsNewAPIHadoopDataset(job.getConfiguration)
    sc.stop()

  }
}
```

### (2) 使用saveAsHadoopDataset()

```scala
package com.bonc.rdpe.spark.hbase

import com.alibaba.fastjson.JSON
import org.apache.hadoop.hbase._
import org.apache.hadoop.hbase.client.{ConnectionFactory, Put}
import org.apache.hadoop.hbase.io.ImmutableBytesWritable
import org.apache.hadoop.hbase.mapred.TableOutputFormat
import org.apache.hadoop.hbase.util.Bytes
import org.apache.hadoop.mapred.JobConf
import org.apache.spark.{SparkConf, SparkContext}

/**
  * Author: YangYunhe
  * Description: spark 通过内置算子写数据到 HBase：使用saveAsHadoopDataset()
  * Create: 2018/7/24 11:24
  */
object WriteHBaseWithOldHadoopAPI {

  def main(args: Array[String]): Unit = {

    val sparkConf = new SparkConf().setAppName(s"${this.getClass.getSimpleName}").setMaster("local")
    val sc = new SparkContext(sparkConf)
    val input = sc.textFile("file:///D:/data/news_profile_data.txt")
    val hbaseConf = HBaseConfiguration.create()
    hbaseConf.set(HConstants.ZOOKEEPER_QUORUM, "172.16.13.185:2181")
    val hbaseConn = ConnectionFactory.createConnection(hbaseConf)
    val admin = hbaseConn.getAdmin
    val jobConf = new JobConf(hbaseConf, this.getClass)
    // 设置表名
    jobConf.set(TableOutputFormat.OUTPUT_TABLE, "news")
    jobConf.setOutputFormat(classOf[TableOutputFormat])

    // 如果表不存在则创建表
    if (!admin.tableExists(TableName.valueOf("news"))) {
      val desc = new HTableDescriptor(TableName.valueOf("news"))
      val hcd = new HColumnDescriptor("cf1")
      desc.addFamily(hcd)
      admin.createTable(desc)
    }

    val data = input.map(jsonStr => {
      // 处理数据的逻辑
      val jsonObject = JSON.parseObject(jsonStr)
      val newsId = jsonObject.get("id").toString.trim
      val title = jsonObject.get("title").toString.trim
      val put = new Put(Bytes.toBytes(newsId))
      put.addColumn(Bytes.toBytes("cf1"), Bytes.toBytes("title"), Bytes.toBytes(title))
      (new ImmutableBytesWritable, put)
    })

    data.saveAsHadoopDataset(jobConf)
    sc.stop()

  }

}
```

以上两个算子分别是基于Hadoop新版API和hadoop旧版API实现的，大部分代码都一样，需要注意的是新版API使用中Job类，旧版API使用JobConf类，另外导包的时候新版的相关jar包在org.apache.hadoop.mapreduce下，而旧版的相关jar包在org.apache.hadoop.mapred下

## 3. 从HBase读数据

以下代码使用newAPIHadoopRDD()算子

```scala
package com.bonc.rdpe.spark.hbase

import org.apache.hadoop.hbase.{Cell, CellUtil, HBaseConfiguration}
import org.apache.hadoop.hbase.client.Result
import org.apache.hadoop.hbase.io.ImmutableBytesWritable
import org.apache.hadoop.hbase.mapreduce.TableInputFormat
import org.apache.hadoop.hbase.util.Bytes
import org.apache.spark.{SparkConf, SparkContext}

import scala.collection.JavaConversions._

/**
  * Author: YangYunhe
  * Description: spark 通过内置算子读取 HBase
  * Create: 2018/7/23 15:22
  */
object ReadHBase {

  def main(args: Array[String]): Unit = {

    val sparkConf = new SparkConf().setMaster("local").setAppName(s"${this.getClass.getSimpleName}")
    sparkConf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    sparkConf.registerKryoClasses(Array(classOf[ImmutableBytesWritable]))
    val sc = new SparkContext(sparkConf)
    val hbaseConf = HBaseConfiguration.create()
    hbaseConf.set("hbase.zookeeper.quorum", "172.16.13.185:2181")
    hbaseConf.set(TableInputFormat.INPUT_TABLE, "news")

    val hBaseRDD = sc.newAPIHadoopRDD(
      hbaseConf,
      classOf[TableInputFormat],
      classOf[ImmutableBytesWritable],
      classOf[Result])

    hBaseRDD.take(10).foreach(tuple => {
      val result = tuple._2
      printResult(result)
    })

  }

  def printResult(result: Result): Unit = {
    val cells = result.listCells
    for (cell <- cells) {
      printCell(cell)
    }
  }

  def printCell(cell: Cell): Unit = {
    val str =
      s"rowkey: ${Bytes.toString(CellUtil.cloneRow(cell))}, family:${Bytes.toString(CellUtil.cloneFamily(cell))}, " +
      s"qualifier:${Bytes.toString(CellUtil.cloneQualifier(cell))}, value:${Bytes.toString(CellUtil.cloneValue(cell))}, " +
      s"timestamp:${cell.getTimestamp}"
    println(str)
  }

}
```

需要注意的是，代码中对ImmutableBytesWritable这个类进行了序列化：

```scala
sparkConf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
sparkConf.registerKryoClasses(Array(classOf[ImmutableBytesWritable]))
```

否则程序就会报错：

```scala
java.io.NotSerializableException: org.apache.hadoop.hbase.io.ImmutableBytesWritable
```

## 4. 写数据的优化：Bulk Load

以上写数据的过程将数据一条条插入到Hbase中，这种方式运行慢且在导入的过程的占用Region资源导致效率低下，所以很不适合一次性导入大量数据，解决办法就是使用 Bulk Load 方式批量导入数据。

Bulk Load 方式由于利用了 HBase 的数据信息是按照特定格式存储在 HDFS 里的这一特性，直接在 HDFS 中生成持久化的 HFile 数据格式文件，然后完成巨量数据快速入库的操作，配合 MapReduce 完成这样的操作，不占用 Region 资源，不会产生巨量的写入 I/O，所以需要较少的 CPU 和网络资源。

Bulk Load 的实现原理是通过一个 MapReduce Job 来实现的，通过 Job 直接生成一个 HBase 的内部 HFile 格式文件，用来形成一个特殊的 HBase 数据表，然后直接将数据文件加载到运行的集群中。与使用HBase API相比，使用Bulkload导入数据占用更少的CPU和网络资源。

接下来介绍在spark中如何使用 Bulk Load 方式批量导入数据到 HBase 中。

```scala
package com.bonc.rdpe.spark.hbase

import com.alibaba.fastjson.JSON
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.fs.{FileSystem, Path}
import org.apache.hadoop.hbase._
import org.apache.hadoop.hbase.client.ConnectionFactory
import org.apache.hadoop.hbase.io.ImmutableBytesWritable
import org.apache.hadoop.hbase.mapreduce.{HFileOutputFormat2, LoadIncrementalHFiles, TableOutputFormat}
import org.apache.hadoop.hbase.util.Bytes
import org.apache.hadoop.mapreduce.Job
import org.apache.spark.{SparkConf, SparkContext}

/**
  * Author: YangYunhe
  * Description: 
  * Create: 2018/7/24 13:14
  */
object BulkLoad {

  val zookeeperQuorum = "172.16.13.185:2181"
  val dataSourcePath = "file:///D:/data/news_profile_data.txt"
  val hdfsRootPath = "hdfs://beh/"
  val hFilePath = "hdfs://beh/test/yyh/hbase/bulkload/hfile/"
  val tableName = "news"
  val familyName = "cf1"
  val qualifierName = "title"

  def main(args: Array[String]): Unit = {

    val sparkConf = new SparkConf().setAppName(s"${this.getClass.getSimpleName}").setMaster("local")
    val sc = new SparkContext(sparkConf)
    val hadoopConf = new Configuration()
    hadoopConf.set("fs.defaultFS", hdfsRootPath)
    val fileSystem = FileSystem.get(hadoopConf)
    val hbaseConf = HBaseConfiguration.create(hadoopConf)
    hbaseConf.set(HConstants.ZOOKEEPER_QUORUM, zookeeperQuorum)
    hbaseConf.set(TableOutputFormat.OUTPUT_TABLE, tableName)
    val hbaseConn = ConnectionFactory.createConnection(hbaseConf)
    val admin = hbaseConn.getAdmin

    // 0. 准备程序运行的环境
    // 如果 HBase 表不存在，就创建一个新表
    if (!admin.tableExists(TableName.valueOf(tableName))) {
      val desc = new HTableDescriptor(TableName.valueOf(tableName))
      val hcd = new HColumnDescriptor(familyName)
      desc.addFamily(hcd)
      admin.createTable(desc)
    }
    // 如果存放 HFile文件的路径已经存在，就删除掉
    if(fileSystem.exists(new Path(hFilePath))) {
      fileSystem.delete(new Path(hFilePath), true)
    }

    // 1. 清洗需要存放到 HFile 中的数据，rowKey 一定要排序，否则会报错：
    // java.io.IOException: Added a key not lexically larger than previous.

    val data = sc.textFile(dataSourcePath)
      .map(jsonStr => {
        // 处理数据的逻辑
        val jsonObject = JSON.parseObject(jsonStr)
        val rowkey = jsonObject.get("id").toString.trim
        val title = jsonObject.get("title").toString.trim
        (rowkey, title)
      })
      .sortByKey()
      .map(tuple => {
        val kv = new KeyValue(Bytes.toBytes(tuple._1), Bytes.toBytes(familyName), Bytes.toBytes(qualifierName), Bytes.toBytes(tuple._2))
        (new ImmutableBytesWritable(Bytes.toBytes(tuple._1)), kv)
      })

    // 2. Save Hfiles on HDFS
    val table = hbaseConn.getTable(TableName.valueOf(tableName))
    val job = Job.getInstance(hbaseConf)
    job.setMapOutputKeyClass(classOf[ImmutableBytesWritable])
    job.setMapOutputValueClass(classOf[KeyValue])
    HFileOutputFormat2.configureIncrementalLoadMap(job, table)

    data.saveAsNewAPIHadoopFile(
      hFilePath,
      classOf[ImmutableBytesWritable],
      classOf[KeyValue],
      classOf[HFileOutputFormat2],
      hbaseConf
    )

    //  3. Bulk load Hfiles to Hbase
    val bulkLoader = new LoadIncrementalHFiles(hbaseConf)
    val regionLocator = hbaseConn.getRegionLocator(TableName.valueOf(tableName))
    bulkLoader.doBulkLoad(new Path(hFilePath), admin, table, regionLocator)

    hbaseConn.close()
    fileSystem.close()
    sc.stop()
  }
}
```

说明：

* rowkey一定要进行排序    
* 上面的代码使用了saveAsNewAPIHadoopFile()，也可以使用saveAsNewAPIHadoopDataset()，把以下代码：

```scala
data.saveAsNewAPIHadoopFile(
  hFilePath,
  classOf[ImmutableBytesWritable],
  classOf[KeyValue],
  classOf[HFileOutputFormat2],
  hbaseConf
)
```

替换为：

```scala
job.getConfiguration.set("mapred.output.dir", hFilePath)
data.saveAsNewAPIHadoopDataset(job.getConfiguration)
```

即可。

参考文章：

* [Spark读取Hbase中的数据](https://www.iteblog.com/archives/1051.html "Spark读取Hbase中的数据")    
* [使用Spark读取HBase中的数据](https://www.iteblog.com/archives/1892.html "使用Spark读取HBase中的数据")    
* [在Spark上通过BulkLoad快速将海量数据导入到Hbase](https://www.iteblog.com/archives/1891.html "在Spark上通过BulkLoad快速将海量数据导入到Hbase")    
* [Spark doBulkLoad数据进入hbase](https://blog.csdn.net/qq_25954159/article/details/52848947 "Spark doBulkLoad数据进入hbase")

