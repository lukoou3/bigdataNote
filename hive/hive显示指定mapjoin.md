# hive显示指定mapjoin
```
https://www.cnblogs.com/leodaxin/p/11005249.html
https://www.cnblogs.com/MOBIN/p/5702580.html
```
## 显示指定mapjoin
注释的方式强制Hive使用Mapjoin：
```sql
SELECT /*+ MAPJOIN(smalltable)*/  .key,value
FROM smalltable JOIN bigtable ON smalltable.key = bigtable.key
```

支持spark 

## Hive MapJoin
### 摘要
MapJoin是Hive的一种优化操作，其适用于小表JOIN大表的场景，由于表的JOIN操作是在Map端且在内存进行的，所以其并不需要启动Reduce任务也就不需要经过shuffle阶段，从而能在一定程度上节省资源提高JOIN效率

### 使用
**方法一：**    
在Hive0.11前，必须使用MAPJOIN来标记显示地启动该优化操作，由于其需要将小表加载进内存所以要注意小表的大小
```sql
SELECT /*+ MAPJOIN(smalltable)*/  .key,value
FROM smalltable JOIN bigtable ON smalltable.key = bigtable.key
```

**方法二：**    
在Hive0.11后，Hive默认启动该优化，也就是不在需要显示的使用MAPJOIN标记，其会在必要的时候触发该优化操作将普通JOIN转换成MapJoin，可以通过以下两个属性来设置该优化的触发时机
```sql
hive.auto.convert.join
```
默认值为true，自动开户MAPJOIN优化
```sql
hive.mapjoin.smalltable.filesize
```
默认值为2500000(25M),通过配置该属性来确定使用该优化的表的大小，如果表的大小小于此值就会被加载进内存中
 
注意：使用默认启动该优化的方式如果出现默名奇妙的BUG(比如MAPJOIN并不起作用),就将以下两个属性置为fase手动使用MAPJOIN标记来启动该优化
```sql
hive.auto.convert.join=false(关闭自动MAPJOIN转换操作)
hive.ignore.mapjoin.hint=false(不忽略MAPJOIN标记)
```

对于以下查询是不支持使用方法二(MAPJOIN标记)来启动该优化的
```sql
select /*+MAPJOIN(smallTableTwo)*/ idOne, idTwo, value FROM
  ( select /*+MAPJOIN(smallTableOne)*/ idOne, idTwo, value FROM
    bigTable JOIN smallTableOne on (bigTable.idOne = smallTableOne.idOne)                                                  
  ) firstjoin                                                            
  JOIN                                                                 
  smallTableTwo ON (firstjoin.idTwo = smallTableTwo.idTwo)  
```

但是，如果使用的是方法一即没有MAPJOIN标记则以上查询语句将会被作为两个MJ执行，进一步的，如果预先知道表大小是能够被加载进内存的，则可以通过以下属性来将两个MJ合并成一个MJ
```sql
hive.auto.convert.join.noconditionaltask：Hive在基于输入文件大小的前提下将普通JOIN转换成MapJoin，并是否将多个MJ合并成一个
hive.auto.convert.join.noconditionaltask.size：多个MJ合并成一个MJ时，其表的总的大小须小于该值，同时hive.auto.convert.join.noconditionaltask必须为true
```




