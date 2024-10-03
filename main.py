from scraper import scraper
from data_import import load_ID
import pandas as pd
from unusual_format import get_parl_meetings, get_comm_meetings, check_recent
import requests
from openpyxl import load_workbook
from tqdm import tqdm
from time import sleep
YEAR = 5 #Considered recent if had a meeting in the past X years
scrapy = scraper()

df_main = pd.DataFrame(columns=['id', 'name', 'status', 'registered', 'website', 'country', 'entity_type', 'total_budget', 'funding_member', 'funding_public','funding_donation', 'funding_grants', 'funding_EU', 'funding_other', 'description',  'parl_meeting', 'comm_meeting', 'recent_parl', 'recent_comm', 'nb_parl_meet', 'nb_comm_meet', 'parl_list', 'comm_list'])
#New Id from june to september
add_id = ['624449992257-11', '933163493346-38', '738447993202-73', '411891392285-37','742890293382-07','132444393028-75','675530492747-51','049459192300-94','264559792803-58','291759092882-45','345260292447-93','197893993146-88','317200893384-66','303897393127-14','062342593080-11','030789693434-15','739781392944-02','899966792430-530','303373093405-56','646472092848-46','585109992192-06','944604893432-85','529340893451-25','325076893433-19', '077271193585-62', '303373093405-56', '135748793646-38', '965708393648-13', '408695993670-28']
df_main['id'] = [*load_ID('/mnt/2To/jupyter_data/FTM/ThinkTank/transparency.json'), *add_id]
to_link = []
line = 2
with pd.ExcelWriter("output-tmp.xlsx", engine='xlsxwriter') as writer:
    for id in tqdm(df_main['id'].values):
        one_recent = False
        try:
            entry = scrapy.get_infos(id)
            if entry == []:
                df_main = df_main[df_main['id'] != id]
            else:
                if (pd.to_datetime(entry['registered'], format='%d/%m/%Y %H:%M:%S', errors='coerce') > (pd.Timestamp.now() - pd.DateOffset(years=YEAR))):
                    one_recent = True
                parl_state , df_parl_meet = get_parl_meetings(entry['parl_meeting'])
                nb_parl_meet = df_parl_meet.shape[0]
                comm_state , df_comm_meet = get_comm_meetings(entry['comm_meeting'])
                nb_comm_meet = df_comm_meet.shape[0]
                for state, df, nb_meet, key in zip([parl_state, comm_state], [df_parl_meet, df_comm_meet], [nb_parl_meet, nb_comm_meet], ['parl', 'comm']):
                    match state:
                        case 0:
                            entry[f'{key}_meeting'] = 'ERROR'
                            entry[f'recent_{key}'] = False
                            entry[f'nb_{key}_meet'] = 0
                        case 1:
                            entry[f'{key}_meeting'] = 'NO'
                            entry[f'recent_{key}'] = False
                            entry[f'nb_{key}_meet'] = 0
                        case 2:
                            entry[f'{key}_meeting'] = 'YES'
                            entry[f'nb_{key}_meet'] = nb_meet
                            recent = check_recent(df, YEAR)
                            one_recent = True if recent == True else one_recent #Switch one recent to True if one of two is true. 
                            entry[f'recent_{key}'] = recent
                            if one_recent:
                                df.to_excel(writer, sheet_name=f"{id.replace('-','_')}_{key}", index=False)
                                letter = 'T' if key == 'parl' else 'U'
                                link = {'from' : f'{letter}{line}',
                                        'to': f"{id.replace('-','_')}_{key}"}
                                to_link.append(link)
                if one_recent: #check if recent enough meeting took place
                    line +=1
                    entry['funding_member'] = True if "Member's contributions" in entry['funding_source'] else False
                    entry['funding_public'] = True if "Public funding" in entry['funding_source'] else False
                    entry['funding_donation'] = True if "Donations" in entry['funding_source'] else False
                    entry['funding_grants'] = True if "Grants" in entry['funding_source'] else False
                    entry['funding_EU'] = True if "EU funding" in entry['funding_source'] else False
                    entry['funding_other'] = True if "Other" in entry['funding_source'] else False
                    for keys in df_main.columns[1:-2]:
                        df_main.loc[df_main['id']==str(id),keys] = entry[keys]
                else: #remove element if no recent enough took place
                    df_main = df_main[df_main['id'] != id]
        except requests.RequestException as e:
            print(f"error {e} with id {id}")
    scrapy.kill()
    df_main.to_excel(writer, sheet_name='Sheet1', index=False)

# Add internal hyperlinks
wb = load_workbook('output-tmp.xlsx')
ws1 = wb['Sheet1']
for el in to_link:
    ws1[el['from']] = f'=HYPERLINK("#{el["to"]}!A1", "OPEN")'

wb.save('output-tmp.xlsx')

df_main.to_pickle('NEW_EU_TT2.pkl')


