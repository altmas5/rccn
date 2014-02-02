############################################################################
#
# Copyright (C) 2013 tele <tele@rhizomatica.org>
#
# REST API Interface to RCCN Modules
# This file is part of RCCN
#
# RCCN is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RCCN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################

from corepost import Response, NotFoundException, AlreadyExistsException
from corepost.web import RESTResource, route, Http 
from daemonizer import Daemonizer
from config import *

class SubscriberRESTService:
	path = '/subscriber'

	# get all subscribers
	@route('/')
	def getAll(self,request):
		api_log.info('%s - [GET] %s' % (request.getHost().host,self.path))
		try:
			sub = Subscriber()
			data = json.dumps(sub.get_all(), cls=PGEncoder)
		except SubscriberException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data
   
	# get subscriber
	@route('/<msisdn>')
	def get(self, request, msisdn):
		api_log.info('%s - [GET] %s/%s' % (request.getHost().host, self.path ,msisdn))
		try:
			sub = Subscriber()
			if msisdn == 'all_connected':
				data = json.dumps(sub.get_all_connected(), cls=PGEncoder)
			else:
				data = json.dumps(sub.get(msisdn), cls=PGEncoder)
		except SubscriberException as e:
			print e
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data
 
	# add new subscriber
	@route('/',Http.POST)
	def post(self,request,msisdn,name,balance):
		api_log.info('%s - [POST] %s Data: msisdn:"%s" name:"%s" balance:"%s"' % (request.getHost().host,self.path,msisdn,name,balance))
		try:
			sub = Subscriber()
			sub.add(msisdn,name,balance)
			data = {'status': 'success', 'error': ''}
		except SubscriberException as e:
			print e
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

	# edit subscriber
	@route('/<msisdn>', Http.PUT)
	def put(self,request,msisdn='',name='',balance='',authorized='',subscription_status=''):
		api_log.info('%s - [PUT] %s/%s Data: name:"%s" balance:"%s" authorized:"%s" subscription_status:"%s"' % (request.getHost().host,self.path,msisdn,name,balance,authorized,subscription_status))
		try:
			sub = Subscriber()
			if  authorized != '':
				sub.authorized(msisdn,authorized)
			if subscription_status != '':
				sub.subscription(msisdn,subscription_status)
			if msisdn != '' and name != '' or balance != '':
				sub.edit(msisdn,name,balance)
			data = {'status': 'success', 'error': ''}
		except SubscriberException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

	# delete subscriber
	@route('/<msisdn>', Http.DELETE)
	def delete(self,request,msisdn):
		api_log.info('%s - [DELETE] %s/%s' % (request.getHost().host,self.path,msisdn))
		try:
			sub = Subscriber()
			sub.delete(msisdn)
			data = {'status': 'success', 'error': ''}
		except SubscriberException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data
		

class CreditRESTService:
	path = '/credit'

	@route('/', Http.POST)
	def post(self, request, msisdn, receipt_id, amount):
		api_log.info('%s - [POST] %s Data: receipt_id:"%s" msisdn:"%s" amount:"%s"' % (request.getHost().host,self.path,receipt_id,msisdn,amount))
                try:
                	credit = Credit()
                        credit.add(receipt_id,msisdn,amount)
                        data = {'status': 'success', 'error': ''}
                except CreditException as e:
                        print e
                        data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
                return data

class SMSRESTService:
        path = '/sms'

        @route('/', Http.POST)
        def receive(self, request, source, destination, text):
                api_log.info('%s - [POST] %s Data: source:"%s" destination:"%s" text:"%s"' % (request.getHost().host,self.path,source,destination,text))
                try:
                        sms = SMS()
                        sms.receive(source,destination,text)
                        data = {'status': 'success', 'error': ''}
                except SMSException as e:
                        data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
                return data

        @route('/send', Http.POST)
        def send(self, request, source, destination, text):
                api_log.info('%s - [POST] %s/send Data: source:"%s" destination:"%s" text:"%s"' % (request.getHost().host,self.path,source,destination,text))
                try:
                        sms = SMS()
                        sms.send(source,destination,text)
                        data = {'status': 'success', 'error': ''}
                except SMSException as e:
                        data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
                return data


