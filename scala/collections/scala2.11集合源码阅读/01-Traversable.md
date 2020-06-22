# Traversable
Traversable是scala collection的顶层抽象trait，它只有一个抽象方法forEach，只要子类实现forEach方法，就能使用Traversable的方法，就连一些需要传递构建集合对象的隐式参数的方法也可以调用。

## 继承Traversable测试
TraversableImpl实现Traversable：
```scala
package com.collect

class TraversableImpl[+A](xs: A*) extends Traversable[A]{
	def foreach[U](f: A => U): Unit = {
		for (x <- xs) {
			f(x)
		}
	}
}

object TraversableImpl {
	def apply[A](xs: A*): TraversableImpl[A] = new TraversableImpl(xs:_*)
}
```

测试：
```scala
package com.collect

object TraversableTest {

	def main(args: Array[String]): Unit = {
		val items = TraversableImpl(1, 2, 3, 4, 5)

		println(items.head)
		println(items.tail)

		println(items.toList)
		println(items.filter(_ % 2 == 0))

		/**
			* 这个方法能够调用应该是默认引入了一些集合类的Build隐士对象
			* map[B, That](f: A => B)(implicit bf: CanBuildFrom[Traversable[A], B, That]): That
			*/
		println(items.map(_ + 1))
	}

}
```

输出：
```
1
List(2, 3, 4, 5)
List(1, 2, 3, 4, 5)
List(2, 4)
List(2, 3, 4, 5, 6)
```

## Traversable源码
Traversable本身并没有实现什么方法，它的方法主要从`TraversableLike[A, Traversable[A]]`和`TraversableOnce[A]`中继承而来。


```scala
package scala
package collection

import generic._
import mutable.Builder
import scala.util.control.Breaks

/** A trait for traversable collections.
 *  All operations are guaranteed to be performed in a single-threaded manner.
 *
 *  $traversableInfo
 */
trait Traversable[+A] extends TraversableLike[A, Traversable[A]]
                         with GenTraversable[A]
                         with TraversableOnce[A]
                         with GenericTraversableTemplate[A, Traversable] {
  override def companion: GenericCompanion[Traversable] = Traversable

  override def seq: Traversable[A] = this

  /* The following methods are inherited from TraversableLike
   *
  override def isEmpty: Boolean
  override def size: Int
  override def hasDefiniteSize
  override def ++[B >: A, That](xs: GenTraversableOnce[B])(implicit bf: CanBuildFrom[Traversable[A], B, That]): That
  override def map[B, That](f: A => B)(implicit bf: CanBuildFrom[Traversable[A], B, That]): That
  override def flatMap[B, That](f: A => GenTraversableOnce[B])(implicit bf: CanBuildFrom[Traversable[A], B, That]): That
  override def filter(p: A => Boolean): Traversable[A]
  override def remove(p: A => Boolean): Traversable[A]
  override def partition(p: A => Boolean): (Traversable[A], Traversable[A])
  override def groupBy[K](f: A => K): Map[K, Traversable[A]]
  override def foreach[U](f: A =>  U): Unit
  override def forall(p: A => Boolean): Boolean
  override def exists(p: A => Boolean): Boolean
  override def count(p: A => Boolean): Int
  override def find(p: A => Boolean): Option[A]
  override def foldLeft[B](z: B)(op: (B, A) => B): B
  override def /: [B](z: B)(op: (B, A) => B): B
  override def foldRight[B](z: B)(op: (A, B) => B): B
  override def :\ [B](z: B)(op: (A, B) => B): B
  override def reduceLeft[B >: A](op: (B, A) => B): B
  override def reduceLeftOption[B >: A](op: (B, A) => B): Option[B]
  override def reduceRight[B >: A](op: (A, B) => B): B
  override def reduceRightOption[B >: A](op: (A, B) => B): Option[B]
  override def head: A
  override def headOption: Option[A]
  override def tail: Traversable[A]
  override def last: A
  override def lastOption: Option[A]
  override def init: Traversable[A]
  override def take(n: Int): Traversable[A]
  override def drop(n: Int): Traversable[A]
  override def slice(from: Int, until: Int): Traversable[A]
  override def takeWhile(p: A => Boolean): Traversable[A]
  override def dropWhile(p: A => Boolean): Traversable[A]
  override def span(p: A => Boolean): (Traversable[A], Traversable[A])
  override def splitAt(n: Int): (Traversable[A], Traversable[A])
  override def copyToBuffer[B >: A](dest: Buffer[B])
  override def copyToArray[B >: A](xs: Array[B], start: Int, len: Int)
  override def copyToArray[B >: A](xs: Array[B], start: Int)
  override def toArray[B >: A : ClassTag]: Array[B]
  override def toList: List[A]
  override def toIterable: Iterable[A]
  override def toSeq: Seq[A]
  override def toStream: Stream[A]
  override def sortWith(lt : (A,A) => Boolean): Traversable[A]
  override def mkString(start: String, sep: String, end: String): String
  override def mkString(sep: String): String
  override def mkString: String
  override def addString(b: StringBuilder, start: String, sep: String, end: String): StringBuilder
  override def addString(b: StringBuilder, sep: String): StringBuilder
  override def addString(b: StringBuilder): StringBuilder
  override def toString
  override def stringPrefix : String
  override def view
  override def view(from: Int, until: Int): TraversableView[A, Traversable[A]]
  */
}

/** $factoryInfo
 *  The current default implementation of a $Coll is a `List`.
 */
object Traversable extends TraversableFactory[Traversable] { self =>

  /** Provides break functionality separate from client code */
  private[collection] val breaks: Breaks = new Breaks

  /** $genericCanBuildFromInfo */
  implicit def canBuildFrom[A]: CanBuildFrom[Coll, A, Traversable[A]] = ReusableCBF.asInstanceOf[GenericCanBuildFrom[A]]

  def newBuilder[A]: Builder[A, Traversable[A]] = immutable.Traversable.newBuilder[A]
}

/** Explicit instantiation of the `Traversable` trait to reduce class file size in subclasses. */
abstract class AbstractTraversable[+A] extends Traversable[A]
```

