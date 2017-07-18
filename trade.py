#!/usr/bin/env python3

import os
import gdax
import krakenex
from poloniex import Poloniex

import time

GREEN = "[32m"
RED = "[31m"
CLEAR = "[0m"

def format_bids_volume(string):

	color = CLEAR
	number = float(string)
	number = round(number, 3)
	number = format(number, '.3f')

	if (float(number) > 50):
		color = GREEN

	string = str(number)
	padding = ' ' * (10 - len(string))
	new_string = color + padding + string + CLEAR
	return new_string 

def format_asks_volume(string):

	color = CLEAR

	number = float(string)
	number = round(number, 3)
	number = format(number, '.3f')

	if (float(number) > 50):
		color = RED

	string = str(number)
	padding = ' ' * (10 - len(string))
	new_string = color + padding + string + CLEAR
	return new_string 

def format_price(string):

	number = float(string)
	number = round(number, 3)
	number = format(number, '.3f')
	return str(number)

def format_bids_order(price, volume):
	new_string = format_price(price) + ' ' + format_bids_volume(volume)
	return new_string

def format_asks_order(price, volume):
	new_string = format_price(price) + ' ' + format_asks_volume(volume)
	return new_string

def connect_to_gdax():
	gdax_api = gdax.PublicClient()
	return gdax_api

def connect_to_kraken():
	kraken_api = krakenex.API()
	return kraken_api

def connect_to_poloniex():
	poloniex_api = Poloniex()
	return poloniex_api

def consolidate(bids, asks):

	for count in range(0, len(bids)):
		print(bids[count])

	new_bids = []
	last_bid = bids[0]
	#print('last bid: ' + str(last_bid))
	for count in range(1, len(bids)):
		#print(bids[count])

		# if the prices match
		first = round(float(last_bid[0]), 3)
		second = round(float(bids[count][0]), 3)

		#print(str(first) + ' ?= ' + str(second))
		if (first == second):
			print('match found!')
			total = float(last_bid[1]) + float(bids[count][1])
			last_bid[1] = str(total)
		else:
			last_bid = bids[count]
			new_bids.append([last_bid[0], last_bid[1]])

	new_asks = []
	last_ask = asks[0]
	#print('last ask: ' + str(last_ask))
	for count in range(1, len(asks)):
		#print(asks[count])

		# if the prices match
		#print(last_ask[0] + ' ?= ' + asks[count][0])
		if (last_ask[0] == asks[count][0]):
			print('match found!')
			total = float(last_ask[1]) + float(asks[count][1])
			last_ask[1] = str(total)
		else:
			last_ask = asks[count]
			new_asks.append([last_ask[0], last_ask[1]])

	for count in range(0, len(new_bids)):
		print(new_bids[count])

	return [new_bids, new_asks]

def fix_orders(orders_list):
	price_volume_list = []
	price_volume_list_adjusted = []


	# adjust each order in the list
	for count in range(0, len(orders_list)):
		price = orders_list[count][0]
		volume = orders_list[count][1]

		price_volume_list.append([round(float(price), 3), round(float(volume), 3)])
		orders_list[count] = [str(round(float(price), 3)), str(round(float(volume), 3))]



	last_item = price_volume_list[0]
	for count in range(1, len(price_volume_list)):
		# if the current item price matches the last time price
		# sum the two together and record the new volume in the last_item
		if (price_volume_list[count][0] == last_item[0]):
			last_item[1] += price_volume_list[count][1]
		else:
			# add the item to the new list
			price_volume_list_adjusted.append([str(last_item[0]), str(last_item[1])])
			last_item = price_volume_list[count]

	# print(str(price_volume_list_adjusted))

	if len(price_volume_list_adjusted) >= 20:
		return price_volume_list_adjusted
	else:
		return orders_list

def process_kraken_order_book(order_book):
	result = order_book['result']
	xethzusd = result['XETHZUSD']
	bids = xethzusd['bids']
	asks = xethzusd['asks']

	new_asks = []
	new_bids = []

	bids = fix_orders(bids)
	asks = fix_orders(asks)

	# [bids, asks] = consolidate(bids, asks)

	#print('---------------')
	#print(str(asks))
	#print(str(bids))

	#print('asks count : ' + str(len(asks)))
	#print('bids count : ' + str(len(bids)))

	for count in reversed(range(0, len(asks))):
		new_asks.append(format_asks_order(asks[count][0], asks[count][1]))

	for count in range(0, len(bids)):
		new_bids.append(format_bids_order(bids[count][0], bids[count][1]))

	return [new_asks[-20:], new_bids[:20]]

