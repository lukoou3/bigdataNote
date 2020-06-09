# spark dataframe,rdd unpersist的坑

使用spark dataframe的时候，发现缓存了两个dataframe，dataframe2依赖于dataframe1，是从dataframe1转过来的，数据预处理完毕后把dataframe1释放了(unpersist)，发现dataframe2竟然也被释放了。

网上搜了一下，发现别人也有这个问题，这是spark的一个bug，之后修复了。

## 网上的描述
`https://blog.csdn.net/Code_LT/article/details/88758220`

目前使用的Spark 2.1.0有一个很坑爹的问题，如果persist一个df1后unpersist 与df1相关的df0，那么df1也会被unpersist掉，导致后续用到df1的地方又需要重新算df1，降低性能。这个问题直到Spark2.4.0才解决。问题复现如下：

但是rdd的persist不会因为linage的rdd被unpersist后而消失

df.sqlContext.clearCache可以清空所有df的persist，但是清不掉rdd直接persist的。

而
```scala
def unpersistUnuse( sc: SparkContext) = {
val persistRdds = sc.getPersistentRDDs
persistRdds.foreach(x => x._2.unpersist() )
}
```
则可清除掉所有df，rdd的缓存

 
即使吧df转为rdd persist下来也是没用的，用到df时还是会重复计算


## cache触发的条件
还发现一个问题，cache不一定把整个数据集一次cache完，要看具体的算子。比如只调用一个first是不会缓存整个rdd的。

一下是网上的描述：
`https://blog.csdn.net/Code_LT/article/details/87719379`
```
由于Spark操作都是底层rdd，所以这里仅以rdd做介绍，dataset和daraframe原理一样。


由于rdd的懒加载机制，官方文档说明在rdd.persist时需要用rdd的action来触发其执行。

有时我们为了追求性能，会选用一些性能高的操作，如rdd.take(1),rdd.isEmpty()来触发。


但是！！！


如果rdd具有多个partition，这些高性能操作并不会将所有partition全部persist下来，而是仅persist一个partition。

若想全部persist下来，则要用rdd.count，rdd.foreachParition等遍历所有parition的操作！
```