### Traversable源码继承的主要方法
根据源码中的注释：
```scala
/* The following methods are inherited from TraversableLike
 *
override def isEmpty: Boolean
override def size: Int
override def hasDefiniteSize
override def ++[B >: A, That](xs: GenTraversableOnce[B])(implicit bf: CanBuildFrom[Traversable[A], B, That]): That
override def map[B, That](f: A => B)(implicit bf: CanBuildFrom[Traversable[A], B, That]): That
override def flatMap[B, That](f: A => GenTraversableOnce[B])(implicit bf: CanBuildFrom[Traversable[A], B, That]): That
override def filter(p: A => Boolean): Traversable[A]
override def remove(p: A => Boolean): Traversable[A]
override def partition(p: A => Boolean): (Traversable[A], Traversable[A])
override def groupBy[K](f: A => K): Map[K, Traversable[A]]
override def foreach[U](f: A =>  U): Unit
override def forall(p: A => Boolean): Boolean
override def exists(p: A => Boolean): Boolean
override def count(p: A => Boolean): Int
override def find(p: A => Boolean): Option[A]
override def foldLeft[B](z: B)(op: (B, A) => B): B
override def /: [B](z: B)(op: (B, A) => B): B
override def foldRight[B](z: B)(op: (A, B) => B): B
override def :\ [B](z: B)(op: (A, B) => B): B
override def reduceLeft[B >: A](op: (B, A) => B): B
override def reduceLeftOption[B >: A](op: (B, A) => B): Option[B]
override def reduceRight[B >: A](op: (A, B) => B): B
override def reduceRightOption[B >: A](op: (A, B) => B): Option[B]
override def head: A
override def headOption: Option[A]
override def tail: Traversable[A]
override def last: A
override def lastOption: Option[A]
override def init: Traversable[A]
override def take(n: Int): Traversable[A]
override def drop(n: Int): Traversable[A]
override def slice(from: Int, until: Int): Traversable[A]
override def takeWhile(p: A => Boolean): Traversable[A]
override def dropWhile(p: A => Boolean): Traversable[A]
override def span(p: A => Boolean): (Traversable[A], Traversable[A])
override def splitAt(n: Int): (Traversable[A], Traversable[A])
override def copyToBuffer[B >: A](dest: Buffer[B])
override def copyToArray[B >: A](xs: Array[B], start: Int, len: Int)
override def copyToArray[B >: A](xs: Array[B], start: Int)
override def toArray[B >: A : ClassTag]: Array[B]
override def toList: List[A]
override def toIterable: Iterable[A]
override def toSeq: Seq[A]
override def toStream: Stream[A]
override def sortWith(lt : (A,A) => Boolean): Traversable[A]
override def mkString(start: String, sep: String, end: String): String
override def mkString(sep: String): String
override def mkString: String
override def addString(b: StringBuilder, start: String, sep: String, end: String): StringBuilder
override def addString(b: StringBuilder, sep: String): StringBuilder
override def addString(b: StringBuilder): StringBuilder
override def toString
override def stringPrefix : String
override def view
override def view(from: Int, until: Int): TraversableView[A, Traversable[A]]
*/
```

### object Traversable中的breaks属性
用于循环的停止，从这里我们也可以看到scala.util.control.Breaks的用法，**需要new 一个对象**。
```scala
import scala.util.control.Breaks

...

/** Provides break functionality separate from client code */
private[collection] val breaks: Breaks = new Breaks
```

其他类(TraversableLike)中引用breaks：
```scala
def isEmpty: Boolean = {
  var result = true
  breakable {
    for (x <- this) {
      result = false
      break
    }
  }
  result
}
```



```scala

```
