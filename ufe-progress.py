# coding: utf-8

import re, time

log = open("/var/www/html/ufe/video_encoded/6f67484ea6/la_duena-6f67484ea6-360pw.log", "r")
# frame=   29 fps=  0 q=2.6 size=     114kB time=0.79 bitrate=1181.0kbits/s

for line in log:
	
	duration_re = re.compile("""Duration: (?P<duration>\S+),""")
        match = re.search(duration_re, line, re.M)
        m = re.findall(duration_re, line)
	if match is not None:
                duration = m[0]
                #print duration

	time_done_re = re.compile("""time=(?P<time>\S+)""")
	match = re.search(time_done_re, line, re.M)
	m = re.findall(time_done_re, line)
	if match is not None:
		time_done = m[-1:][0]
		#print time_done

log.close()

time_done_int = float(time_done.replace(":", "").replace(".",""))
duration_int = float(duration.replace(":", "").replace(".",""))
print time_done_int, duration_int
print round(float((time_done_int*100 )/duration_int),2),"%"
