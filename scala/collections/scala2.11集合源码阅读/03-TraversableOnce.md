# TraversableOnce
TraversableLike也继承了TraversableLike，里面实现的方法基本都是函数式编程常用的方法，都是针对一次迭代的操作，reduce等。

## size
返回size
```scala
def size: Int = {
  var result = 0
  for (x <- self) result += 1
  result
}
```

## nonEmpty
返回!isEmpty
```scala
def nonEmpty: Boolean = !isEmpty
```

##  count(p)
返回符合条件的count
```scala
def count(p: A => Boolean): Int = {
  var cnt = 0
  for (x <- this)
    if (p(x)) cnt += 1

  cnt
}
```

## collectFirst[(PartialFunction[A, B])
找到第一个符合偏函数的，并返回偏函数执行后的结果。
```scala
/** Finds the first element of the traversable collection for which the given partial
 *  function is defined, and applies the partial function to it.
 *
 *  @param pf   the partial function
 *  @return     an option value containing pf applied to the first
 *              value for which it is defined, or `None` if none exists.
 *  @example    `Seq("a", 1, 5L).collectFirst({ case x: Int => x*10 }) = Some(10)`
 */
def collectFirst[B](pf: PartialFunction[A, B]): Option[B] = {
  // make sure to use an iterator or `seq`
  // 匿名函数中的return可以直接导致函数返回，这个挺神奇的
  self.toIterator.foreach(pf.runWith(b => return Some(b)))
  None
}
```

## foldLeft(B)((B, A) => B) 和 /:
经典方法。
```scala
def /:[B](z: B)(op: (B, A) => B): B = foldLeft(z)(op)

def foldLeft[B](z: B)(op: (B, A) => B): B = {
  var result = z
  // 靠，连个for循环都不写，真正的函数式编程啊，人才！
  this foreach (x => result = op(result, x))
  result
}

```

## foldRight(B)((A, B) => B) 和 :\
经典方法。
```scala
def :\[B](z: B)(op: (A, B) => B): B = foldRight(z)(op)

def foldRight[B](z: B)(op: (A, B) => B): B =
  reversed.foldLeft(z)((x, y) => op(y, x))
```

## fold(A1)((A1, A1) => A1)
经典方法。

```scala
def fold[A1 >: A](z: A1)(op: (A1, A1) => A1): A1 = foldLeft(z)(op)
```

## reduce系列
经典方法。
```scala
/** Applies a binary operator to all elements of this traversable collection,
 *  going left to right.
 *  $willNotTerminateInf
 *  $orderDependentFold
 *
 *  @param  op    the binary operator.
 *  @tparam  B    the result type of the binary operator.
 *  @return  the result of inserting `op` between consecutive elements of this traversable collection,
 *           going left to right:
 *           {{{
 *             op( op( ... op(x_1, x_2) ..., x_{n-1}), x_n)
 *           }}}
 *           where `x,,1,,, ..., x,,n,,` are the elements of this traversable collection.
 *  @throws UnsupportedOperationException if this traversable collection is empty.   */
def reduceLeft[B >: A](op: (B, A) => B): B = {
  if (isEmpty)
    throw new UnsupportedOperationException("empty.reduceLeft")

  var first = true
  var acc: B = 0.asInstanceOf[B]

  for (x <- self) {
    if (first) {
      acc = x
      first = false
    }
    else acc = op(acc, x)
  }
  acc
}

def reduceRight[B >: A](op: (A, B) => B): B = {
  if (isEmpty)
    throw new UnsupportedOperationException("empty.reduceRight")

  reversed.reduceLeft[B]((x, y) => op(y, x))
}

def reduceLeftOption[B >: A](op: (B, A) => B): Option[B] =
  if (isEmpty) None else Some(reduceLeft(op))

def reduceRightOption[B >: A](op: (A, B) => B): Option[B] =
  if (isEmpty) None else Some(reduceRight(op))

def reduce[A1 >: A](op: (A1, A1) => A1): A1 = reduceLeft(op)

def reduceOption[A1 >: A](op: (A1, A1) => A1): Option[A1] = reduceLeftOption(op)
```

## min/max
只要有`[B >: A]`，隐式的`Ordering[B]`就行。

利用reduceLeft是实现的，函数式编程的思想可以的。
```scala
def min[B >: A](implicit cmp: Ordering[B]): A = {
  if (isEmpty)
    throw new UnsupportedOperationException("empty.min")

  reduceLeft((x, y) => if (cmp.lteq(x, y)) x else y)
}

def max[B >: A](implicit cmp: Ordering[B]): A = {
  if (isEmpty)
    throw new UnsupportedOperationException("empty.max")

  reduceLeft((x, y) => if (cmp.gteq(x, y)) x else y)
}
```

## minBy/maxBy
顾名思义。

```scala
def maxBy[B](f: A => B)(implicit cmp: Ordering[B]): A = {
  if (isEmpty)
    throw new UnsupportedOperationException("empty.maxBy")

  var maxF: B = null.asInstanceOf[B]
  var maxElem: A = null.asInstanceOf[A]
  var first = true

  for (elem <- self) {
    val fx = f(elem)
    if (first || cmp.gt(fx, maxF)) {
      maxElem = elem
      maxF = fx
      first = false
    }
  }
  maxElem
}

def minBy[B](f: A => B)(implicit cmp: Ordering[B]): A = {
  if (isEmpty)
    throw new UnsupportedOperationException("empty.minBy")

  var minF: B = null.asInstanceOf[B]
  var minElem: A = null.asInstanceOf[A]
  var first = true

  for (elem <- self) {
    val fx = f(elem)
    if (first || cmp.lt(fx, minF)) {
      minElem = elem
      minF = fx
      first = false
    }
  }
  minElem
}
```

## mkString(sep)、mkString(start, sep, end)
经典方法。

调用的addString方法。
```scala
def mkString(start: String, sep: String, end: String): String =
  addString(new StringBuilder(), start, sep, end).toString

def mkString(sep: String): String = mkString("", sep, "")

def mkString: String = mkString("")
```

## addString
功能显而易见。
```scala
def addString(b: StringBuilder, start: String, sep: String, end: String): StringBuilder = {
  var first = true

  b append start
  for (x <- self) {
    if (first) {
      b append x
      first = false
    }
    else {
      b append sep
      b append x
    }
  }
  b append end

  b
}

def addString(b: StringBuilder, sep: String): StringBuilder = addString(b, "", sep, "")

def addString(b: StringBuilder): StringBuilder = addString(b, "")
```


## toArray、toList、toMap等
就是转换，可以转换很多。







