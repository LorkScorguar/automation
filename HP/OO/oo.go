//Simple go program to interact with HP OO api

package main

import "fmt"
import "net/http"
import "io/ioutil"
import "encoding/json"
import "os"
import "bufio"
import "bytes"
import "strconv"

func getVersion(user string, password string, oourl string) (version string){
	client:=&http.Client{}
	oourl+="version"
	req,_:= http.NewRequest("GET",oourl,nil)
	req.Header.Add("content-type","application/json")
	req.SetBasicAuth(user,password)
	resp,_:=client.Do(req)
	defer resp.Body.Close()
	body,_:=ioutil.ReadAll(resp.Body)
	var jResp interface{}
	json.Unmarshal(body,&jResp)
	m:=jResp.(map[string]interface{})
	version=m["version"].(string)
	return
}

func cancelPausedFlows(user string, password string, oourl string) (result string){
	client:=&http.Client{}
	req,_:= http.NewRequest("GET",oourl+"executions?status=PAUSED",nil)
	req.Header.Add("content-type","application/json")
	req.SetBasicAuth(user,password)
	resp,_:=client.Do(req)
	defer resp.Body.Close()
	body,_:=ioutil.ReadAll(resp.Body)
	var jResp []interface{}
	json.Unmarshal(body,&jResp)
	if len(jResp)==0{
		result="No paused flows"
	} else {
		for i:=range jResp{
			m:=jResp[i].(map[string]interface{})
			eid:=m["executionId"].(string)
			var flow=[]byte(`{"action":"CANCEL"}`)
			req,_:= http.NewRequest("PUT",oourl+"executions/"+eid+"/status",bytes.NewBuffer(flow))
			req.Header.Add("content-type","application/json")
			req.SetBasicAuth(user,password)
			resp,_:=client.Do(req)
			defer resp.Body.Close()
		}
		result="Cancelled "+strconv.Itoa(len(jResp))+" flows\n"
	}
	return
}

func main() {
	var password string
	var user string
	var oourl string
	var choice int
	fmt.Printf("Enter Username:")
	fmt.Scanln(&user)
	user="DOMAIN\\"+user
	fmt.Printf("Enter password:")
	fmt.Scanln(&password)
	fmt.Printf("Enter OO url (http|https://<fqdn>:<port>/oo):")
	fmt.Scanln(&oourl)
	oourl=oourl+"/rest/latest/"
	fmt.Printf("What do you want to do?\n1-Get Version\n2-Cancel paused flows\n")
	fmt.Scanln(&choice)
	switch choice {
		case 1:
			version:=getVersion(user,password,oourl)
			fmt.Printf(version+"\n")
		case 2:
			cancelled:=cancelPausedFlows(user,password,oourl)
			fmt.Printf(cancelled+"\n")
		default:
			fmt.Printf("I don't understand")
	}
	bufio.NewReader(os.Stdin).ReadBytes('\n')
}
