# 快速掌握SQL写法
`https://help.aliyun.com/document_detail/51009.html?spm=a2c4g.11186623.6.1014.263d49a0OOhjF1`

本文通过课程实践的方式为您介绍MaxCompute SQL，让您快速掌握SQL的写法以及了解MaxCompute SQL和标准SQL的区别。

## 数据集准备

本文以emp/dept表为示例数据集。单击[emp表数据文件](http://docs-aliyun.cn-hangzhou.oss.aliyun-inc.com/assets/attach/51009/cn_zh/1489374509403/emp%E6%95%B0%E6%8D%AE.txt?spm=a2c4g.11186623.2.10.77fa28ecoGO99Z&amp;file=emp%E6%95%B0%E6%8D%AE.txt "emp表数据文件")、[dept表数据文件](http://docs-aliyun.cn-hangzhou.oss.aliyun-inc.com/assets/attach/51009/cn_zh/1488265664915/dept%E8%A1%A8%E6%95%B0%E6%8D%AE%E6%96%87%E4%BB%B6.txt "dept表数据文件")下载数据文件。您可自行在MaxCompute项目上创建表并上传数据。建表语句如下，数据导入请参见[数据上传下载概述](https://help.aliyun.com/document_detail/51656.html?spm=a2c4g.11186623.2.12.77fa28ecoGO99Z#concept-am2-p3f-vdb "数据上传下载概述")。

直接把数据放上来

emp表:
```
7369,SMITH,CLERK,7902,1980-12-17 00:00:00,800,,20
7499,ALLEN,SALESMAN,7698,1981-02-20 00:00:00,1600,300,30
7521,WARD,SALESMAN,7698,1981-02-22 00:00:00,1250,500,30
7566,JONES,MANAGER,7839,1981-04-02 00:00:00,2975,,20
7654,MARTIN,SALESMAN,7698,1981-09-28 00:00:00,1250,1400,30
7698,BLAKE,MANAGER,7839,1981-05-01 00:00:00,2850,,30
7782,CLARK,MANAGER,7839,1981-06-09 00:00:00,2450,,10
7788,SCOTT,ANALYST,7566,1987-04-19 00:00:00,3000,,20
7839,KING,PRESIDENT,,1981-11-17 00:00:00,5000,,10
7844,TURNER,SALESMAN,7698,1981-09-08 00:00:00,1500,0,30
7876,ADAMS,CLERK,7788,1987-05-23 00:00:00,1100,,20
7900,JAMES,CLERK,7698,1981-12-03 00:00:00,950,,30
7902,FORD,ANALYST,7566,1981-12-03 00:00:00,3000,,20
7934,MILLER,CLERK,7782,1982-01-23 00:00:00,1300,,10
```
dep表:
```
10,ACCOUNTING,NEW YORK
20,RESEARCH,DALLAS
30,SALES,CHICAGO
40,OPERATIONS,BOSTON
```

创建emp表。
```sql
CREATE TABLE IF NOT EXISTS emp (
  EMPNO string ,
  ENAME string ,
  JOB string ,
  MGR bigint ,
  HIREDATE datetime ,
  SAL double ,
  COMM double ,
  DEPTNO bigint );
```

创建dept表。
```sql
CREATE TABLE IF NOT EXISTS dept (
  DEPTNO bigint ,
  DNAME string ,
  LOC string);
```

## 常见问题
初学SQL时，遇到常见问题如下：

* 使用Group by时，Select的部分要么是分组项，要么是聚合函数。    
* Order by后面必须加Limit n。    
* Select表达式中不能用子查询，可以改写为Join。    
* Join不支持笛卡尔积，以及MapJoin的用法和使用场景。    
* Union all需要改成子查询的格式。    
* In/Not in语句对应的子查询只能有一列，而且返回的行数不能超过1000，否则也需要改成Join。  

## SQL示例

### 示例一：列出员工人数大于零的所有部门。
示例一：列出员工人数大于零的所有部门。

**为了避免数据量太大，您需要使用Join进行改写**(常遇问题点 中的第6点)。
```sql
SELECT d.*
FROM dept d
JOIN (
    SELECT DISTINCT deptno AS no
    FROM emp
) e
ON d.deptno = e.no;
```

### 示例二：列出薪金比SMITH多的所有员工。
示例二：列出薪金比SMITH多的所有员工。

**MapJoin的典型场景**(hive似乎只支持等值join)。
```sql
SELECT /*+ MapJoin(a) */ e.empno
    , e.ename
    , e.sal
FROM emp e
JOIN (
    SELECT MAX(sal) AS sal
    FROM `emp`
    WHERE `ENAME` = 'SMITH'
) a
ON e.sal > a.sal;
```

### 示例三：列出所有员工的姓名及其直接上级的姓名。
示例三：列出所有员工的姓名及其直接上级的姓名。

非等值连接(咋就是非等值连接?不明白)。
```sql
SELECT a.ename
    , b.ename
FROM emp a
LEFT OUTER JOIN emp b
ON b.empno = a.mgr;
```

### 示例四：列出基本薪金大于1500的所有工作。
示例四：列出基本薪金大于1500的所有工作。

**Having 的用法**。
```sql
SELECT emp.`JOB`
    , MIN(emp.sal) AS sal
FROM `emp`
GROUP BY emp.`JOB`
HAVING MIN(emp.sal) > 1500;
```

### 示例五：列出在每个部门工作的员工数量、平均工资和平均服务期限。
示例五：列出在每个部门工作的员工数量、平均工资和平均服务期限。

时间处理上有很多好用的内建函数，如下所示。
```sql
SELECT COUNT(empno) AS cnt_emp
    , ROUND(AVG(sal), 2) AS avg_sal
    , ROUND(AVG(datediff(getdate(), hiredate, 'dd')), 2) AS avg_hire
FROM `emp`
GROUP BY `DEPTNO`;
```

### 示例六： 列出每个部门的薪水前3名的人员的姓名以及其排序（Top n的需求非常常见）。
列出每个部门的薪水前3名的人员的姓名以及其排序（Top n的需求非常常见）。

**分组top n**。
```sql

SELECT *
FROM (
  SELECT deptno
    , ename
    , sal
    , ROW_NUMBER() OVER (PARTITION BY deptno ORDER BY sal DESC) AS nums
  FROM emp
) emp1
WHERE emp1.nums < 4;
```

### 示例七： 用一个SQL写出每个部门的人数、CLERK（办事员）的人数占该部门总人数占比。
示例七： 用一个SQL写出每个部门的人数、CLERK（办事员）的人数占该部门总人数占比。

SQL语句如下所示：
```sql
SELECT deptno
    , COUNT(empno) AS cnt
    , ROUND(SUM(CASE 
      WHEN job = 'CLERK' THEN 1
      ELSE 0
    END) / COUNT(empno), 2) AS rate
FROM `EMP`
GROUP BY deptno;
```



```sql

```