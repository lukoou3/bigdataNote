hive partition 不能写函数
https://www.cnblogs.com/amydi/p/10936204.html

https://www.cnblogs.com/drjava/p/10521401.html

https://blog.csdn.net/qq_26442553/article/details/80382174

https://cloud.tencent.com/developer/article/1358116

## hive partition 中不能写函数
想完成类似这样一个需求：insert overwrite table ... partiton(dt=date_sub('2019-03-13',2))

 

当然这样子是行不通的，partition后面那个括号里是不能用函数的，怎么办呢？

网上一顿狂搜，找到了一个解决办法！动态分区

上两个链接就懂啦：
https://stackoverflow.com/questions/44886583/parameter-passing-to-partition-is-not-working-in-hive

https://blog.csdn.net/qq_26442553/article/details/80382174

总之就是可以执行了，方法如下：
```sql
set hive.exec.dynamic.partition=true;  
set hive.exec.dynamic.partition.mode=nonstrict; 

insert into table ts.dyy_test partition(dt)
select a,b,date_sub('2019-03-23',2) dt from asdf.sldfjk
where dt='2019-03-15';
```

我的例子：
```sql
insert overwrite table dws_uv_detail_wk partition( wk_dt=concat(date_add(next_day('2019-02-10','MON'), -7), '_', date_add(next_day('2019-02-10','MON'), -1)) )
select
    mid_id,
    concat_ws('|',collect_set(user_id)) as user_id,
    concat_ws('|',collect_set(version_code)) as version_code,
    concat_ws('|',collect_set(version_name)) as version_name,
    concat_ws('|',collect_set(lang)) as lang,
    concat_ws('|',collect_set(source)) as source,
    concat_ws('|',collect_set(os)) as os,
    concat_ws('|',collect_set(area)) as area,
    concat_ws('|',collect_set(model)) as model,
    concat_ws('|',collect_set(brand)) as brand,
    concat_ws('|',collect_set(sdk_version)) as sdk_version,
    concat_ws('|',collect_set(gmail)) as gmail,
    concat_ws('|',collect_set(height_width)) as height_width,
    concat_ws('|',collect_set(app_time)) as app_time,
    concat_ws('|',collect_set(network)) as network,
    concat_ws('|',collect_set(lng)) as lng,
    concat_ws('|',collect_set(lat)) as lat,
    date_add(next_day('2019-02-10','MON'), -7) as monday_date,
    date_add(next_day('2019-02-10','MON'), -1) as sunday_date
from dws_uv_detail_day
where dt>=date_add(next_day('2019-02-10','MON'), -7) and dt<=date_add(next_day('2019-02-10','MON'), -1)
group by mid_id;

partition后面那个括号里是不能用函数的，怎么办呢？：partition( wk_dt=concat(date_add(next_day('2019-02-10','MON'), -7), '_', date_add(next_day('2019-02-10','MON'), -1)) )
动态分区：
set hive.exec.dynamic.partition=true;
set hive.exec.dynamic.partition.mode=nonstrict;

insert overwrite table dws_uv_detail_wk partition(wk_dt)
select
    mid_id,
    concat_ws('|',collect_set(user_id)) as user_id,
    concat_ws('|',collect_set(version_code)) as version_code,
    concat_ws('|',collect_set(version_name)) as version_name,
    concat_ws('|',collect_set(lang)) as lang,
    concat_ws('|',collect_set(source)) as source,
    concat_ws('|',collect_set(os)) as os,
    concat_ws('|',collect_set(area)) as area,
    concat_ws('|',collect_set(model)) as model,
    concat_ws('|',collect_set(brand)) as brand,
    concat_ws('|',collect_set(sdk_version)) as sdk_version,
    concat_ws('|',collect_set(gmail)) as gmail,
    concat_ws('|',collect_set(height_width)) as height_width,
    concat_ws('|',collect_set(app_time)) as app_time,
    concat_ws('|',collect_set(network)) as network,
    concat_ws('|',collect_set(lng)) as lng,
    concat_ws('|',collect_set(lat)) as lat,
    date_add(next_day('2019-02-10','MON'), -7) as monday_date,
    date_add(next_day('2019-02-10','MON'), -1) as sunday_date,
    concat(date_add(next_day('2019-02-10','MON'), -7), '_', date_add(next_day('2019-02-10','MON'), -1)) wk_dt
from dws_uv_detail_day
where dt>=date_add(next_day('2019-02-10','MON'), -7) and dt<=date_add(next_day('2019-02-10','MON'), -1)
group by mid_id;
```

