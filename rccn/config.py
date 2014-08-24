import sys, os, logging, time, re, glob, importlib
import psycopg2
import psycopg2.extras
import sqlite3
import json
import riak
from riak.transports.pbc.transport import RiakPbcTransport
from logging import handlers as loghandlers
from decimal import Decimal
from datetime import date
from config_values import *

class PGEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return str(obj)
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


# Loggers
smlog = loghandlers.RotatingFileHandler(rhizomatica_dir+'/rccn/log/rccn.log', 'a', 104857600, 5)
formatter = logging.Formatter('%(asctime)s => %(name)-7s: %(levelname)-8s %(message)s')
smlog.setFormatter(formatter)

blog = loghandlers.RotatingFileHandler(rhizomatica_dir+'/rccn/log/billing.log', 'a', 104857600, 5)
blog.setFormatter(formatter)

alog = loghandlers.RotatingFileHandler(rhizomatica_dir+'/rccn/log/rapi.log', 'a', 104857600, 5)
alog.setFormatter(formatter)

slog = loghandlers.RotatingFileHandler(rhizomatica_dir+'/rccn/log/subscription.log', 'a', 104857600, 5)
slog.setFormatter(formatter)

smslog = loghandlers.RotatingFileHandler(rhizomatica_dir+'/rccn/log/sms.log', 'a', 104857600, 5)
smslog.setFormatter(formatter)

rlog = loghandlers.RotatingFileHandler(rhizomatica_dir+'/rccn/log/reseller.log', 'a', 104857600, 5)
rlog.setFormatter(formatter)

roaminglog = loghandlers.RotatingFileHandler(rhizomatica_dir+'/rccn/log/roaming.log', 'a', 104857600, 5)
roaminglog.setFormatter(formatter)

logging.basicConfig()

# initialize logger RCCN
log = logging.getLogger('RCCN')
log.addHandler(smlog)
log.setLevel( logging.DEBUG)

# initialize logger BILLING
bill_log = logging.getLogger('RCCN_BILLING')
bill_log.addHandler(blog)
bill_log.setLevel(logging.DEBUG)

# initialize logger API
api_log = logging.getLogger('RCCN_API')
api_log.addHandler(alog)
api_log.setLevel(logging.DEBUG)

# initialize logger RSC
subscription_log = logging.getLogger('RCCN_RSC')
subscription_log.addHandler(slog)
subscription_log.setLevel(logging.DEBUG)

# initialize logger SMS
sms_log = logging.getLogger('RCCN_SMS')
sms_log.addHandler(smslog)
sms_log.setLevel(logging.DEBUG)

# initialize logger RESELLER
res_log = logging.getLogger('RCCN_RESELLER')
res_log.addHandler(rlog)
res_log.setLevel(logging.DEBUG)

# initialize logger ROAMING
roaming_log = logging.getLogger('RCCN_ROAMING')
roaming_log.addHandler(roaminglog)
roaming_log.setLevel(logging.DEBUG)

# Extensions
class ExtensionException(Exception):
    pass

extensions_list = []
os.chdir(rhizomatica_dir+'/rccn/extensions/')
files = glob.glob(rhizomatica_dir+'/rccn/extensions/ext_*.py')
for f in files:
    file_name = f.rpartition('.')[0]
    ext_name = file_name.split('_')[1]
    extensions_list.append(ext_name)


# initialize DB handler
db_conn = None
config = {}
try:
    db_conn = psycopg2.connect(database=pgsql_db, user=pgsql_user, password=pgsql_pwd, host=pgsql_host)
    cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * from site')
    site_conf = cur.fetchone()
    
    config['site_name'] = site_conf['site_name']
    config['internal_prefix'] = site_conf['postcode']+site_conf['pbxcode']
    config['local_ip'] = site_conf['ip_address']
    
    # load SMS shortcode into global config
    cur.execute('SELECT smsc_shortcode,sms_sender_unauthorized,sms_destination_unauthorized FROM configuration')
    smsc = cur.fetchone()
    config['smsc'] = smsc[0]
    config['sms_source_unauthorized'] = smsc[1]
    config['sms_destination_unauthorized'] = smsc[2]
except psycopg2.DatabaseError as e:
    log.error('Database connection error %s' % e)

# Connect to riak
#riak_client = riak.RiakClient(protocol='http', host='127.0.0.1', http_port=8098)
# use protocol buffers
riak_client = riak.RiakClient(pb_port=8087, protocol='pbc')

# load modules
from modules import subscriber
Subscriber = subscriber.Subscriber
SubscriberException = subscriber.SubscriberException

from modules import numbering
Numbering = numbering.Numbering
NumberingException = numbering.NumberingException

from modules import billing
Billing = billing.Billing

from modules import credit
Credit = credit.Credit
CreditException = credit.CreditException

from modules import configuration
Configuration = configuration.Configuration
ConfigurationException = configuration.ConfigurationException

from modules import statistics
CallsStatistics = statistics.CallsStatistics
CostsStatistics = statistics.CostsStatistics
StatisticException = statistics.StatisticException

from modules import sms
SMS = sms.SMS
SMSException = sms.SMSException

from modules import subscription
Subscription = subscription.Subscription
SubscriptionException = subscription.SubscriptionException

from modules import reseller
Reseller = reseller.Reseller
ResellerException = reseller.ResellerException