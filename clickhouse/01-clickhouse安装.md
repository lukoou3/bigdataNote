# clickhouse安装

## 准备：修改配置

```
sudo vi /etc/security/limits.conf
```
在文件末尾添加：
```
* soft nofile 65536

* hard nofile 65536

* soft nproc 131072

* hard nproc 131072
```


```
sudo vi /etc/security/limits.d/90-nproc.conf
```
在文件末尾添加：
```
* soft nofile 65536

* hard nofile 65536

* soft nproc 131072

* hard nproc 131072
```


修改/etc/selinux/config中的SELINUX=disabled后重启
```
(base) [hadoop@hadoop101 ~]$ cat /etc/selinux/config

# This file controls the state of SELinux on the system.
# SELINUX= can take one of these three values:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
SELINUX=disabled
# SELINUXTYPE= can take one of these two values:
#     targeted - Targeted processes are protected,
#     mls - Multi Level Security protection.
SELINUXTYPE=targeted

```

安装依赖:
```
sudo yum install -y libtool
```

yum报错修改：YumRepo Error: All mirror URLs are not using ftp, http[s] or file.
修改yum源站点配置：vi /etc/yum.repos.d/CentOS-Base.repo
对照清华大学镜像站中的目录修改后如下：
```
[base]
name=CentOS-$releasever - Base
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=os&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/os/$basearch/
baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/os/x86_64/
gpgcheck=1
#gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/os/x86_64/RPM-GPG-KEY-CentOS-6

#released updates
[updates]
name=CentOS-$releasever - Updates
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=updates&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/updates/$basearch/
baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/updates/x86_64/
gpgcheck=1
#gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/os/x86_64/RPM-GPG-KEY-CentOS-6

#additional packages that may be useful
[extras]
name=CentOS-$releasever - Extras
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=extras&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/extras/$basearch/
baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/extras/x86_64/
gpgcheck=1
#gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/os/x86_64/RPM-GPG-KEY-CentOS-6

#additional packages that extend functionality of existing packages
[centosplus]
name=CentOS-$releasever - Plus
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=centosplus&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/centosplus/$basearch/
baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/centosplus/x86_64/
gpgcheck=1
enabled=0
#gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/os/x86_64/RPM-GPG-KEY-CentOS-6

#contrib - packages by Centos Users
[contrib]
name=CentOS-$releasever - Contrib
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=contrib&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/contrib/$basearch/
baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/contrib/x86_64/
gpgcheck=1
enabled=0
#gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-6
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/centos-vault/6.8/os/x86_64/RPM-GPG-KEY-CentOS-6

```

## 安装软件

```
(base) [hadoop@hadoop101 software]$ ll
total 1262280
-rw-rw-r-- 1 hadoop hadoop      56708 Apr 11 19:11 clickhouse-client-20.4.5.36-2.noarch.rpm
-rw-rw-r-- 1 hadoop hadoop  117222435 Apr 11 19:11 clickhouse-common-static-20.4.5.36-2.x86_64.rpm
-rw-rw-r-- 1 hadoop hadoop 1175204526 Apr 11 19:12 clickhouse-common-static-dbg-20.4.5.36-2.x86_64.rpm
-rw-rw-r-- 1 hadoop hadoop      78318 Apr 11 19:12 clickhouse-server-20.4.5.36-2.noarch.rpm
(base) [hadoop@hadoop101 software]$ sudo rpm -ivh *.rpm
warning: clickhouse-client-20.4.5.36-2.noarch.rpm: Header V4 RSA/SHA1 Signature, key ID e0c56bd4: NOKEY
Preparing...                ########################################### [100%]
   1:clickhouse-common-stati########################################### [ 25%]
   2:clickhouse-client      ########################################### [ 50%]
   3:clickhouse-server      ########################################### [ 75%]

Path to data directory in /etc/clickhouse-server/config.xml: /var/lib/clickhouse/
   4:clickhouse-common-stati########################################### [100%]
(base) [hadoop@hadoop101 software]$

```

## 修改配置文件

### 远程连接
修改/etc/clickhouse-server/config.xml

去掉<listen_host>::</listen_host>注释，这样的话才能让 ClickHouse 被除本机以外的服务器访问
```
<!-- Listen specified host. use :: (wildcard IPv6 address), if you want to accept connections both with IPv4 and IPv6 from everywhere. -->
<listen_host>::</listen_host>
<!-- Same for hosts with disabled ipv6: -->
<!-- <listen_host>0.0.0.0</listen_host> -->
```

在这个文件中，有 ClickHouse 的一些默认路径配置，比较重要的
```
数据文件路径： <path>/var/lib/clickhouse/</path>
日志文件路径： <log>/var/log/clickhouse-server/clickhouse-server.log</log>
```


## 启动服务端
sudo service clickhouse-server start

```
(base) [hadoop@hadoop101 software]$ service clickhouse-server status
clickhouse-server service is stopped
(base) [hadoop@hadoop101 software]$ sudo service clickhouse-server start
[sudo] password for hadoop:
Start clickhouse-server service: Path to data directory in /etc/clickhouse-server/config.xml: /var/lib/clickhouse/
DONE
(base) [hadoop@hadoop101 software]$
 
```

## 启动交互式客户端
```
clickhouse-client  -m
```



```

```