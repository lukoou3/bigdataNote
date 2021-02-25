# 自定义data-source(HBaseRelation查看)

通过阅读hbase的api查看

## DefaultSource

`org.apache.spark.sql.execution.datasources.hbase`包下HBaseRelation.scala文件的DefaultSource类
```scala
package org.apache.spark.sql.execution.datasources.hbase

/**
 * val people = sqlContext.read.format("org.apache.spark.sql.execution.datasources.hbase").load("people")
 */
private[sql] class DefaultSource extends RelationProvider with CreatableRelationProvider {//with DataSourceRegister {

  //override def shortName(): String = "hbase"

  // read、load的时候调用
  override def createRelation(
      sqlContext: SQLContext,
      parameters: Map[String, String]): BaseRelation = {
    HBaseRelation(parameters, None)(sqlContext)
  }

  // write、save的时候调用
  override def createRelation(
    sqlContext: SQLContext,
    mode: SaveMode,
    parameters: Map[String, String],
    data: DataFrame): BaseRelation = {
    val relation = HBaseRelation(parameters, Some(data.schema))(sqlContext)
    relation.createTableIfNotExist()
    relation.insert(data, false)
    relation
  }
}
```
read、write都是通过HBaseRelation类实现的。



实现RelationProvider接口，实现createRelation方法返回BaseRelation对象用于load DataFrame。
```scala
package org.apache.spark.sql.sources

/**
 * Implemented by objects that produce relations for a specific kind of data source.  When
 * Spark SQL is given a DDL operation with a USING clause specified (to specify the implemented
 * RelationProvider), this interface is used to pass in the parameters specified by a user.
 *
 * Users may specify the fully qualified class name of a given data source.  When that class is
 * not found Spark SQL will append the class name `DefaultSource` to the path, allowing for
 * less verbose invocation.  For example, 'org.apache.spark.sql.json' would resolve to the
 * data source 'org.apache.spark.sql.json.DefaultSource'
 *
 * A new instance of this class will be instantiated each time a DDL call is made.
 *
 * @since 1.3.0
 */
@InterfaceStability.Stable
trait RelationProvider {
  /**
   * Returns a new base relation with the given parameters.
   *
   * @note The parameters' keywords are case insensitive and this insensitivity is enforced
   * by the Map that is passed to the function.
   */
  def createRelation(sqlContext: SQLContext, parameters: Map[String, String]): BaseRelation
}
```


实现CreatableRelationProvider接口，实现createRelation方法返回BaseRelation对象，在createRelation方法中save参数传入的DataFrame。
```scala
package org.apache.spark.sql.sources

/**
 * @since 1.3.0
 */
@InterfaceStability.Stable
trait CreatableRelationProvider {
  /**
   * Saves a DataFrame to a destination (using data source-specific parameters)
   *
   * @param sqlContext SQLContext
   * @param mode specifies what happens when the destination already exists
   * @param parameters data source-specific parameters
   * @param data DataFrame to save (i.e. the rows after executing the query)
   * @return Relation with a known schema
   *
   * @since 1.3.0
   */
  def createRelation(
      sqlContext: SQLContext,
      mode: SaveMode,
      parameters: Map[String, String],
      data: DataFrame): BaseRelation
}
```

## HBaseRelation

### HBaseRelation实现的接口
```scala
case class HBaseRelation(
    parameters: Map[String, String],
    userSpecifiedschema: Option[StructType]
  )(@transient val sqlContext: SQLContext)
  extends BaseRelation with PrunedFilteredScan with InsertableRelation with Logging {

  val catalog = HBaseTableCatalog(parameters)
  
  /**
   *
   * @param data DataFrame to write to hbase
   * @param overwrite Overwrite existing values
   */
  override def insert(data: DataFrame, overwrite: Boolean): Unit = {
    //...
  }  

  override val schema: StructType = userSpecifiedschema.getOrElse(catalog.toDataType)

  // Tell Spark about filters that has not handled by HBase as opposed to returning all the filters
  override def unhandledFilters(filters: Array[Filter]): Array[Filter] = {
    filters.filter(!HBaseFilter.buildFilter(_, this).handled)
  }

  def buildScan(requiredColumns: Array[String], filters: Array[Filter]): RDD[Row] = {
    new HBaseTableScanRDD(this, requiredColumns, filters)
  }
}
```


BaseRelation是Spark提供的一个标准的接口，如果要实现自己的外部数据源，必须要实现它里面的一些方法。
```scala
// 必须实现sqlContext、schema两个抽象方法
abstract class BaseRelation {
  def sqlContext: SQLContext
  def schema: StructType

  def sizeInBytes: Long = sqlContext.conf.defaultSizeInBytes

  def needConversion: Boolean = true

  def unhandledFilters(filters: Array[Filter]): Array[Filter] = filters
}
```

```scala
// 一种BaseRelation，支持过滤列
// //可以理解为select a,b from xxx where a>10  读取需要的列，再进行过滤，变成RDD[Row]
@InterfaceStability.Stable
trait PrunedFilteredScan {
  def buildScan(requiredColumns: Array[String], filters: Array[Filter]): RDD[Row]
}
```


