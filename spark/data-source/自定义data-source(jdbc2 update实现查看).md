# 自定义data-source(jdbc2 update实现查看)

## DefaultSource

实现DataSourceRegister接口，实现shortName方法可以实现别名format，不过必须通过加载jar的形式，在idea中测试不行。
实现RelationProvider接口，实现createRelation方法返回BaseRelation对象用于load DataFrame。
实现CreatableRelationProvider接口，实现createRelation方法返回BaseRelation对象，在createRelation方法中save参数传入的DataFrame。

```scala
package org.apache.spark.sql.execution.datasources.jdbc2

class DefaultSource extends CreatableRelationProvider with RelationProvider with DataSourceRegister {

  override def shortName(): String = "jdbc2"

  override def createRelation(
                               sqlContext: SQLContext,
                               parameters: Map[String, String]): BaseRelation = {

    ...
    JDBCRelation(parts, jdbcOptions)(sqlContext.sparkSession)
  }

  override def createRelation(
                               sqlContext: SQLContext,
                               mode: SaveMode,
                               parameters: Map[String, String],
                               df: DataFrame): BaseRelation = {
    ...
    createRelation(sqlContext, parameters)
  }
}
```

## save实现

### createRelation

```scala
override def createRelation(
                             sqlContext: SQLContext,
                             mode: SaveMode,
                             parameters: Map[String, String],
                             df: DataFrame): BaseRelation = {
  // 解析jdbc参数
  val options = new JDBCOptions(parameters)
  // 是否大小写敏感，这个判断df column table column为一个column会用到
  val isCaseSensitive = sqlContext.conf.caseSensitiveAnalysis

  // 把spark的SaveMode转行成了自己的，下面可以通过参数修改，所以参数配置了SaveMode，mode方法就会被覆盖。
  var saveMode: JDBCSaveMode.Value = mode match {
    case SaveMode.Overwrite => JDBCSaveMode.Overwrite
    case SaveMode.Append => JDBCSaveMode.Append
    case SaveMode.ErrorIfExists => JDBCSaveMode.ErrorIfExists
    case SaveMode.Ignore => JDBCSaveMode.Ignore
  }
  // 参数key都转小写
  val parameterLower: Map[String, String] = parameters.map(kv => (kv._1.toLowerCase, kv._2))
  // savemode 参数可以覆盖 saveMode
  saveMode = if (parameterLower.keySet.contains("savemode")) {
    if (parameterLower("savemode").toLowerCase == JDBCSaveMode.Update.toString.toLowerCase) JDBCSaveMode.Update else saveMode
  } else {
    saveMode
  }

  val conn: Connection = JdbcUtils.createConnectionFactory(options)()
  try {
    val tableExists: Boolean = JdbcUtils.tableExists(conn, options)
    if (tableExists) {
      saveMode match {
        case JDBCSaveMode.Overwrite =>
          if (options.isTruncate && isCascadingTruncateTable(options.url).contains(false)) {
            // In this case, we should truncate table and then load.
            truncateTable(conn, options)
            val tableSchema = JdbcUtils.getSchemaOption(conn, options)
            saveTable(df, tableSchema, isCaseSensitive, options, saveMode)
          } else {
            // Otherwise, do not truncate the table, instead drop and recreate it
            dropTable(conn, options.table)
            createTable(conn, df, options)
            saveTable(df, Some(df.schema), isCaseSensitive, options, saveMode)
          }

        case JDBCSaveMode.Update =>
          // 获取table的schema，写入df到table
          val tableSchema = JdbcUtils.getSchemaOption(conn, options)
          saveTable(df, tableSchema, isCaseSensitive, options, saveMode)

        case JDBCSaveMode.Append =>
          val tableSchema = JdbcUtils.getSchemaOption(conn, options)
          saveTable(df, tableSchema, isCaseSensitive, options, saveMode)

        case JDBCSaveMode.ErrorIfExists =>
          throw new AnalysisException(
            s"Table or view '${options.table}' already exists. SaveMode: ErrorIfExists.")

        case JDBCSaveMode.Ignore =>
        // With `SaveMode.Ignore` mode, if table already exists, the save operation is expected
        // to not save the contents of the DataFrame and to not change the existing data.
        // Therefore, it is okay to do nothing here and then just return the relation below.
      }
    } else {
      createTable(conn, df, options)
      saveTable(df, Some(df.schema), isCaseSensitive, options, saveMode)
    }
  } finally {
    conn.close()
  }

  createRelation(sqlContext, parameters)
}
```

