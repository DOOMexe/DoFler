from base import BaseParser, log
import re
import os, glob
from PIL import Image


class Parser(BaseParser):
    '''
    Driftnet Parser.  This parser interprets the output of driftnet run in
    headless mode and will pickup the files that have been dropped on the
    disk.  Once sent to the api, we will remove the temporary file.  This should
    help keep the overall cruft on disk to a minimum.
    '''
    name = 'driftnet'

    def checkporn(self, im):
        '''
        Detect if a grabbed picture is porn by counting the % of "skin" color in the image
        Original idea: http://warriorhut.org/
        '''
	
        # Define my is_array function
        is_array = lambda var: isinstance(var, (list, tuple))

	# For performance reasons, don't scan small pictures < 100 x 100 pixels
	if im.size[0] < 100 or im.size[1] < 100:
            return 0
	
        im = im.crop((int(im.size[0]*0.2), int(im.size[1]*0.2), im.size[0]-int(im.size[0]*0.2), im.size[1]-int(im.size[1]*0.2)))
        skin = sum([count for count, rgb in im.getcolors(im.size[0]*im.size[1]) if is_array(rgb) and rgb[0]>60 and rgb[1]<(rgb[0]*0.85) and rgb[2]<(rgb[0]*0.7) and rgb[1]>(rgb[0]*0.4) and rgb[2]>(rgb[0]*0.2)])
        return float(skin)/float(im.size[0]*im.size[1])

    def parse(self, line):
        '''
        Driftnet output line parser. 
        '''
        # This parser is about as simple as they come.  Every line is simply a
        # filename of the image that driftnet carved out.  All we need to do is
        # open it up, send the data to the API, then remove the file.
        filename = line.strip('\r\n ')

        # Check if the picture is "porn"
        try:
            im = Image.open(filename)
            skinratio = self.checkporn(Image.open(filename)) * 100
            if skinratio > 30:
                log.debug('DRIFTNET: skipping image %s (detected as porn - skin: %s%%)' % (filename, skinratio))
            else:
                log.debug('DRIFTNET: sending image %s (skin: %s%%)' % (filename, skinratio))
                self.api.image(filename)
        except:
            log.debug('DRIFTNET: skipping image %s (not readable)' % filename)
        try:
            os.remove(filename)
        except:
            log.warn('DRIFTNET: cannot remove %s' % filename)

    def cleanup(self):
        '''
        Process cleanup.
        '''
        # Driftnet doesnt always clean up after itself, so here we will look to
        # see if the process is running, and if it isnt, then cleanup the
        # pidfile if it exists.
        pidfile = '/var/run/driftnet.pid'
        if os.path.exists(pidfile):
            try:
                os.kill(int(open(pidfile).read()), 0)
            except OSError, e:
                log.error('DRIFTNET: Cannot kill driftnet pidfile, still alive.')
            else:
                os.remove(pidfile)
