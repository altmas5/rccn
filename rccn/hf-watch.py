#!/usr/bin/python
############################################################################
#
# RCCN (Rhizomatica Community Cellular Network)
#
# Copyright (C) 2018 keith <keith@rhizomatica.org>
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
'''
rhizo-hf-connector folder watch

'''

import os, re
import inotify.adapters
import config


if __name__ == "__main__":
    sms = config.SMS()
    log=config.log
    direction = 'incoming'

    log.info('Starting up RHIZ0-HF-WATCH')
    _hermes_path = b'/var/spool/' + direction + '_messages/'

    try:
        if not os.path.exists(_hermes_path):
            os.makedirs(_hermes_path)
    except Exception as e:
        log.debug(e)
        exit(-1)

    i = inotify.adapters.Inotify()
    i.add_watch(_hermes_path)

    try:
        for event in i.event_gen():
            if event is not None:
                (header, type_names, watch_path, filename) = event
                log.debug("Watcher event for file: %s %s" % (filename, type_names))
                if 'IN_CLOSE_WRITE' == type_names[0]:
                    _full_path = _hermes_path+filename
                    log.info("File: %s was written" % (_full_path))
                    m = re.match('msg-(.*).txt', filename)
                    #import code
                    #code.interact(local=locals())
                    _seq = m.groups()[0]
                    with open(_full_path, "r") as file:
                        _source = file.readline().strip()
                        _dest = file.readline().strip()
                        _msg = ''
                        line = file.readline()
                        while line:
                            _msg = _msg + line.strip()
                            line = file.readline()
                    log.info("Message (%s) from: %s to %s with %s" % (_seq, _source, _dest, _msg) )
                    sms.receive(_source, _dest, _msg, 'utf-8', 0, _seq)

                log.debug("WD=(%d) MASK=(%d) COOKIE=(%d) LEN=(%d) MASK->NAMES=%s "
                             "WATCH-PATH=[%s] FILENAME=[%s]",
                             header.wd, header.mask, header.cookie, header.len, type_names,
                             watch_path.decode('utf-8'), filename.decode('utf-8'))

    except Exception as e:
        log.info(e)
    
