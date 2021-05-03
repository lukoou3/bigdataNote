
scala repl 中加载jar


```scala
D:\IdeaWorkspace\FlinkNote\Flink12\target>scala -classpath FlinkNote-jar-with-dependencies.jar
Welcome to Scala 2.11.12 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_181).
Type in expressions for evaluation. Or try :help.

scala> import scala.stream.reflect.BaseJavaPojoTest
import scala.stream.reflect.BaseJavaPojoTest

scala> BaseJavaPojoTest.main(null)
class scala.Tuple2
class scala.Tuple2
class scala.stream.reflect.BaseJavaPojo
class scala.stream.reflect.BaseJavaPojo
class scala.stream.reflect.BaseScalaPojo
class scala.stream.reflect.BaseScalaPojo

scala> :q

D:\IdeaWorkspace\FlinkNote\Flink12\target>scala -cp FlinkNote-jar-with-dependencies.jar
Welcome to Scala 2.11.12 (Java HotSpot(TM) 64-Bit Server VM, Java 1.8.0_181).
Type in expressions for evaluation. Or try :help.

scala> import scala.stream.reflect.BaseJavaPojoTest
import scala.stream.reflect.BaseJavaPojoTest

scala>
```