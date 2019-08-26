'''
testing origin response headers to not cache
'''

#  Licensed to the Apache Software Continueation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os

Test.Summary = 'testing origin response headers to not cache'

# Needs Curl
Test.SkipUnless(
    Condition.HasProgram("curl", "curl needs to be installed on system for this test to work"),
)
Test.ContinueOnFail = True

# Define default ATS
ts = Test.MakeATSProcess("ts")

###### ATS Configuration ######
ts.Disk.plugin_config.AddLine('xdebug.so')
ts.Disk.remap_config.AddLine(
'map / http://127.0.0.1/'
)
ts.Disk.records_config.update({
   'proxy.config.http.insert_request_via_str' : 1,
   'proxy.config.http.insert_response_via_str' : 3,
   'proxy.config.http.request_via_str' : 'ApacheTrafficServer',
   'proxy.config.http.response_via_str' : 'ApacheTrafficServer',
   'proxy.config.cache.ram_cache.algorithm': 1,
   'proxy.config.cache.ram_cache.use_seen_filter': 1,
   'proxy.config.log.logging_enabled' : 3,
   'proxy.config.diags.debug.enabled': 1,
   'proxy.config.diags.debug.tags': 'http|dns',
   'proxy.config.diags.output.debug': 'L',
   'proxy.config.hostdb.host_file.path' : '/etc/hosts',
   'proxy.config.http.cache.ignore_authentication' : 1,
})

###### Test Run ######
# Test 1 - 1 :
#   Characteristic Client Request header : none
#   Characteristic Origin Response header : Cache-Control:max-age=5, no-store
#
# Via Infomation : [uScMsSf pSeN:t cCMp sS]
#   client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#   cache-fill is blank(no cache write performed) , proxy-info is S(served) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_f/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/200_OK_not_cache_with_cache_control.gold"
tr.StillRunningAfter = ts

# Test 2 - 1 :
#   Characteristic Client Request header : none
#   Characteristic Origin Response header : Cache-Control:max-age=5, private
#
# Via Infomation : [uScMsSf pSeN:t cCMp sS]
#   client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#   cache-fill is blank(no cache write performed) , proxy-info is S(served) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_g/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/200_OK_not_cache_with_cache_control.gold"
tr.StillRunningAfter = ts

# Test 3 - 1 :
#   Characteristic Client Request header : none
#   Characteristic Origin Response header : Cache-Control:max-age=5 , WWW-Authenticate: Basic realm="test"
#
# Via Infomation : [uScMsSfWpSeN:t cCMp sS]
#   client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#   cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_h/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/401_Unauthorized_cache_write.gold"
tr.StillRunningAfter = ts
# Test 3 - 2 :
# Via Infomation : [uScHs f p eN:t cCHp s ]
#   client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#   cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_h/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/401_Unauthorized_cache_hit.gold"
tr.StillRunningAfter = ts

# Test 3 - 3 :
#   Characteristic Client Request header : none
#   Characteristic Origin Response header : Cache-Control:max-age=5, public , WWW-Authenticate: Basic realm="test"
#
# Via Infomation : [uScMsSfWpSeN:t cCMp sS]
#   client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#   cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_h_public/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/401_Unauthorized_cache_write.gold"
tr.StillRunningAfter = ts
# Test 3 - 4 :
# Via Infomation : [uScHs f p eN:t cCHp s ]
#   client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#   cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_h_public/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/401_Unauthorized_cache_hit.gold"
tr.StillRunningAfter = ts

# Test 4 - 1 :
#   Characteristic Client Request header : none
#   Characteristic Origin Response header : Cache-Control:max-age=5 , Set-Cookie: hoge=fuga
#
# Via Infomation : [uScMsSfWpSeN:t cCMp sS]
#   client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#   cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_i/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/200_OK_cache_write.gold"
tr.StillRunningAfter = ts
# Test 4 - 2 :
# Via Infomation : [uScHs f p eN:t cCHp s ]
#   client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#   cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_i/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/200_OK_cache_hit.gold"
tr.StillRunningAfter = ts

# Test 5 - 1 :
#   Characteristic Client Request header : none
#   Characteristic Origin Response header : Cache-Control:max-age=5, no-cache
#
# Via Infomation : [uScMsSfWpSeN:t cCMp sS]
#   client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#   cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_j/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/200_OK_cache_write.gold"
tr.StillRunningAfter = ts
# Test 5 - 2 :
# Via Infomation : [uScSsNfUpSeN:t cCSp sS]
#   client-info is S(simple request, not conditional) , cache-lookup is S(in cache, stale) , server-info is S(served) ,
#   cache-fill is U(updated old cache copy) , proxy-info is S(served) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_j/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/200_OK_cache_expired.gold"
tr.StillRunningAfter = ts

# Test 6 - 1 :
#   Characteristic Client Request header : none
#   Characteristic Origin Response header : Cache-Control:max-age=5 , Expires: 0
#
# Via Infomation : [uScMsSfWpSeN:t cCMp sS]
#   client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#   cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_k/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/200_OK_cache_write.gold"
tr.StillRunningAfter = ts
# Test 6 - 2 :
# Via Infomation : [uScHs f p eN:t cCHp s ]
#   client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#   cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_k/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/200_OK_cache_hit.gold"
tr.StillRunningAfter = ts

# Test 7 - 1 :
#   Characteristic Client Request header : none
#   Characteristic Origin Response header : Cache-Control:max-age=5
#
# Via Infomation : [uScMsSfWpSeN:t cCMp sS]
#   client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#   cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_401/'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/401_Unauthorized_cache_write.gold"
tr.StillRunningAfter = ts
# Test 7 - 2 :
# Via Infomation : [uScHs f p eN:t cCHp s ]
#   client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#   cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_401/'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/401_Unauthorized_cache_hit.gold"
tr.StillRunningAfter = ts

# Test 8 - 1 :
#   Characteristic Client Request header : none
#   Characteristic Origin Response header : Cache-Control:max-age=5, WWW-Authenticate: Basic realm="test"
#
# Via Infomation : [uScMsSfWpSeN:t cCMp sS]
#   client-info is S(simple request, not conditional) , cache-lookup is M(miss) , server-info is S(served) ,
#   cache-fill is W(written into cache, new copy) , proxy-info is S(served) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_200_auth/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/200_OK_cache_write.gold"
tr.StillRunningAfter = ts
# Test 8 - 2 :
# Via Infomation : [uScHs f p eN:t cCHp s ]
#   client-info is S(simple request, not conditional) , cache-lookup is H(in cache, fresh) , server-info is blank(no server connection needed) ,
#   cache-fill is blank(=not recorded) , proxy-info is blank(=not recorded) , error-codes is N(no error)
tr = Test.AddTestRun()
tr.Processes.Default.StartBefore(Test.Processes.ts)
tr.Processes.Default.Command = 'curl -s -D - -v --ipv4 --http1.1 http://localhost:{port}/test_200_auth/index.html'.format(port=ts.Variables.port)
tr.Processes.Default.ReturnCode = 0
tr.Processes.Default.Streams.stdout = "gold/200_OK_cache_hit.gold"
tr.StillRunningAfter = ts
