## Hive典型应用场景之行列转换
在使用Hive处理数据时，经常遇到行列转换的场景，本文将对Hive的行列转换操作做详细的说明。

### 行转列
##### 1）多行转多列 
假设数据表 
row2col：
```
col1   col2    col3
a      c       1
a      d       2
a      e       3  
b      c       4
b      d       5
b      e       6
```

现在要将其转化为：
```
col1   c      d      e
a      1      2      3
b      4      5      6
```

此时需要使用到max(case … when … then … else 0 end)，仅限于转化的字段为数值类型，且为正值的情况。

HQL语句为：
```sql
select col1,
max(case col2 when 'c' then col3 else 0 end) as c,
max(case col2 when 'd' then col3 else 0 end) as d,
max(case col2 when 'e' then col3 else 0 end) as e
from row2col
group by col1;
```

##### 2）多行转单列 
假设数据表 
row2col：
```
col1    col2    col3
a       b       1
a       b       2
a       b       3
c       d       4
c       d       5
c       d       6
```

现在要将其转化为：
```
col1    col2    col3
a       b       1,2,3
c       d       4,5,6
```

此时需要用到两个内置的UDF： 
a）cocat_ws(参数1，参数2)，用于进行字符的拼接 
参数1—指定分隔符 
参数2—拼接的内容 
b）collect_set()，它的主要作用是将某字段的值进行去重汇总，产生array类型字段。

HQL语句为：
```sql
select col1, col2, concat_ws(',', collect_set(col3)) as col3
from row2col
group by col1, col2;
```
注意：由于使用concat_ws()函数，collect_set()中的字段必须为string类型，如果是其他类型可使用cast(col3 as string)将其转换为string类型。

### 列转行
##### 1）多列转多行 
假设有数据表 
col2row：
```
col1   c      d      e
a      1      2      3
b      4      5      6
```
现要将其转化为：
```
col1   col2    col3
a      c       1
a      d       2
a      e       3
b      c       4
b      d       5
b      e       6
```

这里需要使用union进行拼接。

HQL语句为：
```sql
select col1, 'c' as col2, c as col3 from col2row
UNION
select col1, 'd' as col2, d as col3 from col2row
UNION
select col1, 'e' as col2, e as col3 from col2row
order by col1, col2;
```

##### 2）单列转多行 
假设有数据表 
col2row：
```
col1    col2    col3
a       b       1,2,3
c       d       4,5,6
```

现要将其转化为：
```
col1    col2    col3
a       b       1
a       b       2
a       b       3
c       d       4
c       d       5
c       d       6
```

这里需要使用UDTF（表生成函数）explode()，该函数接受array类型的参数，其作用恰好与collect_set相反，实现将array类型数据行转列。explode配合lateral view实现将某列数据拆分成多行。

HQL语句为：
```sql
select col1, col2, lv.col3 as col3
from col2row 
lateral view explode(split(col3, ',')) lv as col3;
```