### saveTable
org.apache.spark.sql.execution.datasources.jdbc2.JdbcUtils的方法。
```scala
/**
  * Saves the RDD to the database in a single transaction.
  */
def saveTable(
               df: DataFrame,
               tableSchema: Option[StructType],
               isCaseSensitive: Boolean,
               options: JDBCOptions,
               mode: JDBCSaveMode): Unit = {
  val url = options.url
  val table = options.table
  val dialect = JdbcDialects.get(url)
  val rddSchema = df.schema
  val getConnection: () => Connection = createConnectionFactory(options)
  val batchSize = options.batchSize
  val isolationLevel = options.isolationLevel

  // 生成insert sql
  val insertStmt = getInsertStatement(table, rddSchema, tableSchema, isCaseSensitive, dialect, mode, options)
  val repartitionedDF = options.numPartitions match {
    case Some(n) if n <= 0 => throw new IllegalArgumentException(
      s"Invalid value `$n` for parameter `${JDBCOptions.JDBC_NUM_PARTITIONS}` in table writing " +
        "via JDBC. The minimum value is 1.")
    case Some(n) if n < df.rdd.getNumPartitions => df.coalesce(n)
    case _ => df
  }
  repartitionedDF.rdd.foreachPartition(iterator => savePartition(
    getConnection, table, iterator, rddSchema, insertStmt, batchSize, dialect, isolationLevel, mode)
  )
}

```

### getInsertStatement
```scala
/**
  * Returns an Insert SQL statement for inserting a row into the target table via JDBC conn.
  */
def getInsertStatement(
                        table: String,
                        rddSchema: StructType,
                        tableSchema: Option[StructType],
                        isCaseSensitive: Boolean,
                        dialect: JdbcDialect,
                        mode: JDBCSaveMode,
                        options: JDBCOptions
                      ): String = {
  // 生成sql table 的columns
  val columns = if (tableSchema.isEmpty) {
    // 如果每天sql table 的scheme，用dataframe的columns
    rddSchema.fields.map(x => dialect.quoteIdentifier(x.name)).mkString(",")
  } else {
    val columnNameEquality = if (isCaseSensitive) {
      org.apache.spark.sql.catalyst.analysis.caseSensitiveResolution
    } else {
      org.apache.spark.sql.catalyst.analysis.caseInsensitiveResolution
    }
    // The generated insert statement needs to follow rddSchema's column sequence and
    // tableSchema's column names. When appending data into some case-sensitive DBMSs like
    // PostgreSQL/Oracle, we need to respect the existing case-sensitive column names instead of
    // RDD column names for user convenience.
    val tableColumnNames = tableSchema.get.fieldNames
    // 转dataframe的columns为sql table 的columns，不区分大小写查找
    rddSchema.fields.map { col =>
      val normalizedName = tableColumnNames.find(f => columnNameEquality(f, col.name)).getOrElse {
        throw new AnalysisException(s"""Column "${col.name}" not found in schema $tableSchema""")
      }
      dialect.quoteIdentifier(normalizedName)
    }.mkString(",")
  }
  // 生成替换参数，_ => "?"这个函数定义方法可以学习一下
  val placeholders = rddSchema.fields.map(_ => "?").mkString(",")

  // 根据mode是否是update生成insert sql
  mode match {
    case JDBCSaveMode.Update =>
      val props = options.asProperties
      val duplicateIncs = props
        .getProperty(JDBCOptions.JDBC_DUPLICATE_INCS, "")
        .split(",")
        .filter { x => StringUtils.isNotBlank(x) }
        .map { x => s"`$x`" }
      val duplicateSetting = rddSchema
        .fields
        .map { x => dialect.quoteIdentifier(x.name) }
        .map { name => if (duplicateIncs.contains(name)) s"$name=$name+?" else s"$name=?" }
        .mkString(",")
      // INSERT UPDATE sql
      val sql = s"INSERT INTO $table ($columns) VALUES ($placeholders) ON DUPLICATE KEY UPDATE $duplicateSetting"
      if (props.getProperty("showSql", "false").equals("true")) {
        println(s"${JDBCSaveMode.Update} => sql => $sql")
      }
      sql
    case _ => s"INSERT INTO $table ($columns) VALUES ($placeholders)"
  }
  //    s"INSERT INTO $table ($columns) VALUES ($placeholders)"
}
```