class StatisticsRESTService:
	path = '/statistics'

	# Calls statistics
	@route('/calls/total_calls')
	def total_calls(self, request):
		api_log.info('%s - [GET] %s/calls/total_calls' % (request.getHost().host,self.path))
		try:
			stats = CallsStatistics()
			data = stats.get_total_calls()
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data


	@route('/calls/total_minutes')
	def total_minutes(self, request):
		api_log.info('%s - [GET] %s/calls/total_minutes' % (request.getHost().host,self.path))
		try:
			stats = CallsStatistics()
			data = stats.get_total_minutes()
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

	@route('/calls/average_call_duration')
	def average_call_duration(self, request):
		api_log.info('%s - [GET] %s/calls/average_call_duration' % (request.getHost().host,self.path))
		try:
			stats = CallsStatistics()
			data = json.dumps(stats.get_average_call_duration(), cls=PGEncoder)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data


	@route('/calls/total_calls_by_context',Http.POST)
	def total_calls_by_context(self, request, context):
		api_log.info('%s - [POST] %s/calls/total_calls_by_context Data: context:"%s"' % (request.getHost().host,self.path,context))
		try:
			stats = CallsStatistics()
			data = stats.get_total_calls_by_context(context)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data


	@route('/calls/calls',Http.POST)
	def calls(self, request, period):
		api_log.info('%s - [POST] %s/calls/calls Data: period:"%s"' % (request.getHost().host,self.path,period))
		try:
			stats = CallsStatistics()
			data = json.dumps(stats.get_calls_stats(period), cls=PGEncoder)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

	
	@route('/calls/calls_minutes',Http.POST)
	def calls_minutes(self, request, period):
		api_log.info('%s - [POST] %s/calls/calls_minutes Data: period:"%s"' % (request.getHost().host,self.path,period))
		try:
			stats = CallsStatistics()
			data = json.dumps(stats.get_calls_minutes_stats(period), cls=PGEncoder)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

	
	@route('/calls/calls_context',Http.POST)
	def calls_context(self, request, period):
		api_log.info('%s - [POST] %s/calls/calls_context Data: period:"%s"' % (request.getHost().host,self.path,period))
		try:
			stats = CallsStatistics()
			data = json.dumps(stats.get_calls_context_stats(period), cls=PGEncoder)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data


	# Costs/Credits statistics
	@route('/costs/total_spent')
	def total_spent(self, request):
		api_log.info('%s - [GET] %s/costs/total_spent' % (request.getHost().host,self.path))
		try:
			stats = CostsStatistics()
			data = json.dumps(stats.get_total_spent(), cls=PGEncoder)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

	
	@route('/costs/average_call_cost')
	def average_call_cost(self, request):
		api_log.info('%s - [GET] %s/costs/average_call_cost' % (request.getHost().host,self.path))
		try:
			stats = CostsStatistics()
			data = json.dumps(stats.get_average_call_cost(), cls=PGEncoder)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

	@route('/costs/total_spent_credits')
	def total_spent_credits(self, request):
		api_log.info('%s - [GET] %s/costs/total_spent_credits' % (request.getHost().host,self.path))
		try:
			stats = CostsStatistics()
			data = json.dumps(stats.get_total_spent_credits(), cls=PGEncoder)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

	@route('/costs/top_destinations')
	def top_destinations(self, request):
		api_log.info('%s - [GET] %s/top_destinations' % (request.getHost().host,self.path))
		try:
			stats = CostsStatistics()
			data = json.dumps(stats.get_top_destinations(), cls=PGEncoder)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

	
	@route('/costs/costs_stats',Http.POST)
	def costs_stats(self, request, period):
		api_log.info('%s - [POST] %s/costs/costs_stats Data: period:"%s"' % (request.getHost().host,self.path,period))
		try:
			stats = CostsStatistics()
			data = json.dumps(stats.get_costs_stats(period), cls=PGEncoder)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

	@route('/costs/credits_stats',Http.POST)
	def credits_stats(self, request, period):
		api_log.info('%s - [POST] %s/costs/credits_stats Data: period:"%s"' % (request.getHost().host,self.path,period))
		try:
			stats = CostsStatistics()
			data = json.dumps(stats.get_credits_stats(period), cls=PGEncoder)
		except StatisticException as e:
			data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
		return data

class ConfigurationRESTService:
        path = '/configuration'

        @route('/site', Http.GET)
        def site(self, request):
                api_log.info('%s - [GET] %s/site' % (request.getHost().host,self.path))
                try:
                        config = Configuration()
                        data = json.dumps(config.get_site(), cls=PGEncoder)
                except ConfigurationException as e:
                        data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
                return data

        @route('/config', Http.GET)
        def config(self, request):
                api_log.info('%s - [GET] %s/config' % (request.getHost().host,self.path))
                try:
                        config = Configuration()
                        data = json.dumps(config.get_site_config(), cls=PGEncoder)
                except ConfigurationException as e:
                        data = {'status': 'failed', 'error': str(e)}
		api_log.info(data)
                return data


class RccnAPI(Daemonizer):
	def __init__(self):
		Daemonizer.__init__(self)

	def main_loop(self):
		api_log.info('Starting up RCCN API manager')
		app = RESTResource((SubscriberRESTService(),CreditRESTService(),StatisticsRESTService(),SMSRESTService(),ConfigurationRESTService()))
		app.run(8085)

if __name__ == '__main__':
	rccn_api_manager = RccnAPI()
	rccn_api_manager.process_command_line(sys.argv)
