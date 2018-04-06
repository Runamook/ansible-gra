#!/usr/bin/python

import gzip, csv, sys, socket, datetime, pickle, struct

def get_time(intime):
	# IN : '2017-04-14 23:45:00 MSK'
	date, time = intime.split(' ')[0], intime.split(' ')[1]
	epoch_time = int(datetime.datetime.strptime(date + ' ' + time, "%Y-%m-%d %H:%M:%S").strftime('%s'))
	return epoch_time

def check_if_number(number):
	try:
		float(number)
		return True
	except ValueError:
		return False

def parse_csv(filename, carbon_server, carbon_port):
	with gzip.open(filename, 'rb') as infile:
		reader = csv.reader(infile)
                tuples = ([])

		for line in reader:
			batch = []

			if len(line) == 0:
				# Empty line
				continue

			if line[0] == 'Group':
				# IN: ['Group', 'Diameter Performance']
				group_name = line[1].replace(' ', '_')

			if len(line) < 3:
				# Header lines
				continue

			elif line[0] == 'Timestamp':
				# Measurement header line
				# ['Timestamp', 'Scope Type', 'Scope', 'Server', 'Name/Index', 'TmResponseTimeDownstream', 'TmResponseTimeUpstream', 'RxRequestNoErrors', 'RxAnswerExpectedAll', 'EvPerConnPtrQueuePeak', 'EvPerConnPtrQueueAvg']
				original_header = line

			elif line[3] == 'ALL':
				# KPI value line
				epoch_time = get_time(line[0])
				tuples = parse_kpi(original_header, line, group_name, epoch_time, tuples)

                #if len(tuples) != 0:
                    #print tuples

                message = pickle.dumps(tuples, 1)
                size = struct.pack('!L', len(message))
                write_graphite(message, carbon_server, carbon_port, size)

def parse_kpi(original_header, line, group_name, epoch_time, tuples):
	# ['2017-04-14 23:45:00 MSK', 'NE', 'lab_DSR_HA', 'ALL', 'SY_SERVER_1', '4.105637', '5.229986', '38528', '38485', '18', '3.238418']
	# ['2017-04-15 09:15:00 MSK', 'NE', 'lab_DSR_HA', 'ALL', '465837', '232918', '232918', '232918', '7.321113', '232919']
	messages = {}
	header = original_header[:]
	if check_if_number(line[4]):
		prefix = '%s.Measurement.%s.Simple' % (line[2], group_name)
		for i in range(4):
			header.pop(0)
			line.pop(0)
	else:
		prefix = '%s.Measurement.%s.%s' % (line[2], group_name, line[4])
		prefix = line[2] + '.Measurement.' + line[4]
		for i in range(5):
			header.pop(0)
			line.pop(0)
	for i in range(len(line)):
                # Check every element in line. If there is some meaningful value - create carbon record
		if line[i] != '' and line[i] != 'n/a' and line[i] != '0':
			# LAB_SO_NE.Measurement.FE8_CONN_2.TmFsmOpStateUnavailable n/a 1512768000
			key = prefix + '.' + header[i]
                        value = line[i]
                        tuples.append((key, (epoch_time,value)))
			#messages[key] = line[i]
	#return messages
	return tuples

def write_graphite(message, carbon_server, carbon_port, size):
	sock = socket.socket()
	sock.connect((carbon_server, carbon_port))
	sock.sendall(size)
	sock.sendall(message)
	sock.close()

def main():
	carbon_server = '127.0.0.1'
	carbon_port = 2004
	filename = sys.argv[1]
	parse_csv(filename, carbon_server, carbon_port)

if __name__ == "__main__":
	main()