### savePartition
```scala
/**
  * Saves a partition of a DataFrame to the JDBC database.  This is done in
  * a single database transaction (unless isolation level is "NONE")
  * in order to avoid repeatedly inserting data as much as possible.
  *
  * It is still theoretically possible for rows in a DataFrame to be
  * inserted into the database more than once if a stage somehow fails after
  * the commit occurs but before the stage can return successfully.
  *
  * This is not a closure inside saveTable() because apparently cosmetic
  * implementation changes elsewhere might easily render such a closure
  * non-Serializable.  Instead, we explicitly close over all variables that
  * are used.
  */
def savePartition(
                   getConnection: () => Connection,
                   table: String,
                   iterator: Iterator[Row],
                   rddSchema: StructType,
                   insertStmt: String,
                   batchSize: Int,
                   dialect: JdbcDialect,
                   isolationLevel: Int,
                   mode: JDBCSaveMode): Iterator[Byte] = {
  val conn = getConnection()
  var committed = false

  var finalIsolationLevel = Connection.TRANSACTION_NONE
  if (isolationLevel != Connection.TRANSACTION_NONE) {
    try {
      val metadata = conn.getMetaData
      if (metadata.supportsTransactions()) {
        // Update to at least use the default isolation, if any transaction level
        // has been chosen and transactions are supported
        val defaultIsolation = metadata.getDefaultTransactionIsolation
        finalIsolationLevel = defaultIsolation
        if (metadata.supportsTransactionIsolationLevel(isolationLevel)) {
          // Finally update to actually requested level if possible
          finalIsolationLevel = isolationLevel
        } else {
          logWarning(s"Requested isolation level $isolationLevel is not supported; " +
            s"falling back to default isolation level $defaultIsolation")
        }
      } else {
        logWarning(s"Requested isolation level $isolationLevel, but transactions are unsupported")
      }
    } catch {
      case NonFatal(e) => logWarning("Exception while detecting transaction support", e)
    }
  }
  val supportsTransactions = finalIsolationLevel != Connection.TRANSACTION_NONE

  try {
    if (supportsTransactions) {
      conn.setAutoCommit(false) // Everything in the same db transaction.
      conn.setTransactionIsolation(finalIsolationLevel)
    }
    val isUpdateMode = mode == JDBCSaveMode.Update
    val stmt = conn.prepareStatement(insertStmt)
    // private type JDBCValueSetter = (PreparedStatement, Row, Int, Int) ⇒ Unit
    // 设置函数数组，这个可以借鉴
    // case IntegerType ⇒ (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒ stmt.setInt(pos + 1, row.getInt(pos - offset))
    val setters: Array[JDBCValueSetter] = getSetter(rddSchema.fields, conn, dialect, isUpdateMode)
    val nullTypes = rddSchema.fields.map(f => getJdbcType(f.dataType, dialect).jdbcNullType)
    // dataframe的columns len
    val length = rddSchema.fields.length
    // ? 的个数
    val numFields = if (isUpdateMode) length * 2 else length
    // ? 的个数除以2
    val midField = numFields / 2
    try {
      var rowCount = 0
      while (iterator.hasNext) {
        val row = iterator.next()
        var i = 0
        while (i < numFields) {
          if (isUpdateMode) {
            i < midField match {
              case true ⇒
                if (row.isNullAt(i)) {
                  stmt.setNull(i + 1, nullTypes(i))
                } else {
                  // 这样调用函数
                  setters(i).apply(stmt, row, i, 0)
                }
              case false ⇒
                if (row.isNullAt(i - midField)) {
                  stmt.setNull(i + 1, nullTypes(i - midField))
                } else {
                  setters(i).apply(stmt, row, i, midField)
                }
            }
          } else {
            if (row.isNullAt(i)) {
              stmt.setNull(i + 1, nullTypes(i))
            } else {
              setters(i).apply(stmt, row, i, 0)
            }
          }
          i = i + 1
        }
        stmt.addBatch()
        rowCount += 1
        // 批量提交
        if (rowCount % batchSize == 0) {
          stmt.executeBatch()
          rowCount = 0
        }
      }
      if (rowCount > 0) {
        stmt.executeBatch()
      }
    } finally {
      stmt.close()
    }
    if (supportsTransactions) {
      conn.commit()
    }
    committed = true
    Iterator.empty
  } catch {
    case e: SQLException =>
      val cause = e.getNextException
      if (cause != null && e.getCause != cause) {
        // If there is no cause already, set 'next exception' as cause. If cause is null,
        // it *may* be because no cause was set yet
        if (e.getCause == null) {
          try {
            e.initCause(cause)
          } catch {
            // Or it may be null because the cause *was* explicitly initialized, to *null*,
            // in which case this fails. There is no other way to detect it.
            // addSuppressed in this case as well.
            case _: IllegalStateException => e.addSuppressed(cause)
          }
        } else {
          e.addSuppressed(cause)
        }
      }
      throw e
  } finally {
    if (!committed) {
      // The stage must fail.  We got here through an exception path, so
      // let the exception through unless rollback() or close() want to
      // tell the user about another problem.
      if (supportsTransactions) {
        conn.rollback()
      }
      conn.close()
    } else {
      // The stage must succeed.  We cannot propagate any exception close() might throw.
      try {
        conn.close()
      } catch {
        case e: Exception => logWarning("Transaction succeeded, but closing failed", e)
      }
    }
  }
}
```

