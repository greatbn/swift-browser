from common import get_api
import json
import requests

def get_storage_url(tenant_name, service, username, password, hostname, keystone_port):
    header = {'Content-Type': 'application/json'}
    params = json.dumps(
            {"auth": {"tenantName": tenant_name, "passwordCredentials": {"username": username, "password": password}}})
    method = 'POST'
    path = '/v2.0/tokens'
    response = get_api(method, path, params, header, hostname, keystone_port)
    if response.status == 200:
        data = json.loads(response.read())
        for i in range(len(data['access']['serviceCatalog'])):
            if data['access']['serviceCatalog'][i]['name'] == service:
                storage_url = data['access']['serviceCatalog'][i]['endpoints'][0]['internalURL']
                return storage_url
    if response.status == 400:
        error = 'Incorect username/password check again'
        return redirect(url_for('login', error=error))

def get_info_account(token,storage_url):
    error = ''
    header = {'X-Auth-Token': token}
    method = 'GET'
    storage_url = storage_url+'?format=json'
    try:
        req = requests.request(method=method,headers = header,url=storage_url)
        if req.status_code == 401:
            error = 'Time out'
            return error
        elif req.status_code == 200:
            return req.content
            #print req.raw.getheaders()
    except requests.ConnectionError:
        error = "Connection Error"
        return redirect(url_for('login', error=error))
def get_info_container(token,storage_url,container_name):
    error = ''
    header = {'X-Auth-Token': token}
    method = 'GET'
    url = storage_url+'/'+container_name+'?format=json'
    
    try:
        req = requests.request(method= method,headers = header,url=url)
        
        if req.status_code == 401:
            error = 'Time out'
            return redirect(url_for('login', error=error))
        elif req.status_code == 200:
            return req.content
    except requests.ConnectionError:
        error = 'Connection error'
        return redirect(url_for('login', error=error))


def get_subdir(token,storage_url,container_name,folder_name=None):
    error = ''
    header = {'X-Auth-Token': token}
    method = 'GET'
    if folder_name != None:
        url = storage_url+'/'+container_name+'?prefix='+folder_name+'&delimiter=/&format=json'
    else:
        url = storage_url+'/'+container_name+'?prefix=&delimiter=/&format=json'
    try:
        req = requests.request(method= method,headers = header,url=url)
        if req.status_code == 401:
            error = 'Time out'
            return redirect(url_for('login', error=error))
        elif req.status_code == 200:
            return req.content
    except requests.ConnectionError:
        error = 'Connection error'
        return redirect(url_for('login', error=error))

def list_item_in_dir(list_item):
    list_item_after_modify = []
    
    list_item = json.loads(list_item)
    for i in range(len(list_item)):
        info_item = {}
        if 'subdir' in list_item[i]:
            # print list_item[i]['subdir'].split('/')
            info_item['subdir'] = list_item[i]['subdir'].split('/')[-2]
            info_item['subdir_origin'] = list_item[i]['subdir']
            list_item_after_modify.append(info_item.copy())
            continue
        else:
            # print list_item[i]
            info_item['name'] = list_item[i]['name'].split('/')[len(list_item[i]['name'].split('/'))-1]
            info_item['name_origin'] = list_item[i]['name']
            info_item['hash'] = list_item[i]['hash']
            info_item['last_modified']  = list_item[i]['last_modified']
            info_item['bytes'] = list_item[i]['bytes']
            list_item_after_modify.append(info_item.copy())
            continue
    # print list_item_after_modify
    return list_item_after_modify   
def create_new_container(token,storage_url,container_name):
    error = ''
    header = {'X-Auth-Token': token }
    method = 'PUT'
    url = storage_url+'/'+container_name
    try:
        req = requests.request(method=method,headers= header , url = url)
        print req.status_code
        if req.status_code == 401:
            error = 'Time out'
            return error
        elif req.status_code == 202:
            error = "Container's name exist"
            return error
        elif req.status_code == 201:
            return 'Create new container successful'
    except requests.ConnectionError:
        error = 'Connection Error'
        return redirect(url_for('login', error=error))
def delete_object(token,storage_url,container_name,object_name):
    error = ''
    header = {'X-Auth-Token':token}
    method = "DELETE"
    url = storage_url + '/'+ container_name + '/' + object_name
    try:
        req = requests.delete(headers=header,url=url)
        print req.status_code
        if req.status_code == 401:
            error = 'Time out'
            return error
        elif req.status_code == 204:
            notify = 'Deleted'
            return notify
        elif req.status_code == 404:
            notify = "Unable Delete"
            return notify
    except ConnectionError:
        error = 'Connection Error'
        return redirect(url_for('login', error=error))

def delete_container(token,storage_url,container_name):
    error = ''
    header = {'X-Auth-Token':token}
    method = "DELETE"
    url = storage_url + '/'+ container_name
    try:
        req = requests.delete(headers=header,url=url)
        print req.status_code
        if req.status_code == 401:
            error = 'Time out'
            return error
        elif req.status_code == 204:
            notify = 'Deleted'
            return notify
        elif req.status_code == 409:
            notify = "Unable Delete"
            return notify
        elif req.status_code == 404:
            notify ="container not exist"
            return notify
    except ConnectionError:
        error = 'Connection Error'
        return redirect(url_for('login', error=error))
def download_object(token,storage_url,container_name,object_name):
    error = ''
    header = {'X-Auth-Token':token}
    method = "GET"
    url = storage_url + '/'+ container_name + '/' + object_name
    try:
        req = requests.get(headers=header,url=url,stream=True)
        return req 
    except ConnectionError:
        error = 'Connection Error'
        return redirect(url_for('login', error=error))
if __name__ == '__main__':
    # print create_new_container('9447b480f38e4bb6b6eb4591ecbe88e7','http://172.16.69.238:8080/v1/AUTH_870d62be2c254d428226da346dfe9fbf','saphi3')

    # list_container = json.loads(get_info_account('9447b480f38e4bb6b6eb4591ecbe88e7','http://172.16.69.238:8080/v1/AUTH_870d62be2c254d428226da346dfe9fbf'))

    # for i in range(0,len(list_container)):
    #     print get_info_container('9447b480f38e4bb6b6eb4591ecbe88e7','http://172.16.69.238:8080/v1/AUTH_870d62be2c254d428226da346dfe9fbf',list_container[i]['name'])
    pass