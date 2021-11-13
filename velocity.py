

import json
from datetime import datetime



def get_date_time_from_string(time):
	date_time_obj = datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')

	#print('Date:', date_time_obj.date())
	#print('Time:', date_time_obj.time())
	#print('Date-time:', date_time_obj)
	return date_time_obj

def get_amount_from_currency_string(load_amount):
	return "{:.2f}".format(float(load_amount.replace('$', '')))

def load():
	with open('./input.txt', 'r') as json_file:
		json_list = list(json_file)

	output_list = []
	for json_str in json_list:
		result = json.loads(json_str)
		id = result["id"]
		customer_id = result["customer_id"]
		load_amount = result["load_amount"]
		time = get_date_time_from_string(result["time"])
		#print(f"result: {result}")
		#print(f"customer_id: {customer_id} - load_amount: {load_amount} - time: {time} - id: {id}")
		#print(f'Value is: ${load_amount:,.2f}'.replace('$-', '-$'))
		
		##print(f"result: {load_amount}")
		#print(isinstance(result, dict))
		output_list.append(result)

	#res = sorted(output_list, key=lambda x: get_date_time_from_string(x["time"]))
	#print(f"res: {res}")
	return output_list

def transform(output_list):
	'ensure data is sorted, then check for rules, then map to output'
	res = sorted(output_list, key=lambda x: get_date_time_from_string(x["time"]))

	# for InputLoad, return OutputLoad
	# maintain a memory (hashtable data structure, customer_id)
	# check if stack has per customer
	# 	accepted txns for that day, week - and count
	# 	decide if accepted or not
	# -> return OutputLoad


	mem = Memory()
	output = []
	for txn in res:
		accepted = mem.check_accept_and_add_if_accepted(txn["customer_id"], txn)
		output.append({'id': txn['id'], 'customer_id': txn['customer_id'], 'accepted': accepted})



	return output


def write(data):
	with open("./output.txt", 'w') as out:
		#out.write(res)
		#json.dump(data, out)
		for txn in data:
			#out.write(line)
			out.write(str(txn) + '\n')



class Memory:
	'Memory with methods to check velocity limits'
	memory = {}

	def __init__(self):
		print(f"Memory initiated with {self.memory}")

	def check_accept_and_add_if_accepted(self, customer_id, new_txn):
		print(f"Checking customer {customer_id} transaction {new_txn}")
		if customer_id not in self.memory:
			self.memory[customer_id] = []

		if self.can_accept_new_txn(customer_id, new_txn):
			self.add_new_transaction(customer_id, new_txn)
			print(f"Accept customer {customer_id} transaction {new_txn}")
			print(f"Memory updated to {self.memory} ({len(self.memory[customer_id])} customer {customer_id} records)")
			return True
		else:
			print(f"Reject customer {customer_id} transaction {new_txn}")
			return False



	def add_new_transaction(self, customerId, new_txn):
		self.memory[customerId].append(new_txn)

	def can_accept_new_txn(self, customer_id, new_txn):
		if not self.same_day_count_exceeded(customer_id, self.memory, new_txn) \
			and not self.txn_week_amount_exceeded(customer_id, self.memory, new_txn) \
			and not self.txn_day_amount_exceeded(customer_id, self.memory, new_txn):
			return True
		else:
			return False

	def same_day_count_exceeded(self, customer_id, txns, new_txn):
		existing_transactions = 0
		for txn in self.memory[customer_id]:
			if (self.same_day(txn['time'], new_txn['time'])):
				existing_transactions = existing_transactions + 1

		if existing_transactions >= 3:
			print(f"Rejection triggered - same_day_count_exceeded {existing_transactions}")
			return True
		else:
			return False

	def txn_day_amount_exceeded(self, customer_id, txns, new_txn):
		existing_transaction_amount = 0
		new_txn_amount = float(get_amount_from_currency_string(new_txn['load_amount']))

		for txn in self.memory[customer_id]:
			if self.same_day(txn['time'], new_txn['time']):
				existing_transaction_amount += float(get_amount_from_currency_string(txn['load_amount']))

		new_total = existing_transaction_amount + new_txn_amount
		if new_total >= 5000:
			print(f"Rejection triggered - txn_day_amount_exceeded (total: {new_total})")
			return True
		else:
			return False

	def txn_week_amount_exceeded(self, customer_id, txns, new_txn):
		existing_transaction_amount = 0
		new_txn_amount = float(get_amount_from_currency_string(new_txn['load_amount']))

		for txn in self.memory[customer_id]:
			if self.same_week(txn['time'], new_txn['time']):
				#print(isinstance(float(get_amount_from_currency_string(txn['load_amount'])), float))
				#print(isinstance(get_amount_from_currency_string(txn['load_amount']), str))
				existing_transaction_amount += float(get_amount_from_currency_string(txn['load_amount']))

		new_total = existing_transaction_amount + new_txn_amount
		if new_total >= 20000:
			print(f"Rejection triggered - txn_week_amount_exceeded (total: {new_total})")
			return True
		else:
			return False

	def same_week(self, day_string, day_new_string):
		ds = get_date_time_from_string(day_string)
		dns = get_date_time_from_string(day_new_string)
		return ds.isocalendar()[1] == dns.isocalendar()[1] and ds.year == dns.year

	def same_day(self, day_string, day_new_string):
		ds = get_date_time_from_string(day_string)
		dns = get_date_time_from_string(day_new_string)
		return ds.isocalendar()[2] == dns.isocalendar()[2] and ds.isocalendar()[1] == dns.isocalendar()[1] and ds.year == dns.year