### getSetter
```scala
// 定义函数类型，这个可以借鉴
private type JDBCValueSetter = (PreparedStatement, Row, Int, Int) ⇒ Unit

// 生成set函数
private def makeSetter(
                        conn: Connection,
                        dialect: JdbcDialect,
                        dataType: DataType): JDBCValueSetter = dataType match {

  case IntegerType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setInt(pos + 1, row.getInt(pos - offset))

  case LongType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setLong(pos + 1, row.getLong(pos - offset))

  case DoubleType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setDouble(pos + 1, row.getDouble(pos - offset))

  case FloatType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setFloat(pos + 1, row.getFloat(pos - offset))

  case ShortType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setInt(pos + 1, row.getShort(pos - offset))

  case ByteType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setInt(pos + 1, row.getByte(pos - offset))

  case BooleanType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setBoolean(pos + 1, row.getBoolean(pos - offset))

  case StringType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setString(pos + 1, row.getString(pos - offset))

  case BinaryType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setBytes(pos + 1, row.getAs[Array[Byte]](pos - offset))

  case TimestampType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setTimestamp(pos + 1, row.getAs[java.sql.Timestamp](pos - offset))

  case DateType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setDate(pos + 1, row.getAs[java.sql.Date](pos - offset))

  case t: DecimalType ⇒
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      stmt.setBigDecimal(pos + 1, row.getDecimal(pos - offset))

  case ArrayType(et, _) ⇒
    // remove type length parameters from end of type name
    val typeName = getJdbcType(et, dialect).databaseTypeDefinition
      .toLowerCase.split("\\(")(0)
    (stmt: PreparedStatement, row: Row, pos: Int, offset: Int) ⇒
      val array = conn.createArrayOf(
        typeName,
        row.getSeq[AnyRef](pos - offset).toArray)
      stmt.setArray(pos + 1, array)

  case _ ⇒
    (_: PreparedStatement, _: Row, pos: Int, offset: Int) ⇒
      throw new IllegalArgumentException(
        s"Can't translate non-null value for field $pos")
}

// 生成set函数数组，Array.fill(2)(setter).flatten用法可以借鉴。
private def getSetter(fields: Array[StructField], connection: Connection, dialect: JdbcDialect, isUpdateMode: Boolean): Array[JDBCValueSetter] = {
  val setter = fields.map(_.dataType).map(makeSetter(connection, dialect, _))
  if (isUpdateMode) {
    Array.fill(2)(setter).flatten
  } else {
    setter
  }
}
```

## load实现
```scala
override def createRelation(
                             sqlContext: SQLContext,
                             parameters: Map[String, String]): BaseRelation = {

  val jdbcOptions = new JDBCOptions(parameters)
  // 下面四个参数用户分区，定义了partitionColumn就必须定义其他3个字段
  val partitionColumn = jdbcOptions.partitionColumn
  val lowerBound = jdbcOptions.lowerBound
  val upperBound = jdbcOptions.upperBound
  val numPartitions = jdbcOptions.numPartitions

  val partitionInfo = if (partitionColumn.isEmpty) {
    assert(lowerBound.isEmpty && upperBound.isEmpty, "When 'partitionColumn' is not specified, " +
      s"'$JDBC_LOWER_BOUND' and '$JDBC_UPPER_BOUND' are expected to be empty")
    null
  } else {
    assert(lowerBound.nonEmpty && upperBound.nonEmpty && numPartitions.nonEmpty,
      s"When 'partitionColumn' is specified, '$JDBC_LOWER_BOUND', '$JDBC_UPPER_BOUND', and " +
        s"'$JDBC_NUM_PARTITIONS' are also required")
    JDBCPartitioningInfo(
      partitionColumn.get, lowerBound.get, upperBound.get, numPartitions.get)
  }
  // 生成Array[Partition]
  val parts = JDBCRelation.columnPartition(partitionInfo)
  JDBCRelation(parts, jdbcOptions)(sqlContext.sparkSession)
}

/**
  * Instructions on how to partition the table among workers.
  */
private[sql] case class JDBCPartitioningInfo(
                                              column: String,
                                              lowerBound: Long,
                                              upperBound: Long,
                                              numPartitions: Int)
```

