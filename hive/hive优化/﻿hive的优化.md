# ﻿hive的优化

## ﻿hive的优化
```
hive的优化：
1，分区，分桶。
2，尽量使用外部表
3，可以使用视图，避免重复查询
4，文件压缩格式：
	textfile 没有进行压缩，加载速度很快，查询效率高。占用存储量大。（一般对查询效率有要求，但是存储空间足够）
	rcfile 压缩格式，需要解压，查询速度相对慢一些，但是 压缩比高，占用空间少。
	hive不止有这些文件格式，还有其他的。
5，命名要规范。数据库名称，表名称的时候要规范。
	一般情况下，按照数据类型或者业务类型进行区分。要有解释说明。
6.SQL优化：
	尽量先指定分区，让参与计算的数据量越少越好。
	尽量将数据写入子查询。可以通过 SQL执行计划看下 流程 explain SQL。
	一般情况下，join是发生在where后面的，所以一般情况下，先过滤，再join。
7,合并小文件。hive2的操作会进行自动优化。
	可以通过临时表，进行合并小文件。减少map数量。
8,当sql优化已经完成，集群优化也已经完成，速度还是很慢。
	可以建一些临时表，或者叫做过渡表。把大任务拆成小任务，可以将大任务作为临时表，牺牲空间换时间。
	select ss.DEPTNO,d.DNAME from (select DEPTNO from (select DEPTNO,count(*) as cn from emp group 
	by DEPTNO)s  where s.cn>=4)ss left join dept d on ss.DEPTNO=d.DEPTNO; 
	比如：先将计算量稍微大子查询建一个临时表，insert overwrite emp_tmp as 
	select DEPTNO,count(*) as cn from emp group by DEPTNO
	可以简化sql
	select ss.DEPTNO,d.DNAME from (select DEPTNO from emp_tmp s  where s.cn>=4)ss
	left join dept d on ss.DEPTNO=d.DEPTNO;

9：可以使用mapjoin（），1.2以后自动默认启动mapjoin
	select /*+mapjoin(b)*/ a.xx,b.xxx from a left outer join b on a.id=b.id
10，hive数据倾斜：本质原因是：key的分布不均匀。
	现象：会出现少数或者一个reduce任务执行非常慢，达到99%的时候，还是需要很长时间，也叫长尾。
	1，看下业务上，数据源头能否对数据进行过滤，比如 key为 null的，业务层面进行优化。
	2，找到key重复的具体值，进行拆分，hash。异步求和。
	https://help.aliyun.com/document_detail/51020.html?spm=a2c4g.11186623.6.908.39ae690cbR0ZHG
11， 参数优化
	调整mapper和reducer的数量
	太多map导致启动产生过多开销
	按照输入数据量大小确定reducer数目set mapred.reduce.tasks=  默认3
	dfs -count  /分区目录/* 
	hive.exec.reducers.max设置阻止资源过度消耗

	参数调节
	set hive.map.aggr = true （hive2默认开启）
	Map 端部分聚合，相当于Combiner
	set hive.groupby.skewindata=true
```






