fantuan
=======

A simple fantuan financial tools based on django

一个简单的基于 django 的饭团记账系统

环境依赖
========

* python2 (运行 django 所需环境)
* django (基于 django 1.5 开发, 其他版本没做测试)
* sqlite3 (本地数据库)
* python-flup (用 fastcgi 模式运行 django)

安装运行
========

git clone 本项目, 修改 `fantuan/settings.py` 里 sqlite 本地数据库的地址

生成本地数据库

    $ python manage.py syncdb

启动

    $ python manager.py 0.0.0.0:8000

fastcgi + nginx 模式运行
=============================

修改 `start_fantuan.sh` 里 `PROJDIR` 的地址为实际运行地址

修改 nginx 的转发规则

    # 管理员界面的静态文件重定向, 修改为自己的路径
    location /static/admin/ {
      alias /usr/local/lib/python2.7/dist-packages/django/contrib/admin/static/admin/;
      expires 30d;
    }

    # fastcgi 参数传递 修改为自己的路径
    location / { 
      include fastcgi_params;
      fastcgi_split_path_info ^()(.*)$;
      fastcgi_pass unix:/home/yewen/fantuan/fastcgi.sock;
    }

运行

    $ sh start_fantuan.sh

使用指南
========

使用 http://yourdomain.com 来访问查看, 通过 http://yourdomain.com/admin 来管理

建议只对 [消费记录] 做添加修改操作, 注意事项在管理界面里有内嵌提示, [餐厅] 和 [人员] 可以在 [消费记录] 里更改

如果有专职团长, 存在交钱给团长和团长用团费付账的行为, 则添加 [充值] 和 [提现] 两个虚拟的餐厅