### 生成Array[Partition]

#### JDBCPartition
```scala
/**
  * Data corresponding to one partition of a JDBCRDD.
  */
case class JDBCPartition(whereClause: String, idx: Int) extends Partition {
  override def index: Int = idx
}

/**
 * An identifier for a partition in an RDD.
 */
trait Partition extends Serializable {
  /**
   * Get the partition's index within its parent RDD
   */
  def index: Int

  // A better default implementation of HashCode
  override def hashCode(): Int = index

  override def equals(other: Any): Boolean = super.equals(other)
}
```

#### columnPartition
```scala
// 给定一个分区示意图（整型列、若干分区以及列值的上下界），为每个分区生成WHERE子句，以便表中的每一行恰好出现一次。
// 参数minValue和maxValue是建议性的，因为不正确的值可能会导致分区不好，但不会有数据无法表示。
// 空值谓词被添加到第一个partitionwhere子句中，以包含partitions列中具有空值的行。
/**
  * Given a partitioning schematic (a column of integral type, a number of
  * partitions, and upper and lower bounds on the column's value), generate
  * WHERE clauses for each partition so that each row in the table appears
  * exactly once.  The parameters minValue and maxValue are advisory in that
  * incorrect values may cause the partitioning to be poor, but no data
  * will fail to be represented.
  *
  * Null value predicate is added to the first partition where clause to include
  * the rows with null value for the partitions column.
  *
  * @param partitioning partition information to generate the where clause for each partition
  * @return an array of partitions with where clause for each partition
  */
def columnPartition(partitioning: JDBCPartitioningInfo): Array[Partition] = {
  if (partitioning == null || partitioning.numPartitions <= 1 ||
    partitioning.lowerBound == partitioning.upperBound) {
    // 整个sql table为一个分区
    return Array[Partition](JDBCPartition(null, 0))
  }

  val lowerBound = partitioning.lowerBound
  val upperBound = partitioning.upperBound
  require (lowerBound <= upperBound,
    "Operation not allowed: the lower bound of partitioning column is larger than the upper " +
      s"bound. Lower bound: $lowerBound; Upper bound: $upperBound")

  val numPartitions =
    if ((upperBound - lowerBound) >= partitioning.numPartitions || /* check for overflow */
      (upperBound - lowerBound) < 0) {
      partitioning.numPartitions
    } else {
      logWarning("The number of partitions is reduced because the specified number of " +
        "partitions is less than the difference between upper bound and lower bound. " +
        s"Updated number of partitions: ${upperBound - lowerBound}; Input number of " +
        s"partitions: ${partitioning.numPartitions}; Lower bound: $lowerBound; " +
        s"Upper bound: $upperBound.")
      upperBound - lowerBound
    }
  // Overflow and silliness can happen if you subtract then divide.
  // Here we get a little roundoff, but that's (hopefully) OK.
  val stride: Long = upperBound / numPartitions - lowerBound / numPartitions
  val column = partitioning.column
  var i: Int = 0
  var currentValue: Long = lowerBound
  val ans = new ArrayBuffer[Partition]()
  while (i < numPartitions) {
    val lBound = if (i != 0) s"$column >= $currentValue" else null
    currentValue += stride
    val uBound = if (i != numPartitions - 1) s"$column < $currentValue" else null
    val whereClause =
      if (uBound == null) {
        lBound
      } else if (lBound == null) {
        s"$uBound or $column is null"
      } else {
        s"$lBound AND $uBound"
      }
    ans += JDBCPartition(whereClause, i)
    i = i + 1
  }
  ans.toArray
}
```

