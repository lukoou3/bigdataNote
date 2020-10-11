
## scala类和json互转

### 依赖
```xml
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.10.0</version>
</dependency>

<dependency>
    <groupId>com.fasterxml.jackson.module</groupId>
    <artifactId>jackson-module-scala_2.11</artifactId>
    <version>2.10.0</version>
</dependency>
```

### 一般的case类和类与json互转
加上一句话就行：
```scala
val mapper = new ObjectMapper // create once, reuse
mapper.registerModule(DefaultScalaModule)
```


```scala
package data

import java.{util => ju}

import com.fasterxml.jackson.core.`type`.TypeReference
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule

import scala.collection.mutable

object ScalaTest {

  def test(): Unit ={
    /**
     * DefaultScalaModule照样可以转换java类
     */
    val mapper = new ObjectMapper // create once, reuse
    mapper.registerModule(DefaultScalaModule)

    val stuJavaClass = new StuJavaClass
    stuJavaClass.setName("小明")
    stuJavaClass.setAge(20)
    stuJavaClass.setScore(80D)

    val json = mapper.writeValueAsString(stuJavaClass)
    println(json)
    val stuJavaClass1 = mapper.readValue(json, classOf[StuJavaClass])
    println(stuJavaClass1)
  }

  def main(args: Array[String]): Unit = {
    test()

    val stuCaseClass: StuCaseClass = StuCaseClass("小明", 20, 90D)
    // 默认的tostring：StuCaseClass(小明,20,90.0)
    // case 类的方法可以重写
    println(stuCaseClass)
    println(stuCaseClass == StuCaseClass("小明", 20, 90D))

    println("----------------------------")

    val stuScalaClass = new StuScalaClass
    stuScalaClass.name = "小花"
    stuScalaClass.age = 20
    stuScalaClass.score = 92D
    println(stuScalaClass)

    println("----------------------------")

    val mapper = new ObjectMapper // create once, reuse
    mapper.registerModule(DefaultScalaModule)
    val json = mapper.writeValueAsString(stuCaseClass)
    println(json)
    println(mapper.writeValueAsString(stuScalaClass))

    val stuCaseClass1 = mapper.readValue(json, classOf[StuCaseClass])
    val stuScalaClass1 = mapper.readValue(json, classOf[StuScalaClass])
    println(stuCaseClass1)
    println(stuScalaClass1)

    println("--------------scala list json--------------")
    val list: List[StuCaseClass] = List(StuCaseClass("小明", 20, 90D),
      StuCaseClass("小红", 20, 90D),
      StuCaseClass("小花", 20, 90D),
      StuCaseClass(null, 20, 90D)
    )
    val listJson = mapper.writeValueAsString(list)
    println(listJson)

    val list1: ju.List[StuCaseClass] = mapper.readValue(listJson, new TypeReference[ju.List[StuCaseClass]]() {})
    println(list1)
    val list2: List[StuCaseClass] = mapper.readValue(listJson, new TypeReference[List[StuCaseClass]]() {})
    println(list2)
    val list3: mutable.ArrayBuffer[StuCaseClass] = mapper.readValue(listJson, new TypeReference[mutable.ArrayBuffer[StuCaseClass]]() {})
    println(list3)
  }
}

```

StuCaseClass：
```scala
package data

case class StuCaseClass
(
  name: String,
  age: Int,
  score: Double
){
  override def toString: String = "StuCaseClass{" + "name='" + name + '\'' + ", age=" + age + ", score=" + score + '}'
}
```

StuScalaClass：
```scala
package data

class StuScalaClass {
  var name: String = _
  var age: Int = _
  var score: Double = _
}
```

StuJavaClass(省略get set tostring方法)：
```java
package data;

public class StuJavaClass {
    private String name;
    private int age;
    private double score;
}
```

### 对应javabean的scala类
对应javabean的scala类就不需要做额外的处理了，不过要注意case类的话一定要提供无参的构造函数，不然无法实例化。

加上scala.beans.BeanProperty的注解scala类就具备java bean的特性了，不过case类要注意加上var，不然只会生成get方法。

```scala
package data

import com.fasterxml.jackson.databind.ObjectMapper

object ScalaBeanTest {
  def main(args: Array[String]): Unit = {
    val stuScalaBean = new StuScalaBeanClass("小花")
    println(stuScalaBean)
    stuScalaBean.setName("小明")

    println(stuScalaBean)

    val mapper = new ObjectMapper // create once, reuse
    val json = mapper.writeValueAsString(stuScalaBean)
    println(json)
    val stuScalaBean2 = mapper.readValue(json, classOf[StuScalaBeanClass])
    println(stuScalaBean2)

    val stuCaseBean = StuCaseBeanClass("小明", 20, 90D)
    stuCaseBean.setName("小玉")
    val json2 = mapper.writeValueAsString(stuCaseBean)
    println(json2)
    // case必须提供无参构造器
    val stuCaseBean2 = mapper.readValue(json, classOf[StuCaseBeanClass])
    println(stuCaseBean2)
  }
}

```

StuScalaBeanClass：
```scala
package data

import scala.beans.BeanProperty

class StuScalaBeanClass {
  @BeanProperty
  var name: String = _
  @BeanProperty
  var age: Int = _
  @BeanProperty
  var score: Double = _

  def this(name: String) {
    this()
    this.name = name
  }

  override def toString = s"StuScalaBeanClass($name, $age, $score)"
}
```

StuCaseBeanClass：
```scala
package data

import scala.beans.BeanProperty

case class StuCaseBeanClass
(
  @BeanProperty
  var name: String,
  @BeanProperty
  var age: Int,
  @BeanProperty
  var score: Double
) {

  def this() {
    this(null, 0, 0D)
  }

  override def toString: String = "StuCaseBeanClass{" + "name='" + name + '\'' + ", age=" + age + ", score=" + score + '}'
}

```




```scala

```