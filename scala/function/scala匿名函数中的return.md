# scala匿名函数中的return

## 现象
`https://blog.csdn.net/zero__007/article/details/53241043`

```scala
object Test {
    def main(args: Array[String]) {
        val list = List("A", "B", "C")
        list.foreach(s=>{
            if (s == "C") {
                println("ok, do something.")
                return;
            }
        })
        println("111")
    }
}
```
运行结果：
```
ok, do something.
```
是不是感觉很纳闷，没有打印111。实质上scala里的lambda表达式中的return背后实际是通过特定的异常来实现的。return在嵌套的匿名函数里是无法跳出外层函数的，所以编译器通过抛出scala.runtime.NonLocalReturnControl异常来实现跳出最外层。所有的lambda中使用return都是如此。

如下示例，实质上还是会取得返回值：
```scala
object Test {
    def main(args: Array[String]) {
        println(test)
        println("111")
    }

    def test: Boolean = {
        val list = List("A", "B", "C")
        list.foreach(s => {
            if (s == "C") {
                println("ok, do something.")
                return true
            }
        })
        false
    }
}
```

运行结果：
```
ok, do something.
true
111
```

可以看看它编译的中间环节：

$ scalac -Xprint:explicitouter Test.scala
```scala
[[syntax trees at end of             explicitouter]] // Test.scala
package org.zero {
  object Test extends Object {
    def <init>(): org.zero.Test.type = {
      Test.super.<init>();
      ()
    };
    def main(args: Array[String]): Unit = {
      scala.this.Predef.println(Test.this.test());
      scala.this.Predef.println("111")
    };
    def test(): Boolean = {
      <synthetic> val nonLocalReturnKey1: Object = new Object();
      try {
        val list: List[String] = immutable.this.List.apply[String](scala.this.Predef.wrapRefArray[String](Array[String]{"A", "B", "C"}));
        list.foreach[Unit]({
          @SerialVersionUID(value = 0) final <synthetic> class $anonfun extends scala.runtime.AbstractFunction1[String,Unit] with Serializable {
            def <init>(): <$anon: String => Unit> = {
              $anonfun.super.<init>();
              ()
            };
            final def apply(s: String): Unit = if (s.==("C"))
              {
                scala.this.Predef.println("ok, do something.");
                throw new scala.runtime.NonLocalReturnControl$mcZ$sp(nonLocalReturnKey1, true)
              }
            else
              ()
          };
          (new <$anon: String => Unit>(): String => Unit)
        });
        false
      } catch {
        case (ex @ (_: scala.runtime.NonLocalReturnControl[Boolean @unchecked])) => if (ex.key().eq(nonLocalReturnKey1))
          ex.value$mcZ$sp()
        else
          throw ex
      }
    }
  }
}
```
可以发现，对于return true，scala将它封装成了`scala.runtime.NonLocalReturnControl$mcZ$sp(nonLocalReturnKey1, true)`，在之后的catch块中取得NonLocalReturnControl中的value值然后返回。


Java版：
```java
public static void main(String[] args) {
    List<String> list = Arrays.asList("a","b");
    list.forEach(s->{
        if(s.equals("b")) return;
    });
    System.out.println(111);
}
```
运行结果：
```
111
```

Java对于lamdba表达式中的return处理还是按照之前逻辑处理的。

## lambda表达式里的return是抛异常实现的
`http://hongjiang.info/scala-pitfalls-27/`

尽管Scala和其他函数式编程都不太鼓励使用return，但我不喜欢太多缩进的代码，所以很少用较多的逻辑嵌套（除非是那种非常对称的嵌套），而是喜欢将不满足条件的先return掉。最近遇到一个scala里的流控陷阱，即在lambda里的return背后实际是通过特定的异常来实现的。

对于流控和异常捕获之前也遇到过其他陷阱，但稍不留意仍可能重犯，比如下面这段代码：
```scala
try {
    ...
    for (topicMeta <- resp.topicsMetadata; partMeta <- topicMeta.partitionsMetadata) {
      if (topicMeta.topic == p.topic && partMeta.partitionId == p.partition) {
        redisClient.hset(key, field, node.host + ":" + node.port)
        return
      }
    }
} catch {
    case e: Throwable =>
    ...
}
```