#### JDBCRelation
生成rdd比save复杂，先不看了，自定义读的情况少，自定义保存用的多一点。
```scala
private[sql] case class JDBCRelation(
                                      parts: Array[Partition], jdbcOptions: JDBCOptions)(@transient val sparkSession: SparkSession)
  extends BaseRelation
    with PrunedFilteredScan
    with InsertableRelation {

  override def sqlContext: SQLContext = sparkSession.sqlContext

  override val needConversion: Boolean = false

  override val schema: StructType = {
    val tableSchema = JDBCRDD.resolveTable(jdbcOptions)
    jdbcOptions.customSchema match {
      case Some(customSchema) => JdbcUtils.getCustomSchema(
        tableSchema, customSchema, sparkSession.sessionState.conf.resolver)
      case None => tableSchema
    }
  }

  // Check if JDBCRDD.compileFilter can accept input filters
  override def unhandledFilters(filters: Array[Filter]): Array[Filter] = {
    filters.filter(JDBCRDD.compileFilter(_, JdbcDialects.get(jdbcOptions.url)).isEmpty)
  }

  override def buildScan(requiredColumns: Array[String], filters: Array[Filter]): RDD[Row] = {
    // Rely on a type erasure hack to pass RDD[InternalRow] back as RDD[Row]
    JDBCRDD.scanTable(
      sparkSession.sparkContext,
      schema,
      requiredColumns,
      filters,
      parts,
      jdbcOptions).asInstanceOf[RDD[Row]]
  }

  override def insert(data: DataFrame, overwrite: Boolean): Unit = {
    data
      .write
      .mode(if (overwrite) SaveMode.Overwrite else SaveMode.Append)
      .jdbc(jdbcOptions.url, jdbcOptions.table, jdbcOptions.asProperties)
  }

  override def toString: String = {
    val partitioningInfo = if (parts.nonEmpty) s" [numPartitions=${parts.length}]" else ""
    // credentials should not be included in the plan output, table information is sufficient.
    s"JDBCRelation(${jdbcOptions.table})" + partitioningInfo
  }
}
```

## JDBCOptions
文件定义了伴生类和伴生对象。

### object
```scala
object JDBCOptions {
  private val jdbcOptionNames = collection.mutable.Set[String]()

  private def newOption(name: String): String = {
    // 不区分大小写
    jdbcOptionNames += name.toLowerCase(Locale.ROOT)
    name
  }

  // 下面这个实现很奇妙，同时初始化了枚举和枚举的集合，可以学学。
  val JDBC_URL = newOption("url")
  val JDBC_TABLE_NAME = newOption("dbtable")
  val JDBC_DRIVER_CLASS = newOption("driver")
  val JDBC_PARTITION_COLUMN = newOption("partitionColumn")
  val JDBC_LOWER_BOUND = newOption("lowerBound")
  val JDBC_UPPER_BOUND = newOption("upperBound")
  val JDBC_NUM_PARTITIONS = newOption("numPartitions")
  val JDBC_BATCH_FETCH_SIZE = newOption("fetchsize")
  val JDBC_TRUNCATE = newOption("truncate")
  val JDBC_CREATE_TABLE_OPTIONS = newOption("createTableOptions")
  val JDBC_CREATE_TABLE_COLUMN_TYPES = newOption("createTableColumnTypes")
  val JDBC_CUSTOM_DATAFRAME_COLUMN_TYPES = newOption("customSchema")
  val JDBC_BATCH_INSERT_SIZE = newOption("batchsize")
  val JDBC_TXN_ISOLATION_LEVEL = newOption("isolationLevel")
  val JDBC_SESSION_INIT_STATEMENT = newOption("sessionInitStatement")
  val JDBC_DUPLICATE_INCS = newOption("duplicateIncs")
}
```

