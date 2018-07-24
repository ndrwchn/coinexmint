# CoinexMiner

# 使用须知
1. 本项目没有经过严格测试 仅测试过以下交易对
	* 感谢flufy3d 测试CDYBCH交易对
	* 感谢shawncd 测试BTCUSDT交易对
	* 感谢Max     测试ETHUSDT交易对
	* 感谢imcoddy 测试ETHBCH交易对
	* 感谢mmbbss888 测试BTMBCH交易对
2. 交易挖矿有风险
3. 请先小额测试
4. 刚开始使用前 请观察程序执行情况 确定安全 再让它自己跑
5. 平挖赚的是返佣给大号的20% 不是自己小号的就别挖了啊 会亏钱的
6. 本项目由python实现 支持linux macos windows


# 交易策略

1. 查询 余额 cdy bch  难度 cet/h cet价格
2. 检测最近成交 浮动不超过 设定值
3. 检查盘口 如果有空间(买一卖一超过最小 价格单位) 取部分 cdy持有量 
4. 同时 下单买卖 bid_ask_spread 是0 就是 自己和自己成交 如果是 0.1就是 买卖 差千分之1 挂单
5. 检查 两个 order成交情况

	都成交了 继续刷
	只有一个成交 等待 十分钟 还是没成交 跳到1

6. 统计交易量 手续费消耗 每小时 平衡一次消耗的 cdy 和 bch

7. 检测难度 如果已挖到的cet达到 难度的95% 则等待下个小时



# 参数说明

coinex_api_id="xxxx"

机器人密钥id(不要泄漏给他其他人)


coinex_api_key="xxx"

机器人密钥key(不要泄漏给他其他人)


partial_ratio = 0.1

每单的仓位比例 0.1 就是 10%的仓位比例 减少该值 可以减少被套的资金量 但是挖矿速度也会下降


bid_ask_spread = 0 

买单卖单差价 百分比 0就是 原价 自己买自己卖 0.1 就是相差千分之1


wave_ratio = 1

最近成交波动方差 1就是 最近成交价格浮动 小于1% 减小该值可以减少被套风险 但是挖矿速度会下降


wait_order = 10

未成交订单等待时间 单位分钟 默认等待10分钟


stop_threshold = 0.9

挖矿停止阈值 因为读取的coinex难度api 已挖cet有一定延迟 可以调小这个值来抵御 默认0.9 已挖cet达到难度的90%就停止


first_submit = "sell"

优先提交卖单还是买单  sell就是 先提交卖 buy就是先提交买

买先盯住卖一价 上升区间适合执行买先策略

卖先盯住买一价 下降区间适合执行卖先策略

横盘的时候 随意选择一个

target_price = "b1"

目标价格 b1就是锚定买一价格 s1就是锚定卖一价格

batch_size = 10

一个批次内挖矿次数 默认是10次 如果你没单的金额特别大 可以减小该数值 最小值1

ignore_amount = 0

有些时候会遇到盘口 小额挂单干扰挖矿 就可以开启这个参数 默认0 不开启

比如在CDYBCH交易对中 设置这个值为10 意味着 只要盘口买一卖一的数量小于10个 就会忽略该小额单继续挖矿

telegram_notify : false

telegram通知 默认不启用 不用的话 telegram开头的参数都可以不用管

如果想使用 请参考[教程](https://www.forsomedefinition.com/automation/creating-telegram-bot-notifications/)

telegram_chatid : "12345"

telegram_token : "12345:AAFu7Pyx6WGBrfbypr9idvnjdKfAXu9xxxx"

telegram_rmsc : 3


market = "CDYBCH"

挖矿交易对 全大写 也可以是 "BTCUSDT" 等等


goods = "CDY"

交易对商品 也可以是 "BTC" 等等 请注意和market对应


money = "BCH"

交易对计价币种 也可以是 "USDT" 等等 请注意和market对应



# 快速开始

1. 申请coinex API
	
	[如何申请CoinEx API](https://github.com/flufy3d/CoinexMiner/wiki/%E5%A6%82%E4%BD%95%E7%94%B3%E8%AF%B7-CoinEx-API)

2. 安装运行环境

	a. 安装python3(安装的时候 选择添加到系统path)
		https://www.python.org/downloads/

	b. 安装requests模块
		pip install requests

3. 调整 config-example.json 里面的配置参数 (注意 输入的字符全是英文 不要有中文标点符号)

4. 将 config-example.json 改名 config.json

5. 
	打开控制台 输入 python main.py 回车
	windows 平台也可以直接双击 main.py 运行

6. crtl-c 停止运行

7. python balance_cost.py 手动平衡消耗的手续费(程序主动退出或者异常退出后使用)


# 问题反馈
1. 通过github的 issues 提交
2. 通过wechat联系我 wechat_id: kenshin1987
3. 通过telegram http://t.me/bitcoin_faith

# FAQ
1. api-ms-win-crt-runtime-|1-1-0.dll 丢失

	安装
		https://www.microsoft.com/zh-cn/download/details.aspx?id=48145

	或者参考
		https://blog.csdn.net/fuchaosz/article/details/78996544

2. ModuleNotFoundError: No module named 'requests'

	手动安装requests模块
		pip install requests

3. apikey都配置好了 get_balance 还是失败

	请确保系统时间 已经与互联网时间同步 因为下单要填写时间戳
	如果和服务器的utc时间相差 1分钟 服务器会拒绝提供服务

4. 开始运行程序后 执行sell闪退

	请确保账户上面 有一定资金 如果下单量小于系统最小限额 下单会失败

5. 安装python3.7 提示需要升级windows sp1补丁

	请安装老版本的python3  [Python 3.4.3](https://www.python.org/downloads/release/python-343/)

6. 实在不会装python怎么办

	装python有困难的同学可以直接用我打包的exe版本[CoinexMiner](https://github.com/flufy3d/CoinexMiner/releases)
		
7. 运行一段时间以后 显示 IP not allowed 无法连接到服务器
 
	如果你用的是家庭宽带 不定期ip地址会变更	 导致Coinex绑定的ip地址失效 解决方法是 重新绑定ip地址 或者租用一个长期的vps



# 免责声明
 本项目是公益性质 不搞收费版 不搞会员制 纯属coinex爱好者 互相帮助
 由本程序带来的收益或者亏损都和项目作者没有关系

# 打赏


如果你觉得我写的程序对你有用或是有一定帮助，请我喝杯咖啡吧！ 

* bch: 1QCBhad9pegNenYGbtYYC9mkwZpEUMB3tP

* cet: 0x8d740c9779674b13a7038a5d56b04470b7a1b096 (Coinex 站内转账 flufy3d@gmail.com)










