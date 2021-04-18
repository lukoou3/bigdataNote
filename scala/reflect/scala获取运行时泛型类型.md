

```scala
package scala.stream.join

import org.apache.flink.api.common.typeinfo.TypeInformation
import org.apache.flink.streaming.api.scala._

import scala.reflect.ClassTag

object TestGetClass {

  def getClass[T]()(implicit m: Manifest[T]):String={
    m.erasure.asInstanceOf[Class[T]].getName
  }

  def getClass2[T: ClassTag]():String={
    implicitly[ClassTag[T]].runtimeClass.asInstanceOf[Class[T]].getName
  }
  def getClass3[T: TypeInformation]()={
    val stateTypeInfo: TypeInformation[T] = implicitly[TypeInformation[T]]
    println(stateTypeInfo)
    stateTypeInfo.toString
  }


  def main(args: Array[String]): Unit = {
    println(getClass[Int]())
    println(getClass[DD]())

    println(getClass2[Int]())
    println(getClass2[DD]())
    println(getClass2[(Int,String)]())

    println(getClass3[Int]())
    println(getClass3[DD]())
    println(getClass3[(Int,String)]())
  }

  case class DD(id:Int, name:String)
}
```

输出
```
int
scala.stream.join.TestGetClass$DD
int
scala.stream.join.TestGetClass$DD
scala.Tuple2
Integer
Integer
scala.stream.join.TestGetClass$DD(id: Integer, name: String)
scala.stream.join.TestGetClass$DD(id: Integer, name: String)
scala.Tuple2(_1: Integer, _2: String)
scala.Tuple2(_1: Integer, _2: String)
```
