import CoinexAPI
import logging
import math
import time
import json
import pickle
import config
import random

import importlib

from telegram import send_message


_private_api = CoinexAPI.PrivateAPI()


records = {}
records['money_fees'] = 0
records['goods_fees'] = 0
records['balance_cost_time'] = time.time()
records['variance'] = 1
records['predict_cet'] = 0

tmp_data = {}
tmp_data['tprice_cet_money'] = 0
tmp_data['tprice_goods_money'] = 0
tmp_data['prev_api_predict_cet'] = 0.1

def get_self_cet_prediction():
	money_markets = 'CET' + config.money
	data = _private_api.get_ticker(money_markets)
	data = data['data']
	tmp_data['tprice_cet_money'] = float(data['ticker']['buy'])
	
	goods_markets = config.market
	data = _private_api.get_ticker(goods_markets)
	data = data['data']
	tmp_data['tprice_goods_money'] = float(data['ticker']['sell'])

def init_logger():
    logging.VERBOSE = 15
    logging.verbose = lambda x: logging.log(logging.VERBOSE, x)
    logging.addLevelName(logging.VERBOSE, "VERBOSE")

    level = logging.INFO
 
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        level=level)

    fh = logging.FileHandler('./log.txt')
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    fh.setFormatter(formatter)
    logging.getLogger('').addHandler(fh)


def calculate_variance(_private_api):
	data = _private_api.get_latest_transaction(config.market)
	data = data['data']
	_sum = 0
	for x in data:
		_sum = _sum + float(x['price'])

	_avg = _sum / float(len(data))

	_sum = 0

	for x in data:
		_price = float(x['price'])
		_sum = _sum + (_price - _avg)*( _price - _avg)

	_variance = math.sqrt(_sum / float(len(data)))
	_variance = _variance / _avg * 100

	return _variance


def check_order_state(_type,data):
	data = data['data']

	_id = data['id']

	start_time = time.time()

	left_amout = float(data['left'])

	index = 0

	while True:
		if left_amout == 0:
			if _type == 'sell':
				records['money_fees'] = records['money_fees'] + float(data['deal_fee'])
			else:
				records['goods_fees'] = records['goods_fees'] + float(data['deal_fee'])

			total_money = tmp_data['tprice_goods_money'] * records['goods_fees']
			total_money = total_money + records['money_fees']

			records['predict_cet'] = total_money / tmp_data['tprice_cet_money']

			logging.info('mined %0.2f cet; %0.4f m costed; %0.4f g costed' % (records['predict_cet'],records['money_fees'],records['goods_fees']))
			

			pickle.dump(records,open('cache.data','wb'))
			return 'done'
		else:
			time.sleep(0.3)
			try:
				logging.info('get order state: id %d ' % (_id))
				index = index + 1
				data = _private_api.get_order(config.market,_id)
				data = data['data']
				left_amout = float(data['left'])
				logging.info('check order state: id %d left %0.3f' % (_id,left_amout))
			except Exception as e:
				logging.info(str(e))


		elapsed_time = time.time() - start_time
		if elapsed_time > 60*config.wait_order:
			if _type == 'sell':
				records['money_fees'] = records['money_fees'] + float(data['deal_fee'])
			else:
				records['goods_fees'] = records['goods_fees'] + float(data['deal_fee'])
			return 'timeout'

		if index < 3:
			time.sleep(0.1)
		else:
			time.sleep(5)

		


def digging():
	index = 0
	while True:
		data = _private_api.get_ticker(config.market)
		data = data['data']
		sell_price = float(data['ticker']['sell'])
		buy_price = float(data['ticker']['buy'])
		delta = sell_price - buy_price
		if sell_price - buy_price >= 0.000000019:
			logging.info('space is enough')

			amount = records['goods_available'] * config.partial_ratio

			if config.first_submit == 'sell':
				price = buy_price + 0.00000001
				price_s = price * (1 + config.bid_ask_spread/100.0)
				price_b = price
				logging.info('sell %0.3f at %0.8f %s' % (amount,price_s,config.market))
				data_s = _private_api.sell(amount,price_s,config.market)
				logging.info('buy %0.3f at %0.8f %s' % (amount,price_b,config.market))
				data_b = _private_api.buy(amount,price_b,config.market)
			else:
				price = sell_price - 0.00000001
				price_s = price
				price_b = price * (1 - config.bid_ask_spread/100.0)
				logging.info('buy %0.3f at %0.8f %s' % (amount,price_b,config.market))
				data_b = _private_api.buy(amount,price_b,config.market)	
				logging.info('sell %0.3f at %0.8f %s' % (amount,price_s,config.market))
				data_s = _private_api.sell(amount,price_s,config.market)


			stats_b = check_order_state('buy',data_b)
			stats_s = check_order_state('sell',data_s)

			if stats_b == 'timeout' or stats_s == 'timeout':
				logging.info('wait order too much time')
				return 'timeout'

		index = index+1
		if index > config.batch_size:
			return 'maximum'
		time.sleep(0.05)

