from base import BaseParser, log 
import re

class Parser(BaseParser):
    '''
    Ettercap password parser.  This parser interprets the output from ettercap
    (basically looking for account info) and then passes it on to the API.
    '''
    name = 'ettercap'
    #ruser = re.compile(r'USER: (.*?)  ')    # USER Regex: Pulls out USER field.
    ruser = re.compile(r'USER: (\S*)')    # USER Regex: Pulls out USER field.
    rpass = re.compile(r'PASS: (\S*)')    # PASS Regex: Pulls out PASS field.
    rinfo = re.compile(r'INFO: (.*?)$')     # INFO Regex: Pulls out INFO field.
    rproto = re.compile(r'^(\w*) : ')       # PROTO Regex: Pulls the protocal.
    rhost = re.compile(r'^\w* : (\S*)')    # Host regex, extract the IP address/port
    rcommunity = re.compile('COMMUNITY: (\S*)')	# SNMP community

    def parse(self, line):
        '''Ettercap line output parser.'''
	log.debug('ETTERCAP: DEBUG0: %s' % line)
        if 'USER' in line:
            usernames = self.ruser.findall(line)
            passwords = self.rpass.findall(line)
            infos = self.rinfo.findall(line)
            protos = self.rproto.findall(line)
            hosts = self.rhost.findall(line)
            log.debug('ETTERCAP: DEBUG1: %s, %s, %s,%s' % (usernames,passwords,infos,protos))
            if len(usernames) > 0 and len(passwords) > 0:
                username = usernames[0]
                password = passwords[0]
                host     = hosts[0]
                proto    = protos[0]
                try:
                    info = infos[0]
                except:
                    info = ''
                if proto == 'FTP':
                    info = host
                log.debug('ETTERCAP: sending Account <%s>' % username)
                self.api.account(username, password, info, proto, 'ettercap')

        if 'COMMUNITY' in line:
            communities = self.rcommunity.findall(line)
            hosts = self.rhost.findall(line)
            host = (hosts[0].split(':'))[0]
            port = (hosts[0].split(':'))[1]
            protos = self.rproto.findall(line)
            if len(communities) > 0 and port == '161':
                community = communities[0]
                proto     = protos[0]
                log.debug('ETTERCAP: sending SNMP community: <%s>' % community)
                self.api.account('n/a', community, host, proto, 'ettercap')
            
