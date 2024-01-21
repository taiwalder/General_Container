import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

#create empty data set
data = np.zeros((0,12))
columns = ['ID','NAME','KANTON','ADRESSE','PLZ','ORT','TELEFON','FAX','EMAIL','WEBSITE','KATEGORIE', 'FIRMA']
df = pd.DataFrame(data, columns = columns)

#URL = 'https://www.fskb.ch/der-fskb/mitglieder-und-standorte/?kt=BS'
#page = requests.get(URL)

#soup = BeautifulSoup(page.text, 'html.parser')

#function to extract Werk-Nummer and City
def get_visible_data(extract):
    ID_list = []; CP_list = []; ID_extended = []; 
    PLZ_list = []; Ort_list = [];
    for element in extract:
        sub_element = element.find('a')
        ID_values = sub_element.get('aria-controls','')
        ID_extended.append(ID_values)
        try:
            ID_list.append(int(ID_values[3:7]))
        except ValueError:
            ID_list.append(int(ID_values[3:6]))
        CP_list.append(sub_element.get_text(strip=True))
        PLZ_ORT = (element.find('div', class_='col-lg-12'))
        PLZ = str(PLZ_ORT.find_all(string=True, recursive = False))
        PLZ_list.append(int(PLZ[2:6]))
        Ort_list.append(PLZ[7:-2])
    return ID_list, CP_list, PLZ_list, Ort_list

                    
def get_werk_data(data):

    address_list = []; website_list = []; mail_list = [];
    fax_list = []; phone_list = []; name_list = []; ort_list = [];

    data = str(data)
    keyword = 'Werk: '
    split_parts = data.split(keyword, 3)
    #iterate over every Werk
    for i in range(1,len(split_parts)):
        #print(f'Working on: {keyword + split_parts[i]}')
        #convert string back to beautiful soup object
        current_werk = BeautifulSoup(keyword + split_parts[i], 'html.parser')
        werk_data = (current_werk.find_all(string=True))
        phone_counter=0

        for item in werk_data:
            #print(item)
            if item[0:6] == 'Werk: ':
                name_list.append(item)
                ort_list.append(item[6:])
            elif item[-1].isnumeric() and item[0:1].isalpha():
                address_list.append(item)
            elif 'strasse' in item:
                address_list.append(item)
            elif item[0:2].isnumeric() and item[-1].isnumeric:
                if phone_counter == 0:
                    phone_list.append(item)
                    phone_counter += 1 
                else:
                    fax_list.append(item) 
            elif '@' in item:
                mail_list.append(item)
            elif 'www.' in item:
                website_list.append(item)
                
        
        
        #fill holes for next round
        max_length = i
        
        address_list += [0] * (max_length - len(address_list))
        website_list += [0] * (max_length - len(website_list))
        mail_list += [0] * (max_length - len(mail_list))
        fax_list += [0] * (max_length - len(fax_list))
        phone_list += [0] * (max_length - len(phone_list))   
        ort_list += [0] * (max_length - len(ort_list))

    return address_list, website_list, mail_list, fax_list, phone_list, ort_list        

def get_collapsed_data(extract):
    address_list = []; website_list = []; mail_list = [];
    fax_list = []; phone_list = []; 

    for index, element in enumerate(extract):
        #print(type(extract))
        data = (element.find_all(string=True))
        phone_counter=0
        #print(element)
        for item in data:
        #check whether Werk it is Werk-data
            #print(item)
            if item[0:6] == 'Werk: ':
                get_werk_data(element)
                break
            elif item[-1].isnumeric() and item[0:1].isalpha():
                address_list.append(item)
                continue
            elif 'strasse' in item:
                address_list.append(item)
                continue
            elif item[0:2].isnumeric() and item[-1].isnumeric:
                if phone_counter == 0:
                    phone_list.append(item)
                    phone_counter += 1
                    continue
                else:
                    fax_list.append(item)
                    continue
            elif '@' in item:
                mail_list.append(item)
                continue
            elif 'www.' in item:
                website_list.append(item)
                continue    

        #fill holes for next round
        max_length = index+1
        
        address_list += [0] * (max_length - len(address_list))
        website_list += [0] * (max_length - len(website_list))
        mail_list += [0] * (max_length - len(mail_list))
        fax_list += [0] * (max_length - len(fax_list))
        phone_list += [0] * (max_length - len(phone_list))   
    
    listen_länge = len(address_list) + len(website_list) + len(mail_list) + len(fax_list) + len(phone_list)
    if listen_länge/5 == index+1:
        print(f'Alle Datenlisten haben genau {index+1} Einträge.')
    else:
        print('AAAALAAAAAAAAAARM')

    return address_list, website_list, mail_list, fax_list, phone_list

def compile_list_from_function(data_vis, data_col, kanton):
    #create empty lists for all categories
    ID_list = []; PLZ_list = []; Ort_list = []; CP_list = []; 

    mail_list = []; fax_list = []; phone_list = []; 
    name_list = []; ort_list = []; address_list = []; 
    website_list = []; kanton_list = []; cat_list = [];

    #fill the lists using the corresponding functions

    ID_list, CP_list, PLZ_list, Ort_list = (get_visible_data(data_vis))
    
    address_list, website_list, mail_list, fax_list, phone_list = (get_collapsed_data(data_col))

    kanton_list += [kanton] * len(ID_list)

    return ID_list, name_list, kanton_list, address_list, PLZ_list, Ort_list, phone_list, fax_list, mail_list, website_list, cat_list, CP_list

#extract all data from collapsible section


#print(get_visible_data(visible_data))
#print(collapsed_data)

#print(get_collapsed_data(collapsed_data))

###############################################
# ID_list, CP_list, PLZ_list, Ort_list, address_list, website_list, mail_list, fax_list, phone_list
#columns = ['ID','NAME','KANTON','ADRESSE','PLZ','ORT','TELEFON','FAX','EMAIL','WEBSITE','KATEGORIE', 'FIRMA']

def run():
    kantone = ['UR']
    ID = []; name = []; canton = []; address = []; PLZ = []; Ort = []; phone = []; fax = []; mail = []; website = []; cat = []; CP = []; 
    for kanton in kantone:
        
        URL = 'https://www.fskb.ch/der-fskb/mitglieder-und-standorte/?kt='+kanton
        page = requests.get(URL)
        soup = BeautifulSoup(page.text, 'html.parser')
        visible_data = soup.find_all('div', class_= 'row firma-wrapper')
        collapsed_data = soup.find_all('div', class_ ='col-lg-12 collapse')
        lists = compile_list_from_function(visible_data, collapsed_data, kanton)
        ID += lists[0]; name += lists[1]; canton += lists[2]; address += lists[3]; PLZ += lists[4]; Ort += lists[5]; phone += lists[6]; fax += lists[7]; mail += lists[8]; website += lists[9]; cat += lists[10]; CP += lists[11]
    return ID, name, canton, address, PLZ, Ort, phone, fax, mail, website, cat, CP, visible_data, collapsed_data

out = run()
for index, column in enumerate(columns):
    try:
        df[column] = out[index]
    except ValueError:
        print('No values for this category yet.')

print(df)