```scala
// 支持write、save
trait InsertableRelation {
  def insert(data: DataFrame, overwrite: Boolean): Unit
}
```

### interfaces.scala中常见的一些trait
摘抄自网络:`https://blog.csdn.net/liweihope/article/details/94781588`


下面是`org.apache.spark.sql.sources`包下interfaces.scala中常见的一些接口：

下面各种类、方法，在源码里面都有详细的注释。

```scala
//Spark提供的一个标准的接口
//如果要实现自己的外部数据源，必须要实现它里面的一些方法
//这个里面是含有schema的元组集合（字段:字段类型）
//继承了BaseRelation的类，必须以StructType这个形式产生数据的schema
//继承了`Scan`类之后，要实现它里面的相应的方法
@InterfaceStability.Stable
abstract class BaseRelation {
  def sqlContext: SQLContext
  def schema: StructType
.....
}

//A BaseRelation that can produce all of its tuples as an RDD of Row objects.
//读取数据，构建RDD[ROW]
//可以理解为select * from xxx   把所有数据读取出来变成RDD[Row]
trait TableScan {
  def buildScan(): RDD[Row]
}

//A BaseRelation that can eliminate unneeded columns before producing an RDD 
//containing all of its tuples as Row objects.
//可以理解为select a,b from xxx   读取需要的列变成RDD[Row]
trait PrunedScan {
  def buildScan(requiredColumns: Array[String]): RDD[Row]
}

//可以理解为select a,b from xxx where a>10  读取需要的列，再进行过滤，变成RDD[Row]
trait PrunedFilteredScan {
  def buildScan(requiredColumns: Array[String], filters: Array[Filter]): RDD[Row]
}

//写数据，插入数据，无返回
trait InsertableRelation {
  def insert(data: DataFrame, overwrite: Boolean): Unit
}

trait CatalystScan {
  def buildScan(requiredColumns: Seq[Attribute], filters: Seq[Expression]): RDD[Row]
}



//用来创建上面的BaseRelation
//传进来指定数据源的参数：比如url、dbtable、user、password等（这个就是你要连接的那个数据源）
//最后返回BaseRelation（已经带有了传进来参数的属性了）
trait RelationProvider {
  def createRelation(sqlContext: SQLContext, parameters: Map[String, String]): BaseRelation
}

// Saves a DataFrame to a destination (using data source-specific parameters)
//mode: SaveMode，当目标已经存在，是用什么方式保存
//parameters: Map[String, String] ：指定的数据源参数
//要保存的DataFrame，比如执行查询之后的rows
//返回BaseRelation
trait CreatableRelationProvider {
  def createRelation(
      sqlContext: SQLContext,
      mode: SaveMode,
      parameters: Map[String, String],
      data: DataFrame): BaseRelation
}

//把你的数据源起一个简短的别名
trait DataSourceRegister {
//override def shortName(): String = "parquet"（举例）
  def shortName(): String
}

//比CreatableRelationProvider多了个schema参数
trait SchemaRelationProvider {
  def createRelation(
      sqlContext: SQLContext,
      parameters: Map[String, String],
      schema: StructType): BaseRelation
}

```

### HBaseRelation的构造方法
case class 竟然也能使用多参数列表函数语法，学到了。
```scala
// parameters：可以读取option设置的参数
// userSpecifiedschema：获取schema
// sqlContext：这个巧妙地重写了BaseRelation的sqlContext抽象方法(scala的语法)
case class HBaseRelation(
    parameters: Map[String, String],
    userSpecifiedschema: Option[StructType]
  )(@transient val sqlContext: SQLContext)
  extends BaseRelation with PrunedFilteredScan with InsertableRelation with Logging
```

### catalog
catalog字段就是解析后的catalog，在options中配置。里面有spark table和hbase表的对应关系。
```scala
  val catalog = HBaseTableCatalog(parameters)
```

### hbaseConf
可以通过hbase-site.xml配置参数，看代码似乎也可以通过"hbaseConfiguration"配置json类型的参数，"hbaseConfigFile"配置xml类型的参数。
```scala
private val wrappedConf = {
  implicit val formats = DefaultFormats
  val hConf = {
    val testConf = sqlContext.sparkContext.conf.getBoolean(SparkHBaseConf.testConf, false)
    if (testConf) {
      SparkHBaseConf.conf
    } else {
      // HBASE_CONFIGURATION = "hbaseConfiguration"
      // 配置json类型的参数
      val hBaseConfiguration = parameters.get(HBaseRelation.HBASE_CONFIGURATION).map(
        parse(_).extract[Map[String, String]])

      // HBASE_CONFIGFILE = "hbaseConfigFile"
      // 加载xml配置文件
      val cFile = parameters.get(HBaseRelation.HBASE_CONFIGFILE)
      val hBaseConfigFile = {
        var confMap: Map[String, String] = Map.empty
        if (cFile.isDefined) {
          val xmlFile = XML.loadFile(cFile.get)
          (xmlFile \\ "property").foreach(
            x => { confMap += ((x \ "name").text -> (x \ "value").text) })
        }
        confMap
      }

      val conf = HBaseConfiguration.create
      hBaseConfiguration.foreach(_.foreach(e => conf.set(e._1, e._2)))
      hBaseConfigFile.foreach(e => conf.set(e._1, e._2))
      conf
    }
  }
  // task is already broadcast; since hConf is per HBaseRelation (currently), broadcast'ing
  // it again does not help - it actually hurts. When we add support for
  // caching hConf across HBaseRelation, we can revisit broadcast'ing it (with a caching
  // mechanism in place)
  new SerializableConfiguration(hConf)
}

def hbaseConf = wrappedConf.value

val serializedToken = SHCCredentialsManager.manager.getTokenForCluster(hbaseConf)
```

