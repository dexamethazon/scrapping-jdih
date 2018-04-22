#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
import urllib2
import re
import os.path
import datetime
import mysql.connector

conn = mysql.connector.connect(host='localhost', database='produkhukum', user='xxxxx', password='*****', use_unicode=True, charset='utf8')

success = 0
failed = 0

for x in range(1990, 2019):
	main_page = urllib2.urlopen(url + "&tahun=" + str(x) + "&title=&search=CARI")

	main_soup = BeautifulSoup(main_page)

	links = []
	for link in main_soup.findAll('a', attrs={'href': re.compile("produk_hukum")}):
		
		if link.get('href') not in links:
			links.append(link.get('href'))
			#print '[+] link => ' + link.get('href')

	for l in links:
		detail_page = urllib2.urlopen(l)
		detail_soup = BeautifulSoup(detail_page)

		rows = []
		for row in detail_soup.findAll('tr'):
			rows.append(row)

		cells = rows[1].findChildren('td')
		_type = cells[1].getText().strip()

		cells = rows[2].findChildren('td')
		_number = cells[1].getText().strip()

		cells = rows[3].findChildren('td')
		_year = cells[1].getText().strip()

		cells = rows[4].findChildren('td')
		xdate = cells[1].getText().strip().split('-')
		_date = xdate[2] + '-' + xdate[1] + '-' + xdate[0]

		cells = rows[5].findChildren('td')
		_unit = cells[1].getText().strip()

		cells = rows[6].findChildren('td')
		_title = cells[1].getText().strip()
		_title = re.sub(u'\u201c', '"', _title)
		_title = re.sub(u'\u201d', '"', _title)
		_title = re.sub(u'\u2013', '-', _title)
		_title = re.sub(u'&#8211;', '-', _title)
		_title = re.sub(u'\u2019', '`', _title)

		cells = rows[7].findChildren('td')
		_status = cells[1].getText().strip()

		cells = rows[8].findChildren('td')
		link = cells[1].find('a')
		url = link['href']
		filename = url.rsplit('/', 1)[1]

		req = urllib2.Request(url)

		try:
			response = urllib2.urlopen(req)
		except urllib2.URLError as e:
			print e.reason
			_filename = 'NULL'
		else:
			response_data = response.read()

			file_ = open('files/' + filename, 'w')
			file_.write(response_data)
			file_.close()

			if os.path.exists('files/' + filename):
				#print '[FILES] ' + url + ' downloaded'
				_filename = filename

			else:
				_filename = 'NULL'

		dt = datetime.datetime.now()
		_dt = dt.strftime('%Y-%m-%d %H:%M:%S')

		print('SCRAPPING => THN ' + _year + ' - ' + _title)

		query = "INSERT INTO law_products(type, number, year, date, unit, title, status, file) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
		args = (_type, _number, _year, _date, _unit, _title, _status, _filename)

		cursor = conn.cursor()
		cursor.execute('SET NAMES utf8;')
		cursor.execute('SET CHARACTER SET utf8;')
		cursor.execute('SET character_set_connection=utf8;')
		cursor.execute(query, args)

		if cursor.lastrowid:
			#print('INSERT_SUCCESS')
			success += 1

		else:
			#print('INSERT_FAILED')
			failed += 1

		conn.commit()
		cursor.close()

		print('Success: ' + str(success) + ' ; Failed: ' + str(failed))

conn.close()