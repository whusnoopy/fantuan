# 饭团 (fantuan)

A simple fantuan financial tools based on django

Fantuan is a free software, you can use, modify or distribute it without restriction, visit http://whusnoopy.github.io/fantuan/LICENSE.html for more detail

一个简单的基于 django 的饭团记账系统

饭团是一个自由软件, 您可以免费使用, 修改和再分发, 详见 http://whusnoopy.github.io/fantuan/LICENSE.html


# 环境依赖

## 系统环境

* python2.7 (运行 django 所需环境)
* sqlite3 (本地数据库)

## Python 库

* django (基于 django 1.5 开发, 其他版本没做测试)
* python-flup (用 fastcgi 模式运行 django)


# 安装运行

## 获取代码

git clone 本项目, 进入目录

``` bash
$ git clone https://github.com/whusnoopy/fantuan.git
$ cd fantuan
```

## 建立开发运行环境

``` bash
$ virtualenv ve
$ source ve/bin/activate
$ pip install -r requirements.txt
```

## 生成本地数据库

``` bash
$ python manage.py syncdb
```

> 可修改 `fantuan/settings.py` 里 sqlite 本地数据库的地址

## 启动

``` bash
$ python manager.py runserver 0.0.0.0:8000
```

# fastcgi + nginx 模式运行

## 静态文件汇集

    $ python manager.py collectstatic

## 修改 nginx 的转发规则

下面是一个 nginx conf 文件样例:

``` bash
server {
    listen 80;
    server_name fantuan.yourdomain.com;

    # fastcgi 参数传递 修改为自己的路径
    location / {
      include fastcgi_params;
      fastcgi_split_path_info ^()(.*)$;
      fastcgi_pass unix:/home/yourname/fantuan/fastcgi.sock;
    }

    # 静态文件重定向, 修改为自己的路径
    location /static/admin/ {
      alias /home/yourname/fantuan/static/;
      expires 30d;
    }
}
```

## 运行

``` bash
$ sh start_fantuan.sh
```


# 使用指南

使用 http://yourdomain.com 来访问查看, 通过 http://yourdomain.com/admin 来管理

建议只对 [消费记录] 做添加修改操作, 注意事项在管理界面里有内嵌提示, [餐厅] 和 [人员] 可以在 [消费记录] 里更改

支持转账操作, 自行添加一个 [转账] 的虚拟餐厅, 转账的消费记录里, 付款人选转出者, 参与人选转入者 (其他人都不选), 则可以保持账面平衡