### insert方法(save的实现)
insert方法中还嵌套一个convertToPut函数，转换`(row: Row) => (ImmutableBytesWritable, Put)`

read和write比较还是write好实现，直接对DataFrame处理即可，其它的都是解析参数，解析表的映射关系等。

insert方法内部也是通过调用saveAsNewAPIHadoopDataset实现保存，这个我们自己也完全能够实现。
```scala
/**
 *
 * @param data DataFrame to write to hbase
 * @param overwrite Overwrite existing values
 */
override def insert(data: DataFrame, overwrite: Boolean): Unit = {
  hbaseConf.set(TableOutputFormat.OUTPUT_TABLE, s"${catalog.namespace}:${catalog.name}")
  val job = Job.getInstance(hbaseConf)
  job.setOutputFormatClass(classOf[TableOutputFormat[String]])

  // This is a workaround for SPARK-21549. After it is fixed, the snippet can be removed.
  val jobConfig = job.getConfiguration
  val tempDir = Utils.createTempDir()
  if (jobConfig.get("mapreduce.output.fileoutputformat.outputdir") == null) {
    jobConfig.set("mapreduce.output.fileoutputformat.outputdir", tempDir.getPath + "/outputDataset")
  }
  
  // 上面的都是配置，固定的套路，不用看。

  var count = 0
  val rkFields = catalog.getRowKey
  // Seq[(Int, Field)]，rowkey对应的列
  val rkIdxedFields = rkFields.map{ case x =>
    (schema.fieldIndex(x.colName), x)
  }
  // Array[(Int, Field)]，正常的列
  // partition后._2返回的是正常的列
  val colsIdxedFields = schema
    .fieldNames
    .partition( x => rkFields.map(_.colName).contains(x))
    ._2.map(x => (schema.fieldIndex(x), catalog.getField(x)))
  val rdd = data.rdd //df.queryExecution.toRdd

  // 转换一行数据为Put，实现保存到hbase
  def convertToPut(row: Row) : (ImmutableBytesWritable, Put) = {
    val coder = catalog.shcTableCoder
    // construct bytes for row key
    val rBytes =
      // rowkey是组合的。Composite：组合的
      if (isComposite()) {
        // 把是rowkey的每一列转换成bate数组，只能最后一列的长度是可变的，这样应该是为了rowkey的过滤吧
        val rowBytes = coder.encodeCompositeRowKey(rkIdxedFields, row)

        val rLen = rowBytes.foldLeft(0) { case (x, y) =>
          x + y.length
        }
        // 所有的bate数组组成一个最终的bate数组
        val rBytes = new Array[Byte](rLen)
        var offset = 0
        rowBytes.foreach { x =>
          System.arraycopy(x, 0, rBytes, offset, x.length)
          offset += x.length
        }
        rBytes
      } else {
        // 单个列为rowkey
        val rBytes = rkIdxedFields.map { case (x, y) =>
          SHCDataTypeFactory.create(y).toBytes(row(x))
        }
        rBytes(0)
      }
    // Option的方法：def fold[B](ifEmpty: => B)(f: A => B): B
    // scala太灵活了
    val put = timestamp.fold(new Put(rBytes))(new Put(rBytes, _))
    // colsIdxedFields: Array[(Int, Field)]
    // 把正常的列设置到put，实现保存
    colsIdxedFields.foreach { case (x, y) =>
      // 修改源码， 跳过null值的列
      /*put.addColumn(
        coder.toBytes(y.cf),
        coder.toBytes(y.col),
        SHCDataTypeFactory.create(y).toBytes(row(x)))*/
      val value: Any = row(x)
      if(value != null ){
        put.addColumn(
          coder.toBytes(y.cf),
          coder.toBytes(y.col),
          SHCDataTypeFactory.create(y).toBytes(value))
      }
    }
    count += 1
    (new ImmutableBytesWritable, put)
  }

  // 最后还是调用的saveAsNewAPIHadoopDataset api，主要是实现了列的自动映射
  rdd.mapPartitions(iter => {
    SHCCredentialsManager.processShcToken(serializedToken)
    iter.map(convertToPut)
  }).saveAsNewAPIHadoopDataset(jobConfig)
}
```

### buildScan
返回DataFrame。
read比write复杂多了，还要自己实现返回RDD[Row].
```java
def buildScan(requiredColumns: Array[String], filters: Array[Filter]): RDD[Row] = {
  new HBaseTableScanRDD(this, requiredColumns, filters)
}
```



```java

```

```scala

```
