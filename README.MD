# ReadLogs

![image](https://user-images.githubusercontent.com/24751376/73341682-17447700-42b8-11ea-9735-40b333a85b9a.png)
![](static/logviewer.gif)

主要是想做一个简易的日志实时查看面板，当然不适合大型log。适用面是假如你有自己的一个或者多个小项目，想看看日志实时流，又不想登录机器查看，在此情况下查看此项目的web页面。

前期借鉴[read_logs_in_flask](https://github.com/mitulshah44/read_logs_in_flask)，主要是基于`python`自带文件`seek`操作来实现，同时可以实现`windows`和`linux`适用。但是实测如果监控的日志文件如果有所变动，`flask`就会阻塞住，所以放弃这种实现。直接使用调用命令行`tail`。

## 环境
 - python 3.7.2
 - flask 1.1.1

## 运行
 1. 更改`docker-compose.yml`下`logs`文件的挂载目录，挂载至你要查看的目录(可以将自己项目的日志统一放在一个目录，这样更加方便查看)
 2. 启动
 ```shell
docker-compose build
docker-compose up -d
 ```
 3. 打开`ip:9700`，查看使用(端口配置在`docker-compose.yml`)
 

## TODO
 - 因该不会再更新
 