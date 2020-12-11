# spark-sql处理复杂的类型
array对应scala的Seq，struct对应scala的Row。

官网有对应关系的说明：http://spark.apache.org/docs/2.4.7/sql-reference.html


测试：
```sql
package com.test.spark04

import org.apache.spark.sql.{DataFrame, Dataset, Row, SparkSession}

import scala.collection.mutable

/**
  * http://spark.apache.org/docs/2.4.7/sql-reference.html
  */
object ArrayStructUDFTest {

  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Spark SQL basic example").master("local[4]")
      .config("spark.some.config.option", "some-value")
      .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    import spark.implicits._

    val json ="""
    {
        "name": "Geoff Lui",
        "age": 26,
        "isChinese": 1,
        "friends":[{"name":"Lucy","age": 26}, {"name":"Lily","age": 24}, {"name":"Gwen","age": 29}],
        "Mother": {
            "name": "Mary Lui",
            "age": 54
        }
    }
    """

    val jsonDataset: Dataset[String] = spark.createDataset(List(json))

    val jsonDf: DataFrame = spark.read.json(jsonDataset)

    jsonDf.printSchema()

    jsonDf.show()


    val row = jsonDf.select("friends").first()
    /*val friends: mutable.WrappedArray[Row] = row.getAs[mutable.WrappedArray[Row]]("friends")
    for (Row(age: Long, name: String) <- friends) {
      println(age, name)
    }

    spark.udf.register("test_friends", ( friends: mutable.WrappedArray[Row] )=> {
      friends.map(x => x.getAs[String]("name") + ":" + x.getAs[Long]("age")).mkString(", ")
    })*/

    val friends: Seq[Row] = row.getAs[Seq[Row]]("friends")
    for (Row(age: Long, name: String) <- friends) {
      println(age, name)
    }

    spark.udf.register("test_friends", ( friends: Seq[Row] )=> {
      friends.map(x => x.getAs[String]("name") + ":" + x.getAs[Long]("age")).mkString(", ")
    })

    jsonDf.selectExpr("test_friends(friends) rst").show(false)


    spark.stop()
  }

}

```