它是一段在actor里的逻辑，因为不希望非预期异常导致这个actor重启，所以是对Throwable进行的捕获，然而运行时竟捕获到了scala.runtime.NonLocalReturnControl$mcV$sp这样的异常。for语法糖容易让人忘记它里面的操作可能是一段匿名函数，简化一下这个例子：
```scala
➜  cat Test.scala
object Test {
    def main(args: Array[String]) {
        val list = List("A", "B", "C")
        for (e1 <- list) {
            if (e1 == "C") {
                println("ok, do something.")
                return
            }
        }
    }   
}
```

看看它编译的中间环节：
```scala
➜  scalac -Xprint:explicitouter Test.scala
[[syntax trees at end of             explicitouter]] // Test.scala
package <empty> {
object Test extends Object {
def <init>(): Test.type = {
  Test.super.<init>();
  ()
};
def main(args: Array[String]): Unit = {
  <synthetic> val nonLocalReturnKey1: Object = new Object();
  try {
    val list: List[String] = immutable.this.List.apply[String](scala.this.Predef.wrapRefArray[String](Array[String]{"A", "B", "C"}));
    list.foreach[Unit]({
      @SerialVersionUID(value = 0) final <synthetic> class $anonfun extends scala.runtime.AbstractFunction1[String,Unit] with Serializable {
        def <init>(): <$anon: String => Unit> = {
          $anonfun.super.<init>();
          ()
        };
        final def apply(e1: String): Unit = if (e1.==("C"))
          {
            scala.this.Predef.println("ok, do something.");
            throw new scala.runtime.NonLocalReturnControl$mcV$sp(nonLocalReturnKey1, ())
          }
        else
          ()
      };
      (new <$anon: String => Unit>(): String => Unit)
    })
  } catch {
    case (ex @ (_: scala.runtime.NonLocalReturnControl[Unit @unchecked])) => if (ex.key().eq(nonLocalReturnKey1))
      ex.value$mcV$sp()
    else
      throw ex
  }
}
}
}
```

很明显return在嵌套的匿名函数里是无法跳出外层函数的，所以编译器通过抛出 scala.runtime.NonLocalReturnControl 异常来实现跳出最外层。所有的lambda中使用return都是如此：
```scala
def main(args: Array[String]) {
    val lambda: String => Unit =
        (str: String) => { if ("hit" == str) return } //跳出main

    try {
        lambda("hit")
    } catch {
        case e: Throwable => //scala.runtime.NonLocalReturnControl
        e.printStackTrace()
    }
}
```

还是要注意对Throwable的捕获，不要干扰流控逻辑：
```scala
try{
    ...
}catch {
case e0: ControlThrowable => throw e0 // 不要干预流控的异常
case e1: Throwable => e1.printStackTrace
}   
```

## break与异常捕获
`http://hongjiang.info/scala-pitfalls-24/`

这段代码如果把异常捕获部分的Exception替换为Throwable会有什么不同？
```scala
import scala.util.control.Breaks.break
import scala.util.control.Breaks.breakable

object Main {

  @throws(classOf[Exception])
  def prepare() = false

  def main(args:Array[String]) {
    var i = 0

    while(i < 3) {
      breakable {

        try{
          i+=1
          if(!prepare()) break
          println("do something here")
        }catch {
          //case e: Throwable => e.printStackTrace
          case e: Exception => e.printStackTrace
        }

        println("done")
      }
    }

  }
}
```

问题的关键在于scala里的break是通过异常机制实现的流控，与java里完全不同。break是抛出了一个BreakControl的异常，也是从Throwable接口继承下来的。所以当应用在捕获异常时，try代码块里有break流控语句，需要注意对流控异常不要干预，如果这种情况下真要捕获Throwable的话，正确的方式是：

```scala
try{
    if (...) break
    ...

}catch {
    case e0: ControlThrowable => throw e0 // 不要干预流控的异常
    case e1: Throwable => e1.printStackTrace
}
```

