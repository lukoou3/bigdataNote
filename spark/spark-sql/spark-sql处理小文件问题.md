# spark-sql处理小文件问题

## 一、小文件产生的原因
1、在使用spark sql处理数据的过程中，如果有shuffle产生，依赖于spark.sql.shuffle.partitions配置信息，默认为200，当处理的数据量比较大时，通常会把该值调大，以避免单个分区处理的数据太大出现异常或者拖慢整个任务的执行时间。

2、如果没有shuffle产生，文件的数量依赖于数据源的文件数量以及文件是否可切分等特性决定任务的并发度即task数量，如果在进行数据清洗转换或者的过程中通常不会涉及shuffle，此时会产生很多小文件，造成资源的浪费，给NameNode增加压力。


## 二、如何解决小文件问题
1）、降低spark.sql.shuffle.partitions配置的值，但会影响处理的并发度
2）、使用repartition和coalesce 根据经验调整分区数的大小，但是太不灵活，如果使用spark-sql cli方式，就很不方便
3）、在数据入库的时候使用distribute by 字段或者rand(),但是此时对字段的选择就需要慎重
4）、spark sql adaptive 自适应框架


## 三、spark-sql adaptive框架解决小文件问题
1、打开自适应框架的开关
```
spark.sql.adaptive.enabled true
```

2、设置partition的上下限
```
spark.sql.adaptive.minNumPostShufflePartitions 10
spark.sql.adaptive.maxNumPostShufflePartitions 2000
```

3、设置单reduce task处理的数据大小
```
spark.sql.adaptive.shuffle.targetPostShuffleInputSize 134217728
spark.sql.adaptive.shuffle.targetPostShuffleRowCount 10000000
```

4、必须要触发shuffle，如果任务中只有map task，需要通过group by 或者distribute 触发shuffle的执行，只有触发shuffle，才能使用adaptive解决小文件问题



