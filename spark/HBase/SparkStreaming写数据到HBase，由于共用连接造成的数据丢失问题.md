[toc]

# SparkStreaming 写数据到 HBase，由于共用连接造成的数据丢失问题
摘抄自：`https://cloud.tencent.com/developer/article/1336581`

有如下程序，SparkStreaming 读取 Kafka 中的数据，经过处理后，把数据写入到 Hbase 中

```scala
/**
  * Author: Jed
  * Description: SparkStreaming 读取 Kafka 中的数据，实时写入 HBase中
  * Create: 2018-05-04 14:50
  */
object HBaseTest {

  def main(args: Array[String]): Unit = {

    val sparkConf = new SparkConf().setAppName(s"${this.getClass.getSimpleName}").setMaster("local[*]")
    val sc = new SparkContext(sparkConf)
    val ssc = new StreamingContext(sc, Seconds(2))

    val kafkaParams = Map[String, AnyRef](
      "bootstrap.servers" -> "172.16.26.6:9092,172.16.26.10:9092,172.16.26.13:9092",
      "key.deserializer" -> classOf[StringDeserializer],
      "value.deserializer" -> classOf[StringDeserializer],
      "auto.offset.reset" -> "latest"
      "group.id" -> s"GROUP${new Random().nextInt(1000)}"
    )

    val topics = Array("baihe")

    val stream: InputDStream[ConsumerRecord[String, String]] = KafkaUtils.createDirectStream[String, String](
      ssc,
      PreferConsistent,
      Subscribe[String, String](topics, kafkaParams)
    )

    val values: DStream[Array[String]] = stream.map(_.value.split("\\|"))

    values.foreachRDD(rdd => {
      rdd.foreachPartition(partition => {
        val connection = HBaseUtil.getConnection
        val tableName = TableName.valueOf("test")
        val table = connection.getTable(tableName)
        val puts = new ArrayList[Put]

        try {
          partition.foreach(arr => {

            val put = new Put(CustomerFunction.genRowkey(arr(0)))
            val index = Array[Int](0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            val enNames = Array[String]("touched", "user_number", "start_time", "end_time", "channel_id", "binding_flag", "click_path", "result", "interf_name", "channel_category", "by_operator")
            var value = ""
            for (i <- 0 until index.length) {
              value += arr(i) + "|"
            }
            value = value.dropRight(1)
            put.addColumn(Bytes.toBytes("f"), Bytes.toBytes("q"), Bytes.toBytes(value))
            puts.add(put)
            // 这里为了提高性能，每一万条入一次HBase库
            if (puts.size % 10000 == 0) {
              table.put(puts)
              puts.clear()
            }
          })
        } catch {
          case e: Exception => e.printStackTrace
        } finally {
          table.put(puts)
          table.close
          connection.close
        }
      })
    })

    ssc.start
    ssc.awaitTermination
  }
}


object HBaseUtil {

  var conf: Configuration = null
  var connection: Connection = null

  def getConnection(): Connection = {

    if (conf == null) {
      conf.set("hbase.zookeeper.quorum", "172.16.26.6:2181,172.16.26.10:2181,172.16.26.13:2181")
    }

    if ((connection == null || connection.isClosed()) && conf != null) {
      try {
        connection = ConnectionFactory.createConnection(conf)
      } catch {
        case e: Exception => e.printStackTrace()
      }
    }
    return connection;
  }

  def colse() = {
    if (connection != null) {
      try {
        connection.close();
      } catch {
        case e: Exception => e.printStackTrace()
      }
    }
  }
}
```

执行以上程序，中途会报错：

```scala
2018-05-29 16:21:40 883 [ERROR] org.apache.hadoop.hbase.client.AsyncProcess.submit(AsyncProcess.java:432) Failed to get region location 
org.apache.hadoop.hbase.DoNotRetryIOException: hconnection-0x6432ad81 closed
    at org.apache.hadoop.hbase.client.ConnectionManager$HConnectionImplementation.locateRegion(ConnectionManager.java:1174)
    at org.apache.hadoop.hbase.client.AsyncProcess.submit(AsyncProcess.java:422)
    at org.apache.hadoop.hbase.client.AsyncProcess.submit(AsyncProcess.java:371)
    at org.apache.hadoop.hbase.client.BufferedMutatorImpl.backgroundFlushCommits(BufferedMutatorImpl.java:245)
    at org.apache.hadoop.hbase.client.BufferedMutatorImpl.flush(BufferedMutatorImpl.java:197)
    at org.apache.hadoop.hbase.client.HTable.flushCommits(HTable.java:1461)
    at org.apache.hadoop.hbase.client.HTable.put(HTable.java:1029)
```

重点是：**hconnection-0x6432ad81 closed**问题出在获得连接的工具类中，在 DStream 中的每个 partition 中获得中一个 HBase 的连接，为了提高"效率"，让每个 partition 共用了一个 connection，但就是这样，才导致了问题的出现，假设 A partition 中有 10000 条数据，B partition 中有 20000 条数据，两个 partition 共用一个 connection，A、B两个 partition 并行的往 HBase 中写数据，当 A partition 写完10000条数据后，关闭了 connection，假设此时 B partition 也已经写入了10000条数据，但它还有 10000 条数据要写，连接却关闭了，程序会报以上的错误，数据会丢失 10000 条

解决办法就是**让每个 partition 获得独立的 connection**，只需要把 HBaseUtil 类修改如下即可：

```scala
object HBaseUtil {
  val conf: Configuration = HBaseConfiguration.create()
  conf.set("hbase.zookeeper.quorum", "192.168.42.101:2181,192.168.42.102:2181,192.168.42.101:2181")
  def getConnection(): Connection = {
    return ConnectionFactory.createConnection(conf)
  }
}
```

我的看法：其实也可以每个jvm进程公用一个connection，使用单例对象，程序关闭时关闭connection。

