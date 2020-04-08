# SQL优化示例
`https://help.aliyun.com/document_detail/102614.html?spm=a2c4g.11186623.6.1049.5bce6d67JHt0yM`

[toc]

本文为您介绍SQL优化示例。

## Join语句中Where条件的位置
当两个表进行Join操作时，主表的Where限制可以写在最后，但从表分区限制条件不要写在Where条件中，建议写在ON条件或者子查询中。主表的分区限制条件可以写在Where条件中（最好先用子查询过滤）。示例如下。
```sql
select * from A join (select * from B where dt=20150301)B on B.id=A.id where A.dt=20150301； 
select * from A join B on B.id=A.id where B.dt=20150301； --不允许 
select * from (select * from A where dt=20150301)A join (select * from B where dt=20150301)B on B.id=A.id；
```
第二个语句会先Join，后进行分区裁剪，数据量变大，性能下降。在实际使用过程中，应该尽量避免第二种用法。

## 数据倾斜
产生数据倾斜的根本原因是有少数Worker处理的数据量远远超过其他Worker处理的数据量，从而导致少数Worker的运行时长远远超过其他Worker的平均运行时长，从而导致整个任务运行时间超长，造成任务延迟。

更多数据倾斜优化的详情请参见其它计算长尾调优。

### Join造成的数据倾斜
造成Join数据倾斜的原因是Join on的key分布不均匀。假设还是上述示例语句，现在将大表A和小表B进行Join操作，运行如下语句。
```sql
select * from A join B on A.value= B.value;
```

此时，复制logview的链接并打开webcosole页面，双击执行Join操作的fuxi job，可以看到此时在[Long-tails]区域有长尾，表示数据已经倾斜了。
![](assets/markdown-img-paste-20200408134355506.png)

此时您可通过如下方法进行优化。

由于表B是个小表并且没有超过512MB，您可将上述语句优化为**mapjoin**语句再执行，语句如下。
```sql
select /*+ MAPJOIN(B) */ * from A join B on A.value= B.value;
```

您也可将倾斜的key用单独的逻辑来处理，例如经常发生两边的key中有大量null数据导致了倾斜。则需要在Join前**先过滤掉null**的数据或者**补上随机数**，然后再进行Join，示例如下。
```sql
select * from A join B
on case when A.value is null then concat('value',rand() ) else A.value end = B.value;
```

在实际场景中，如果您知道数据倾斜了，但无法获取导致数据倾斜的key信息，那么可以使用一个**通用的方案**，查看数据倾斜，如下所示。

例如：`select * from a join b on a.key=b.key;` 产生数据倾斜。 
您可以执行： 
```sql
select left.key, left.cnt * right.cnt from 
(select key, count(*) as cnt from a group by key) left 
join
(select key, count(*) as cnt from b group by key) right
on left.key=right.key;
```

**查看key的分布**，可以判断a join b时是否会有数据倾斜。

### group by倾斜
造成group by倾斜的原因是group by的key分布不均匀。

假设表A内有两个字段（key，value），表内的数据量足够大，并且key的值分布不均，运行语句如下所示。
```sql
select key,count(value) from A group by key;
```
当表中的数据足够大时，您会在webcosole页面看见长尾。若想解决这个问题，您需要在执行SQL前设置防倾斜的参数，设置语句为**set odps.sql.groupby.skewindata=true**。

### 错误使用动态分区造成的数据倾斜
动态分区的SQL，在MaxCompute中会默认增加一个Reduce，用来将相同分区的数据合并在一起。这样做的好处，如下所示。

* 可减少MaxCompute系统产生的小文件，使后续处理更快速。    
* 可避免一个Worker输出文件很多时占用内存过大。  

但也正是因为这个Reduce的引入，导致分区数据如果有倾斜的话，会发生长尾。因为相同的数据最多只会有10个Worker处理，所以数据量大，则会发生长尾，示例如下。
```sql
insert overwrite table A2 partition(dt) select split_part(value,'\t',1) as field1, split_part(value,'\t',2) as field2, dt from A where dt='20151010';
```

这种情况下，没有必要使用动态分区，所以可以改为如下语句：
```sql
insert overwrite table A2 partition(dt='20151010') 
select
split_part(value,'\t',1) as field1,
split_part(value,'\t',2) as field2
from A 
where dt='20151010';
```

## 窗口函数的优化
如果您的SQL语句中用到了窗口函数，一般情况下每个窗口函数会形成一个Reduce作业。如果窗口函数略多，那么就会消耗资源。在某些特定场景下，窗口函数是可以进行优化的。

* 窗口函数over后面要完全相同，要有相同的分组和排序条件。    
* 多个窗口函数在同一层SQL执行。  

**符合上述两个条件的窗口函数会合并为一个Reduce执行**。SQL示例如下所示。
```sql
select
rank()over(partition by A order by B desc) as rank,
row_number()over(partition by A order by B desc) as row_num
from MyTable;
```

## 子查询改Join
例如有一个子查询，如下所示。
```sql
SELECT * FROM table_a a WHERE a.col1 IN (SELECT col1 FROM table_b b WHERE xxx);
```

当此语句中的table_b子查询返回的col1的个数超过1000个时，系统会报错为records returned from subquery exceeded limit of 1000。此时您可以使用Join语句来代替，如下所示。
```sql
SELECT a.* FROM table_a a JOIN (SELECT DISTINCT col1 FROM table_b b WHERE xxx) c ON (a.col1 = c.col1)
```

**说明**:

* **如果没用Distinct，而子查询c返回的结果中有相同的col1的值，可能会导致a表的结果数变多。**    
* **因为Distinct子句会导致查询全落到一个Worker里，如果子查询数据量比较大的话，可能会导致查询比较慢。**    
* **如果已经从业务上控制了子查询里的col1不可能会重复，例如查的是主键字段，为了提高性能，可以把Distinct去掉。**  



```sql

```