class InputLoad:
	'Common base class for input loads'
	id = 0
	customer_id = 0
	load_amount = 0
	time = datetime.utcnow()

	def __init__(self, id, customer_id, load_amount, time):
	  self.id = id
	  self.customer_id = customer_id
	  self.load_amount = load_amount
	  self.time = time

	def display(self):
	  print ("Customer id : ", self.customer_id,  ", Load amount: ", self.load_amount)


class OutputLoad:
	'Common base class for output loads'
	id = 0
	customer_id = 0
	accepted = False

	def __init__(self, id, customer_id, accepted):
	  self.id = id
	  self.customer_id = customer_id
	  self.accepted = accepted

	def display(self):
	  print ("Customer id : ", self.customer_id,  ", Accepted: ", self.accepted)





def testing():

	dict = {}

	print(f"start: {dict}")
	#del dict['Name'];

	if "528" not in dict:
		dict['528'] = []

	intxn1 = {"id":"19366","customer_id":"443","load_amount":"$181.35","time":"2000-01-13T12:41:48Z"}
	intxn2 = {"id":"19363","customer_id":"443","load_amount":"$117.35","time":"2000-01-13T12:42:48Z"}
	intxn3 = {"id":"19361","customer_id":"443","load_amount":"$421.35","time":"2000-01-13T12:43:48Z"}
	intxn4 = {"id":"19369","customer_id":"443","load_amount":"$181.35","time":"2000-01-13T12:47:48Z"}

	txn1 = {"id":"15887","customer_id":"528","accepted":True}
	txn2 = {"id":"30081","customer_id":"528","accepted":True}
	txn3 = {"id":"26540","customer_id":"528","accepted":False}

	dict['528'].append(txn1)
	dict['528'].append(txn2)
	dict['528'].append(txn3)

	for txn in dict['528']:
		print(f"txn: {txn}")

	print(f"end: {dict}")

	amount = intxn1["load_amount"]
	print(f"amount: {amount}")

	number_commas_only = get_amount_from_currency_string(amount)
	print(number_commas_only)

	print("Memory tests:")

	mem = Memory()
	mem.check_accept_and_add_if_accepted(intxn1["customer_id"], intxn1)
	mem.check_accept_and_add_if_accepted(intxn2["customer_id"], intxn2)
	mem.check_accept_and_add_if_accepted(intxn3["customer_id"], intxn3)
	mem.check_accept_and_add_if_accepted(intxn3["customer_id"], intxn4)


# dict structure
#	customer_id 
# 		id
#		accepted




extracted = load()
transformed = transform(extracted)
write(transformed)