def process_gdax_order_book(order_book):
	bids = order_book['bids']
	asks = order_book['asks']

	new_asks = []
	new_bids = []

	bids = fix_orders(bids)
	asks = fix_orders(asks)

	#print(str(asks))
	#print(str(bids))

	# [bids, asks] = consolidate(bids, asks)
	#print('asks count : ' + str(len(asks)))
	#print('bids count : ' + str(len(bids)))

	for count in reversed(range(0, len(asks))):
		new_asks.append(format_asks_order(asks[count][0], asks[count][1]))

	for count in range(0, len(bids)):
		new_bids.append(format_bids_order(bids[count][0], bids[count][1]))

	return [new_asks[-20:], new_bids[:20]]

def process_poloniex_order_book(order_book):
	bids = order_book['bids']
	asks = order_book['asks']

	new_asks = []
	new_bids = []

	bids = fix_orders(bids)
	asks = fix_orders(asks)

	#print(str(asks))
	#print(str(bids))

	# [bids, asks] = consolidate(bids, asks)
	#print('asks count : ' + str(len(asks)))
	#print('bids count : ' + str(len(bids)))

	for count in reversed(range(0, len(asks))):
		new_asks.append(format_asks_order(asks[count][0], asks[count][1]))

	for count in range(0, len(bids)):
		new_bids.append(format_bids_order(bids[count][0], bids[count][1]))
	return [new_asks[-20:], new_bids[:20]]

def print_books(kraken_book, gdax_book, poloniex_book):
	combined_books = []
	print('KRAKEN             | GDAX               | POLONIEX         ')
	print('===================|====================|===================')
	for count in range(0, 20):
		row = str(kraken_book[0][count]) + ' | ' + str(gdax_book[0][count]) + ' | ' + str(poloniex_book[0][count])
		combined_books.append(row)
		print(row)
	print('-------------------|--------------------|-------------------')
	for count in range(0, 20):
		row = str(kraken_book[1][count]) + ' | ' + str(gdax_book[1][count]) + ' | ' + str(poloniex_book[1][count])
		combined_books.append(row)
		print(row)

gdax_api = connect_to_gdax()
kraken_api = connect_to_kraken()
poloniex_api = connect_to_poloniex()

def main_loop(gdax_api, kraken_api, poloniex_api):

	while(True):
		try:
			kraken_order_book = kraken_api.query_public('Depth', {'pair': 'XETHZUSD', 'count': '50'})
			gdax_order_book = gdax_api.get_product_order_book('ETH-USD', level=2)
			poloniex_order_book = poloniex_api.returnOrderBook('USDT_ETH', 50)

			kraken_book = process_kraken_order_book(kraken_order_book)
			gdax_book = process_gdax_order_book(gdax_order_book)
			poloniex_book = process_poloniex_order_book(poloniex_order_book)

			kraken_price = kraken_api.query_public('Ticker', {'pair': 'XETHZUSD'})
			gdax_price = gdax_api.get_product_ticker(product_id='ETH-USD')['price']
			poloniex_price = poloniex_api.marketTradeHist('USDT_ETH')[0]['rate']

			os.system('clear')
			print_books(kraken_book, gdax_book, poloniex_book)
			print('-------------------|--------------------|-------------------')
			print(str(format(float(kraken_price['result']['XETHZUSD']['c'][0]), '.3f'))  + '            | ' + str(format( float(gdax_price), '.3f')) + '            | ' + str(format(float(poloniex_price), '.3f')))
		except:
			time.sleep(1)

main_loop(gdax_api, kraken_api, poloniex_api)

#kraken_order_book = kraken_api.query_public('Depth', {'pair': 'XETHZUSD', 'count': '50'})
#gdax_order_book = gdax_api.get_product_order_book('ETH-USD', level=2)
#poloniex_order_book = poloniex_api.returnOrderBook('USDT_ETH', 50)

#kraken_book = process_kraken_order_book(kraken_order_book)
#gdax_book = process_gdax_order_book(gdax_order_book)
#poloniex_book = process_poloniex_order_book(poloniex_order_book)

# os.system('clear')
#print_books(kraken_book, gdax_book, poloniex_book)