def need_pause():
	data = ''
	try:
		data = _private_api.get_difficulty()
	except Exception as e:
		logging.error(str(e))
		logging.info('need_pause failed try again 1')
		time.sleep(10)
		try:
			data = _private_api.get_difficulty()
		except Exception as e:
			logging.error(str(e))
			logging.info('need_pause failed try again 2')
			time.sleep(5*60)
			data = _private_api.get_difficulty()
	
	data = data['data']

	difficulty = float(data['difficulty'])
	prediction = float(data['prediction'])


	if prediction == 0 and tmp_data['prev_api_predict_cet'] > 0.1:
		#difficult reset now
		logging.info('difficult have reseted! balance the fee cost now')
		time.sleep(random.random()*10)
		balance_cost()
		records['balance_cost_time'] = time.time()



	tmp_data['prev_api_predict_cet'] = prediction


	if prediction > difficulty * config.stop_threshold:
		logging.info('from api. difficulty %f prediction %0.3f' % (difficulty,prediction))
		return True

	if records['predict_cet'] > difficulty * config.stop_threshold:
		logging.info('from self. difficulty %f prediction %0.3f' % (difficulty,records['predict_cet']))
		return True

	return False

def update_balance():
	data = _private_api.get_balances()
	data = data['data']

	records['goods_available'] = float(data[config.goods]['available'])
	records['cet_available'] = float(data['CET']['available'])
	records['money_available'] = float(data[config.money]['available'])

	logging.info('goods_available: %0.3f' % records['goods_available'])
	logging.info('cet_available: %0.3f' % records['cet_available'])
	logging.info('money_available: %0.3f' % records['money_available'])

def balance_cost():
	if records['money_fees'] < 0.0001 or records['goods_fees'] < 0.0001 :
		logging.info('no need to balance the cost')
		return

	goods_markets = config.market
	logging.info('need buy %s: %0.3f' % (config.goods,records['goods_fees']))
	data = _private_api.get_ticker(goods_markets)
	data = data['data']
	price = float(data['ticker']['sell'])
	amount = records['goods_fees']
	logging.info('buy %0.3f at %f %s' % (amount,price,goods_markets))
	_private_api.buy(amount,price,goods_markets)
	records['goods_fees'] = 0

	_money_cast_buy_goods = amount * price

	money_markets = 'CET' + config.money
	logging.info('need buy %s: %0.3f' % (config.money,records['money_fees']))
	data = _private_api.get_ticker(money_markets)
	data = data['data']
	price = float(data['ticker']['buy'])
	amount = (records['money_fees'] + _money_cast_buy_goods) / price
	logging.info('sell %0.3f at %f %s' % (amount,price,money_markets))
	_private_api.sell(amount,price,money_markets)
	records['money_fees'] = 0
	
	cur_hour = time.strftime("%Y-%m-%d %H", time.localtime())

	item = '%s mined %0.3f CET\r\n' % (cur_hour,records['predict_cet'])
	logging.info(item)

	if config.telegram_notify:
		send_message(item)
		
	with open('records.txt', 'a+') as f:
	    f.write(item)

	records['predict_cet'] = 0


init_logger()

def main():
	global records
	
	welcome = 'CoinexMiner Started!'
	logging.info(welcome)
	if config.telegram_notify:
		send_message(welcome)

	try:
		records = pickle.load(open('cache.data','rb'))
		logging.info(records)
	except Exception as e:
		logging.info('no cache file found.')


	get_self_cet_prediction()

	while True:

		#runtime load config
		importlib.reload(config)

		try:
			update_balance()
		except Exception as e:
			logging.info('update_balance failed try again 1')
			time.sleep(10)
			try:
				update_balance()
			except Exception as e:
				logging.info('update_balance failed try again 2')
				time.sleep(5*60)				
				update_balance()
		
		if random.random() < 0.2:
			try:
				get_self_cet_prediction()
			except Exception as e:
				logging.info('get_self_cet_prediction: ' + str(e))
			

		cur_time = time.time()

		since_balance_cost_time = (cur_time - records['balance_cost_time'])/60

		logging.info('%0.2f minute ago have executed balance fee cost' % since_balance_cost_time)

		if since_balance_cost_time > 60:
			logging.info('balance the fee cost. time beyond 1 hour')
			balance_cost()
			records['balance_cost_time'] = cur_time

		if need_pause():
			logging.info('need_pause mine too much')
			pickle.dump(records,open('cache.data','wb'))
			cur_min = time.gmtime().tm_min
			if cur_min > 10:
				time.sleep(float(60-cur_min)*60)
			else:
				time.sleep(5)
			
			continue

		try:
			records['variance'] = calculate_variance(_private_api)
		except json.decoder.JSONDecodeError as e:
			logging.error('calculate_variance json.decoder.JSONDecodeError')

		

		logging.info('wave ratio: %0.3f%%' % records['variance'])

		if records['variance'] < config.wave_ratio:
			logging.info('no fluctuation')
			
			status = digging()

		pickle.dump(records,open('cache.data','wb'))

		time.sleep(3)


		

if __name__ == "__main__":
	while True:
		try:
			main()
		except Exception as e:
			logging.error(str(e))
			if config.telegram_notify:
				send_message('CoinexMiner: ' + str(e) + ', restarting in 1 min')
			time.sleep(60)

	
