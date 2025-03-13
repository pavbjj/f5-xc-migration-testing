import requests
import sys
import socket
import pandas as pd


api_token=sys.argv[1]
tenant=sys.argv[2]
namespace=sys.argv[3]
name_check="dmz"

endpoint="http_loadbalancers"

def fetch_all_lbs(endpoint,namespace,api_token,tenant):
    url = f"https://{tenant}.console.ves.volterra.io/api/config/namespaces/{namespace}/{endpoint}"
    print(url)
    headers = {"Authorization": f"APIToken {api_token}"}
    response = requests.get(url, headers=headers, timeout=4)
    data = response.json()
    status = response.status_code
    return [item["name"] for item in data.get("items", [])]

def fetch_domain_info(endpoint,namespace,api_token,tenant,lb):
    url = f"https://{tenant}.console.ves.volterra.io/api/config/namespaces/{namespace}/{endpoint}/{lb}"
    headers = {"Authorization": f"APIToken {api_token}"}
    response = requests.get(url, headers=headers)
    data = response.json().get("spec", {}).get("domains", {})
    return data

def fetch_status_code(fqdn):
    url = f"https://{fqdn}"
    try:
        response = requests.get(url,timeout=3)
        data = response.status_code
        return data
    except requests.RequestException as e:
        return {"error": str(e)}

def fetch_response_headers(fqdn):
    url = f"https://{fqdn}"
    try:
        response = requests.get(url, timeout=3)
        data = response.headers
        return data
    except requests.RequestException as e:
        return {"error": str(e)}

def fetch_server_header(fqdn):
    url = f"https://{fqdn}"
    try:
        response = requests.get(f"http://{domain}", timeout=3)
        # Use .get() to avoid KeyError in case 'server' header is not present
        server_header = response.headers.get('server', 'Server header not found')
        return server_header
    except requests.RequestException as e:
        print(f"Error fetching header for {domain}: {e}")
        return None
    
def get_ip_of_url(url):
    hostname = url.split("://")[-1].split("/")[0]
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror as e:
        print(f"Error resolving {hostname}: {e}")
        return None

lb_list=fetch_all_lbs(endpoint,namespace,api_token,tenant)
print(lb_list)

data_list=[]

for lb in lb_list:
    if name_check in lb.lower():
        domain_list = fetch_domain_info(endpoint,namespace,api_token,tenant,lb)
        for domain in domain_list:
            print(domain)
            status = fetch_status_code(domain)
            ip = get_ip_of_url(domain)
            response_headers = fetch_response_headers(domain)
            server_header = fetch_server_header(domain)
        
        data_list.append({
            "Domain" : domain,
            "Status_code" : status,
            "XC_Server_header" : server_header,
            "Response_headers" : response_headers
            # "IP" : ip
        })

df = pd.DataFrame(data_list)
df.to_excel("big-ip-migration.xlsx", index=False)
print("Excel file saved with API data.")
