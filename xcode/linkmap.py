
#######################################################################
#
#	The following license supersedes all notices in the source code.
#
#	Copyright (c) 2017 Kurt Dekker/PLBM Games All rights reserved.
#
#	@kurtdekker - http://www.plbm.com
#	
#	Redistribution and use in source and binary forms, with or without
#	modification, are permitted provided that the following conditions are
#	met:
#	
#	Redistributions of source code must retain the above copyright notice,
#	this list of conditions and the following disclaimer.
#	
#	Redistributions in binary form must reproduce the above copyright
#	notice, this list of conditions and the following disclaimer in the
#	documentation and/or other materials provided with the distribution.
#	
#	Neither the name of the Kurt Dekker/PLBM Games nor the names of its
#	contributors may be used to endorse or promote products derived from
#	this software without specific prior written permission.
#	
#	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#	IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#	TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#	PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#	HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#	SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#	TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#	PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#	LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#	NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#	SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#######################################################################
#
# Author: Kurt Dekker # # 7:28 PM 7/25/2017
#
# XCode linkmap parser - parses linkmaps from XCode and displayes the
# contributions of the object files, sorted by size.
#
# Generally these linkmaps are found in ~/Library/Developer/Xcode/DerivedData
# with a series of bash commands such as:
#
#		cd ~/Library/Developer/Xcode/DerivedData
#		find -f . | grep LinkMap
#
#######################################################################
#
# Objfiles that match these strings will be removed and put into
# separate lists at printout time.
#
identified_sections = [
	"libiPhone-lib.a",
]

# Any piece smaller than this number is not reported
minimum_total_size = 10240

def	read_additional_identified_sections_file(file):
	try:
		with open( file) as fpi:
			for section in fpi.readlines():
				section = section.rstrip()
				if len(section) > 2:
					if not section in identified_sections:
						identified_sections.append(section)
	except IOError:
		print "Did not find identified_sections.txt file. Breaking it up by defaults."

	return

class	objfile:
	def	__init__(self,number,name):
		self.number = number
		self.name = name
		self.size = 0
		return
	def	__repr__(self):
		return "%u,%u,\"%s\"" % (self.size, self.number, self.name)

def	main(argv):
	import re
	with open( argv[1]) as fpi:
		contents = [a.rstrip() for a in fpi.readlines()]

	objfiles = dict()

	lineno = 0
	while 1:
		if lineno >= len(contents):
			break
		line = contents[lineno]

		# we terminate after the .o files because stray crap
		# later on in the string literals can screw up the regex!!
		if line == "# Sections:":
			break

		m = re.search( "^\[(.*?)\]\s*(.*)$", line)
		if m:
			fileno = int(m.group(1))
			payload = m.group(2)
			objfiles[fileno] = objfile( fileno, payload)

		lineno += 1

	scanning = 0
	while 1:
		if lineno >= len(contents):
			break
		line = contents[lineno]

		if scanning:
			m = re.search( "^(0x[0-9A-Fa-f]*)\s(0x[0-9A-Fa-f]*)\s*\[(.*?)\]", line)
			if m:
				address = m.group(1)
				size = m.group(2)
				fileno = m.group(3)

				address = int(address,16)
				size = int(size,16)
				fileno = int(fileno)

#				print "0x%09x 0x%08x [%u]" % (address, size, fileno)

				of = objfiles[fileno]
				of.size += size

		if line == "# Symbols:":
			scanning = 1

		lineno += 1

	print "Found %u objfiles." % len( objfiles)
	print

	files = [objfiles[x] for x in objfiles]

	files.sort( key = lambda a: -a.size)

	print "Filtering contributions on size must be larger than %u" % minimum_total_size
	files = filter( lambda a: a.size >= minimum_total_size, files)

	def	header():
		print
		print "Size,ObjFileNo,ObjectFileName"

	header()

	for file in files:
		print file

	print
	print "Broken down by identified_sections:"
	print

	section_lists = dict()

	commonkey = "(everything else)"

	for file in files:
		wasadded = None
		for sectionkey in identified_sections:
			if file.name.find( sectionkey) >= 0:
				if not section_lists.has_key(sectionkey):
					section_lists[sectionkey] = []
				section_lists[sectionkey].append( file)
				wasadded = 1
				break
		if not wasadded:
			if not section_lists.has_key(commonkey):
				section_lists[commonkey] = []
			section_lists[commonkey].append( file)

	for sectionkey in list(identified_sections) + [commonkey]:
		if section_lists.has_key(sectionkey):
			section = section_lists[sectionkey]

			totalsize = 0
			for piece in section:
				totalsize += piece.size

			print
			print "identified section '%s',total size: %u" % (sectionkey, totalsize)

			header()

			for piece in section:
				print piece

	return

import os, sys
if __name__ == "__main__":
	read_additional_identified_sections_file( "identified_sections.txt") 
	main(sys.argv)
