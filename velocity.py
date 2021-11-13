import json
from datetime import datetime



def get_date_time_from_string(time):
	return datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')

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
		output_list.append(result)

	return output_list

def transform(output_list):
	'ensure data is sorted, then check for rules, then map to output'
	res = sorted(output_list, key=lambda x: get_date_time_from_string(x["time"]))

	mem = Memory()
	output = []
	for txn in res:
		accepted = mem.check_accept_and_add_if_accepted(txn["customer_id"], txn)
		output.append({'id': txn['id'], 'customer_id': txn['customer_id'], 'accepted': accepted})

	return output


def write(data):
	with open("./output.txt", 'w') as out:
		for txn in data:
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





if __name__ == "__main__":
	extracted = load()
	transformed = transform(extracted)
	write(transformed)