### class
这里面这要解析和存了一些参数(直接解析成字段，class中的代码就相当于java中的构造函数中的代码)，一些不是必须定义参数的类型为Option， 其他的直接存的值。
```scala
package org.apache.spark.sql.execution.datasources.jdbc2

import java.sql.{Connection, DriverManager}
import java.util.{Locale, Properties}

import org.apache.spark.sql.catalyst.util.CaseInsensitiveMap

// 这里都实现Serializable是因为saprk集群运行要序列化吧
class JDBCOptions(
                   @transient private val parameters: CaseInsensitiveMap[String])
  extends Serializable {

  // 可以直接引用object JDBCOptions中的变量，不用JDBCOptions.field访问。
  import JDBCOptions._

  // scala中非主构造函数的定义：必须最终调动主构造器
  def this(parameters: Map[String, String]) = this(CaseInsensitiveMap(parameters))

  def this(url: String, table: String, parameters: Map[String, String]) = {
    this(CaseInsensitiveMap(parameters ++ Map(
      JDBCOptions.JDBC_URL -> url,
      JDBCOptions.JDBC_TABLE_NAME -> table)))
  }

  /**
    * Returns a property with all options.
    */
  val asProperties: Properties = {
    val properties = new Properties()
    // 函数式编程：突然注意到scala的foreach，java8的是forEach(scala12之前不能使用原生的scala函数)。
    parameters.originalMap.foreach { case (k, v) => properties.setProperty(k, v) }
    properties
  }

  /**
    * Returns a property with all options except Spark internal data source options like `url`,
    * `dbtable`, and `numPartition`. This should be used when invoking JDBC API like `Driver.connect`
    * because each DBMS vendor has its own property list for JDBC driver. See SPARK-17776.
    */
  // 去除spark中定义的key
  val asConnectionProperties: Properties = {
    val properties = new Properties()
    // jdbcOptionNames是set类型，set(e)返回Boolean，调用的是class的apply方法。
    parameters.originalMap.filterKeys(key => !jdbcOptionNames(key.toLowerCase(Locale.ROOT)))
      .foreach { case (k, v) => properties.setProperty(k, v) }
    properties
  }

  // ------------------------------------------------------------
  // Required parameters
  // ------------------------------------------------------------
  require(parameters.isDefinedAt(JDBC_URL), s"Option '$JDBC_URL' is required.")
  require(parameters.isDefinedAt(JDBC_TABLE_NAME), s"Option '$JDBC_TABLE_NAME' is required.")
  // a JDBC URL
  val url = parameters(JDBC_URL)
  // name of table
  val table = parameters(JDBC_TABLE_NAME)

  // ------------------------------------------------------------
  // Optional parameters
  // ------------------------------------------------------------
  val driverClass = {
    val userSpecifiedDriverClass = parameters.get(JDBC_DRIVER_CLASS)
    userSpecifiedDriverClass.foreach(DriverRegistry.register)

    // Performing this part of the logic on the driver guards against the corner-case where the
    // driver returned for a URL is different on the driver and executors due to classpath
    // differences.
    userSpecifiedDriverClass.getOrElse {
      DriverManager.getDriver(url).getClass.getCanonicalName
    }
  }

  // the number of partitions
  val numPartitions = parameters.get(JDBC_NUM_PARTITIONS).map(_.toInt)

  // ------------------------------------------------------------
  // Optional parameters only for reading
  // ------------------------------------------------------------
  // the column used to partition
  val partitionColumn = parameters.get(JDBC_PARTITION_COLUMN)
  // the lower bound of partition column
  val lowerBound = parameters.get(JDBC_LOWER_BOUND).map(_.toLong)
  // the upper bound of the partition column
  val upperBound = parameters.get(JDBC_UPPER_BOUND).map(_.toLong)
  // numPartitions is also used for data source writing
  require((partitionColumn.isEmpty && lowerBound.isEmpty && upperBound.isEmpty) ||
    (partitionColumn.isDefined && lowerBound.isDefined && upperBound.isDefined &&
      numPartitions.isDefined),
    s"When reading JDBC data sources, users need to specify all or none for the following " +
      s"options: '$JDBC_PARTITION_COLUMN', '$JDBC_LOWER_BOUND', '$JDBC_UPPER_BOUND', " +
      s"and '$JDBC_NUM_PARTITIONS'")
  val fetchSize = {
    val size = parameters.getOrElse(JDBC_BATCH_FETCH_SIZE, "0").toInt
    require(size >= 0,
      s"Invalid value `${size.toString}` for parameter " +
        s"`$JDBC_BATCH_FETCH_SIZE`. The minimum value is 0. When the value is 0, " +
        "the JDBC driver ignores the value and does the estimates.")
    size
  }

  // ------------------------------------------------------------
  // Optional parameters only for writing
  // ------------------------------------------------------------
  // if to truncate the table from the JDBC database
  val isTruncate = parameters.getOrElse(JDBC_TRUNCATE, "false").toBoolean
  // the create table option , which can be table_options or partition_options.
  // E.g., "CREATE TABLE t (name string) ENGINE=InnoDB DEFAULT CHARSET=utf8"
  // TODO: to reuse the existing partition parameters for those partition specific options
  val createTableOptions = parameters.getOrElse(JDBC_CREATE_TABLE_OPTIONS, "")
  val createTableColumnTypes = parameters.get(JDBC_CREATE_TABLE_COLUMN_TYPES)
  val customSchema = parameters.get(JDBC_CUSTOM_DATAFRAME_COLUMN_TYPES)

  val batchSize = {
    val size = parameters.getOrElse(JDBC_BATCH_INSERT_SIZE, "1000").toInt
    require(size >= 1,
      s"Invalid value `${size.toString}` for parameter " +
        s"`$JDBC_BATCH_INSERT_SIZE`. The minimum value is 1.")
    size
  }
  val isolationLevel =
    parameters.getOrElse(JDBC_TXN_ISOLATION_LEVEL, "READ_UNCOMMITTED") match {
      case "NONE" => Connection.TRANSACTION_NONE
      case "READ_UNCOMMITTED" => Connection.TRANSACTION_READ_UNCOMMITTED
      case "READ_COMMITTED" => Connection.TRANSACTION_READ_COMMITTED
      case "REPEATABLE_READ" => Connection.TRANSACTION_REPEATABLE_READ
      case "SERIALIZABLE" => Connection.TRANSACTION_SERIALIZABLE
    }
  // An option to execute custom SQL before fetching data from the remote DB
  val sessionInitStatement = parameters.get(JDBC_SESSION_INIT_STATEMENT)
}
```


