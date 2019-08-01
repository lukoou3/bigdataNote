
https://blog.51cto.com/14048416/2342535

https://www.cnblogs.com/kimbo/p/6288516.html

未完成....
## * 查看函数的介绍（必读）：
### show functions
show functions ; #查看hive中的所有内置函数

### desc function extended  funcName
desc function extended 函数名; #查看某个函数的详细介绍


```
!connect jdbc:hive2://hadoop01:10000
lifenghcao
xwdxwthf
```

## * hive中常见的内置函数

### * 字符串函数
#### substr(str,pos,len) 与 substring(str,pos,len)
substr(str,pos,len) #截取字符串（下标从1开始） 

```sql
select substr('123456',2);
```

```
+--------+--+
|  _c0   |
+--------+--+
| 23456  |
+--------+--+
```

```sql
select substr('123456',2,3);
```

```
+------+--+
| _c0  |
+------+--+
| 234  |
+------+--+
```
ps：substr和substring用法相同

#### instr(str,substr)
instr(str,substr) #返回子串开始的位置
**注意位置为从1开始的，查不到返回0**

```sql
select instr('123456','23');
```

```
+------+--+
| _c0  |
+------+--+
| 2    |
+------+--+
```

```sql
select instr('123456','9');
```

```
+------+--+
| _c0  |
+------+--+
| 0    |
+------+--+
```
#### split(str,regex)
split(str,regex) #字符串切分，返回一个数组

```sql
select split('1,2,34,56',',');
```

```
+----------------------+--+
|         _c0          |
+----------------------+--+
| ["1","2","34","56"]  |
+----------------------+--+
```

```sql
select split('a1b23c3fg','\\d+');
```

```
+---------------------+--+
|         _c0         |
+---------------------+--+
| ["a","b","c","fg"]  |
+---------------------+--+
```

upper(str) #转大写
lower(str) #转小写
trim(str)  #去除两边空格
length(str) #返回字符串的长度

#### str rlike regexp 
str rlike regexp #Returns true if str matches regexp and false otherwise

```sql
SELECT 'fb' rlike '.*';
```

```
+-------+--+
|  _c0  |
+-------+--+
| true  |
+-------+--+
```

#### concat(str1, str2, ... strN)
concat(str1, str2, ... strN) #字符串拼接

```sql
select concat('1',',','2',',','3');
```

```
+--------+--+
|  _c0   |
+--------+--+
| 1,2,3  |
+--------+--+
```

#### concat_ws(separator, [string | array(string)]+)
concat_ws(separator, [string | array(string)]+) #字符串拼接

```sql
select concat_ws(',','1','2',array('3','4','5'));
```

```
+------------+--+
|    _c0     |
+------------+--+
| 1,2,3,4,5  |
+------------+--+
```
#### nvl(value,default_value)
nvl(value,default_value) # Returns default value if value is null else returns value 

```
select nvl(1,0);
```

```
+------+--+
| _c0  |
+------+--+
| 1    |
+------+--+
```

```sql
select nvl(null,0);
```

```
+------+--+
| _c0  |
+------+--+
| 0    |
+------+--+
```

### * 数值函数
#### round(x[, d])
round(x[, d]) # round x to d decimal places 
round(x[, d]) #四舍五入

```sql
SELECT round(12.3456, 1);
+-------+--+
|  _c0  |
+-------+--+
| 12.3  |
+-------+--+
```

ceil(x) #向上取整
floor(x) #向下取整

### * 集合函数
#### array(n0, n1...)
array(n0, n1...) # Creates an array with the given elements
array(n0, n1...) # 创建数组

```sql
select array(1,2,3,4);
+------------+--+
|    _c0     |
+------------+--+
| [1,2,3,4]  |
+------------+--+
```

#### array_contains(array, value)
array_contains(array, value) # 判断值是否在数组中

```sql
select array_contains(array(1,2,3,4),5);
+--------+--+
|  _c0   |
+--------+--+
| false  |
+--------+--+
```

#### map(key0, value0, key1, value1...)
map(key0, value0, key1, value1...) # 创建map

```sql
select map('zs',1,1,2);
+-----------------+--+
|       _c0       |
+-----------------+--+
| {"zs":1,"1":2}  |
+-----------------+--+
```

map_keys(map) #返回map中所有的key
map_values(map) #返回map中所有的value

### * 日期函数
#### unix_timestamp([date[, format]])
unix_timestamp([date[, format]]) ##返回指定日期的时间戳

```sql
select unix_timestamp();
+-------------+--+
|     _c0     |
+-------------+--+
| 1557478992  |
+-------------+--+
```

```sql
select unix_timestamp('2018-9-1','yyyy-MM-dd'); #返回给定日期的时间戳
+-------------+--+
|     _c0     |
+-------------+--+
| 1535731200  |
+-------------+--+
```

#### from_unixtime(unix_time, format)
from_unixtime(unix_time, format)  #返回相应时间戳的时间

```sql
SELECT from_unixtime(0, 'yyyy-MM-dd HH:mm:ss');
+----------------------+--+
|         _c0          |
+----------------------+--+
| 1970-01-01 08:00:00  |
+----------------------+--+
```

year(data) # #返回给定日期的年
year('2018-5-4') #返回2018 
相应的函数还有：month、day、hour、minute、second

### * 其他的
#### parse_url(url, partToExtract[, key]) 
parse_url(url, partToExtract[, key]) #解析URL字符串,partToExtract的选项包含[HOST,PATH,QUERY,REF,PROTOCOL,FILE,AUTHORITY,USERINFO]

```sql
SELECT parse_url('http://facebook.com/path/p1.php?query=1', 'HOST');
+---------------+--+
|      _c0      |
+---------------+--+
| facebook.com  |
+---------------+--+
```

```sql
SELECT parse_url('http://facebook.com/path/p1.php?query=1', 'QUERY');
+----------+--+
|   _c0    |
+----------+--+
| query=1  |
+----------+--+
```

```sql
SELECT parse_url('http://facebook.com/path/p1.php?query=1', 'QUERY', 'query');
+------+--+
| _c0  |
+------+--+
| 1    |
+------+--+
```


