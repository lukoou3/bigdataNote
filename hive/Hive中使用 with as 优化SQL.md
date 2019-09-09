# Hive中使用 with as 优化SQL
**背景**：  
当我们书写一些结构相对复杂的SQL语句时，可能某个子查询在多个层级多个地方存在重复使用的情况，这个时候我们可以使用 with as 语句将其独立出来，极大提高SQL可读性，简化SQL~

注：目前 oracle、sql server、hive等均支持 with as 用法，但 **mysql并不支持！**

2019-05-31更新：MySQL8.0大量更新优化，支持Common table expressions，即支持 with 语法！

## 一、介绍
with as 也叫做子查询部分，首先定义一个sql片段，该sql片段会被整个sql语句所用到，为了让sql语句的可读性更高些，作为提供数据的部分，也常常用在union等集合操作中。

with as就类似于一个视图或临时表，可以用来存储一部分的sql语句作为别名，不同的是with as 属于一次性的，而且必须要和其他sql一起使用才可以！

其最大的好处就是适当的**提高代码可读性**，而且如果with子句在后面要多次使用到，这可以大大的**简化SQL**；更重要的是：一次分析，多次使用，这也是为什么会提供性能的地方，达到了“少读”的目标。

## 二、使用
```sql
WITH t1 AS (
  SELECT *
  FROM carinfo
), 
t2 AS (
  SELECT *
  FROM car_blacklist
)
SELECT *
FROM t1, t2
```
**注意：这里必须要整体作为一条sql查询，即with as语句后不能加分号，不然会报错。**

## 三、注意事项
1. with子句必须在引用的select语句之前定义,同级with关键字只能使用一次,多个只能用逗号分割；最后一个with 子句与下面的查询之间不能有逗号，只通过右括号分割,with 子句的查询必须用括号括起来.

以下写法会报错：
```sql
with t1 as (select * from carinfo)
with t2 as (select * from car_blacklist)
select * from t1,t2
```

```sql
with t1 as (select * from carinfo);
select * from t1
```

2.如果定义了with子句，但其后没有跟select查询，则会报错！

以下写法会报错：
```sql
with t1 as (select * from carinfo)
```

正确写法（没有使用 t1没关系，其后有select就行）：
```sql
with t1 as (select * from carinfo)
select * from carinfo
```

3.前面的with子句定义的查询在后面的with子句中可以使用。但是一个with子句内部不能嵌套with子句！

正确写法：
```sql
with t1 as (select * from carinfo),
t2 as (select t1.id from t1)
select * from t2
```

## 四、例子
1、在 select 中使用
```sql
with q1 as ( select key from src where key = '5')
select *
from q1;
 
-- from style
with q1 as (select * from src where key= '5')
from q1
select *;
  
-- chaining CTEs
with q1 as ( select key from q2 where key = '5'),
q2 as ( select key from src where key = '5')
select * from (select key from q1) a;
  
-- union example
with q1 as (select * from src where key= '5'),
q2 as (select * from src s2 where key = '4')
select * from q1 union all select * from q2;
```

2、在 insert 中使用
```sql
-- insert example
create table s1 like src;
with q1 as ( select key, value from src where key = '5')
from q1
insert overwrite table s1
select *;
 
-- insert example
create table s1 like src;
with q1 as ( select key, value from src where key = '5')
insert overwrite table s1
select * from q1;
```