## CaseInsensitiveMap
这个是spark中的类。

CaseInsensitiveMap类代码阅读。Insensitive:不敏感的。类的字面意思的就是大小写不敏感的map。这个实际现实的是key大部分大小写的map。

文件定义了伴生类和伴生对象。


```scala
package org.apache.spark.sql.catalyst.util

import java.util.Locale

// 构建键不区分大小写的映射。对于需要区分大小写的信息的情况，可以访问输入映射。主构造函数被标记为private以避免创建嵌套的不区分大小写的映射，否则在这种情况下，原始映射中的键将变得不区分大小写。
/**
 * Builds a map in which keys are case insensitive. Input map can be accessed for cases where
 * case-sensitive information is required. The primary constructor is marked private to avoid
 * nested case-insensitive map creation, otherwise the keys in the original map will become
 * case-insensitive in this scenario.
 */
// 这个类继承Map[String, T]，参数也是Map[String, T]为了防止嵌套创建，把构造函数定义成了private。
// 同时实现Serializable接口
class CaseInsensitiveMap[T] private (val originalMap: Map[String, T]) extends Map[String, T]
  with Serializable {

  // scala类中的代码创建对象时会从上往下执行(scala常识)
  // 从原始的map生成key都是小写的map，kv.copy应该是元组(Product2)的内建方法而且还支持关键字参数。
  val keyLowerCasedMap = originalMap.map(kv => kv.copy(_1 = kv._1.toLowerCase(Locale.ROOT)))

  // 重写map的get方法：key不区分大小写。同时也相当于重写的apply方法，MapLike的apply也是依赖get。
  override def get(k: String): Option[T] = keyLowerCasedMap.get(k.toLowerCase(Locale.ROOT))

  // 重写map的contains方法：key不区分大小写
  override def contains(k: String): Boolean =
    keyLowerCasedMap.contains(k.toLowerCase(Locale.ROOT))

  // 重写+：添加元素
  override def +[B1 >: T](kv: (String, B1)): CaseInsensitiveMap[B1] = {
    new CaseInsensitiveMap(originalMap.filter(!_._1.equalsIgnoreCase(kv._1)) + kv)
  }

  // 重写+：添加集合
  def ++(xs: TraversableOnce[(String, T)]): CaseInsensitiveMap[T] = {
    // 这个实现很奇妙，scala真灵活
    xs.foldLeft(this)(_ + _)
  }

  override def iterator: Iterator[(String, T)] = keyLowerCasedMap.iterator

  // 重写-：减去元素
  override def -(key: String): Map[String, T] = {
    new CaseInsensitiveMap(originalMap.filterKeys(!_.equalsIgnoreCase(key)))
  }

  // 返回原始map
  def toMap: Map[String, T] = originalMap
}

// 伴生对象
object CaseInsensitiveMap {
  // 这样其他地方就可以创建CaseInsensitiveMap类了，同样防止了嵌套创建。
  def apply[T](params: Map[String, T]): CaseInsensitiveMap[T] = params match {
    // 如果传入CaseInsensitiveMap返回本身
    case caseSensitiveMap: CaseInsensitiveMap[T] => caseSensitiveMap
    // 如果传入map就创建CaseInsensitiveMap
    case _ => new CaseInsensitiveMap(params)
  }
}
```























