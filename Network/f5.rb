require 'httpclient'
require 'json'

def create_node(f5_url,f5_user,f5_password,ip,name)
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"ltm/node"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	headers = { "Content-Type" => "application/json", "Accept" => "application/json;version=2" }
	content = { :kind => 'tm:ltm:node:nodecollectionstate', :name => ip, :description => name, :address => ip }
	response = http.post(uri, content.to_json, headers)
	jResp=JSON.parse(response.content)
	#puts(jResp)
end

def delete_node(f5_url,f5_user,f5_password,name)
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"ltm/node/#{name}"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	response = http.delete(uri)
end

def create_monitor(f5_url,f5_user,f5_password,monitor_name,monitor_type,monitor_from,monitor_dest,monitor_interv,monitor_dscp,monitor_recv,monitor_send1,monitor_send2,monitor_until,monitor_timeout)
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"ltm/monitor/http"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	headers = { "Content-Type" => "application/json", "Accept" => "application/json;version=2" }
	content = { :name => monitor_name,
	'defaults-from' => monitor_from,
	'destination' => monitor_dest,
	'interval' => monitor_interv,
	'ip-dscp' => monitor_dscp,
	'recv' => monitor_recv,
	'send' => monitor_send1+monitor_send2,
	'time-until-up' => monitor_until,
	'timeout' => monitor_timeout
	}
	response = http.post(uri, content.to_json, headers)
	jResp=JSON.parse(response.content)
	#puts(jResp)
end

def delete_monitor(f5_url,f5_user,f5_password,name)
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"ltm/monitor/http/#{name}"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	response = http.delete(uri)
	#puts(response.content)
end

def create_pool(f5_url,f5_user,f5_password,name,members,lbmode,monitoring)
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"ltm/pool"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	headers = { "Content-Type" => "application/json", "Accept" => "application/json;version=2" }
	content = { :kind => 'tm:ltm:pool:poolstate', :name => name, :loadBalancingMode => lbmode, :monitor => monitoring, :members => members }
	response = http.post(uri, content.to_json, headers)
	jResp=JSON.parse(response.content)
	#puts(jResp)
end

def delete_pool(f5_url,f5_user,f5_password,name)
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"ltm/pool/#{name}"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	response = http.delete(uri)
	#puts(response.content)
end

def create_virtual(f5_url,f5_user,f5_password,name,dest,satranslate,pool,profil_http,profil_tcp,profil_oneconnect,profil_persistence)
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"ltm/virtual"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	headers = { "Content-Type" => "application/json", "Accept" => "application/json;version=2" }
	vsprofil=
	[
	{'kind' => 'ltm:virtual:profile',  'name' => profil_http},
	{'kind' => 'ltm:virtual:profile',  'name' => profil_tcp},
	{'kind' => 'ltm:virtual:profile',  'name' => profil_oneconnect}
	]
	content = { :kind => 'tm:ltm:virtual:virtualstate', :name => name, :destination => dest, :sourceAddressTranslation => { :type => satranslate}, :profiles => vsprofil, :persist => profil_persistence, :pool => pool}
	response = http.post(uri, content.to_json, headers)
	jResp=JSON.parse(response.content)
	#puts(jResp)
end

def delete_virtual(f5_url,f5_user,f5_password,name)
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"ltm/virtual/#{name}"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	response = http.delete(uri)
	#puts(response.content)
end

def gtm_conf(f5_url,f5_user,f5_password,f5_servername,name,name2,url)
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"gtm/pool"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	headers = { "Content-Type" => "application/json", "Accept" => "application/json;version=2" }
	content = { :name => name, :members => [
	{:name => "#{f5_servername}:/Common/#{name}",
	:order => 0},
	{:name => "#{f5_servername}:/Common/#{name2}",
	:order => 1}
	]}
	response = http.post(uri, content.to_json, headers)
	jResp=JSON.parse(response.content)
	#puts(jResp)
	
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"gtm/wideip"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	headers = { "Content-Type" => "application/json", "Accept" => "application/json;version=2" }
	members=[{:name => name}]
	content = { :name => url, :pools => members}
	response = http.post(uri, content.to_json, headers)
	jResp=JSON.parse(response.content)
	#puts(jResp)
end

def delete_gtm(f5_url,f5_user,f5_password,name,url)
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"gtm/wideip/#{url}"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	response = http.delete(uri)
	#puts(response.content)
	
	http = HTTPClient.new
	http.ssl_config.verify_mode = OpenSSL::SSL::VERIFY_NONE
	uri = f5_url+"gtm/pool/#{name}"
	http.set_auth(uri, f5_user, f5_password)
	http.www_auth.basic_auth.challenge(uri)
	response = http.delete(uri)
	#puts(response.content)
end

