## Hive中抽取连续多天登录用户
摘抄自：https://www.cnblogs.com/juefan/p/3928966.html

昨天群上有人发个某单位面试题，题目描述大概如下：

数据源：用户登录表，只有俩个字段，uid和dt

试用HQL抽取出连续登录了K天的用户uid

第一个想法就是直接用一个UDF解决，按uid分组，把dt收集起来然后在UDF里面判断是否满足条件
```sql
SELECT
    uid,
    isExist(collect_set(dt), k) flag
FROM
    table_name
GROUP BY
    uid
HAVING
    flag = 1;
```
其中isExist的逻辑是判断collect_set中是否存在k个连续的值

这种方法简单明了，但是需要额外的写一个UDF，对于不懂JAVA的来说确实比较麻烦

 

今天群里有个神人给出了一种新的解决思路，十分完美的解决了，下面是具体代码
```sql
SELECT 
    uid, MAX(dt) - MIN(dt) diff, COLLECT_set (dt) 
FROM
    (SELECT 
        a.uid, a.dt, dt - rn num 
    FROM
        (SELECT 
            uid, dt, row_number () over (PARTITION BY uid 
        ORDER BY dt) rn 
        FROM
            table_name
        GROUP BY uid, dt) a) a 
GROUP BY uid, num
```
该思路首先利用窗口函数以uid分组然后按照dt排序给出每个dt在排序中的位置，然后用求出dt与位置的差（记为num)

最后按照uid和num做一个聚合，容易发现同一个num组内的dt是连续的值

然后直接计数(count(*))就可以得出结果了

上面的代码只是为了更加方便看到输出的结果正确性，输出结果如下：
```
UID        DIFF    DT_ARRAY
1043736    3.0    ｛20140815    20140814    20140813    20140812｝
1043736    0.0    ｛20140818｝
1043736    1.0    ｛20140821    20140820｝
1043844    0.0    ｛20140814｝
1044090    1.0    ｛20140812    20140811｝
1044090    2.0    ｛20140816    20140815    20140817｝
1044090    0.0    ｛20140821｝
1044264    0.0    ｛20140810｝
1044264    3.0    ｛20140815    20140814    20140813    20140812｝
1044264    5.0    ｛20140821    20140820    20140822    20140819    20140817    20140818｝
```
结果中uid = 1043736 的一共登录了7天，其中可以拆分成三个连续的登录模块，分别是连续登录1天、2天和4天

