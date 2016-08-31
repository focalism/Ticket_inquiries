# Ticket_inquiries
python3 终端命令行查询机票

#示例：

python xc_flight_price.py -C西宁 -D南京 -T2016-9-2 -Ftrans -Pprice -L5

-C出发城市

-D到达城市

-T出发时间

-F航班种类，dirc:直达航班，trans：中加需要中转的航班，inner:需要换乘其他交通工具的航班

-P最近三个月的最低价列表，price:按价格排序，day：按时间排序

-L需要打印多少天航班的最低价格

