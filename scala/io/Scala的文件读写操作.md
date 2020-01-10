## Scala的文件读写操作
Scala读取文本文件使用scala.io.Source.fromFile即可

其它的io操作Scala并未提供，写入文本文件使用使用java.io.PrintWriter即可

## 读取文本文件
Source.fromFile使用十分方便：
```scala
import scala.io.Source

object Test {
   def main(args: Array[String]) {
      println("文件内容为:" )

      Source.fromFile("test.txt" ).foreach{ 
         print 
      }
   }
}
```
getLines返回的是迭代器：
```scala
//文件读取
val file=Source.fromFile("D:\\a.txt", "uft-8")
for(line <- file.getLines)
{
    println(line)
}
file.close
```

## 写入文本文件

```scala
import java.io.FileWriter

//文件追加
val out = new FileWriter("/root/test/test.txt",true)
for (i <- 0 to 15){
    out.write(i.toString)
}
out.close()

//文件写入
val writer = new PrintWriter(new File("D:\\saveTextTitle.txt"))
for(i <- 1 to 10)
    writer.println(i)// 这里是自动换行 不用再加\n 切记切记    
}
writer.close()
```