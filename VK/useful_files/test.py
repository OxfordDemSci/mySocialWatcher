import requests
import json
import re

response = requests.get(
    'https://pypi.org/project/har2requests/',

    headers={'Host': 'pypi.org', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate, br', 'Referer': 'https://www.google.com/', 'Connection': 'keep-alive', 'Cookie': 'session_id=QNqSBa8aTK8JPBuzF5bxDJO6lyFNH3gwkzxO2Fm_ePA.YIaoGA.6i3uhXxG_3cJ2tV8PRdLHcJF9PJF3ks8dY_y2KMkU0irgEsDsRLWu219SaGm64mooXuUFlQZLz8PDJGWfML--A; _ga=GA1.2.735785210.1619437594; _gid=GA1.2.1141903637.1619437594', 'Upgrade-Insecure-Requests': '1', 'If-None-Match': '"Ct27T19ykHNA4sVrkNSmeg"', 'Cache-Control': 'max-age=0'},
)

# Copy and paste the request header from browser's network panel
# getHeadersFromFirefox converts the string that you can copy in
# the firefox developer tools (tab network, right click on 1 request ->
# -> copy request-header) to a header that you can use here

testheaders="""
Host: www.linkedin.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
x-restli-protocol-version: 2.0.0
x-li-lang: en_US
x-li-track: {"clientVersion":"2.4.1498","mpVersion":"2.4.1498","osName":"web","timezoneOffset":3,"timezone":"Asia/Riyadh","deviceFormFactor":"DESKTOP","mpName":"campaign-manager-web","displayDensity":1,"displayWidth":1680,"displayHeight":1050}
x-li-page-instance: urn:li:page:d_campaign_details;5ctPoTnHRbObTPihqFid3w==
csrf-token: ajax:2093587861622909016
x-li-er-key: urn:li:sponsoredAccount:507131805
x-http-method-override: GET
content-type: application/x-www-form-urlencoded
Content-Length: 3178
Origin: https://www.linkedin.com
Connection: keep-alive
Referer: https://www.linkedin.com/campaignmanager/accounts/507131805/campaigns/new/details?campaignGroupId=615557454
Cookie: bcookie="v=2&12924590-f701-481b-85f7-c19b4542266d"; bscookie="v=1&20210605151237ae2ef469-025d-48ac-8628-cb7117040996AQEPTxcCAH5qpDBPxzyV-9d3SpqFoEf6"; li_rm=AQFriIKtZOttzAAAAXoNr-dxS_DF6A7jDSK0b6_2pA3XYF8baYr5AwLncQUDAd1arwbD7uFOP2CINH7Y6CHhif-HklHJdBuUecaT2OJ6KncOCCStFJjH10_Tl3dWU9f53B0XpDbSU6LAp51HSMCSKtbsnrQ8C985V9eFOpJZtonqYjoJxBp6OOyWr-lBXcUZQZE-ldLLRfRQ8xSKTSXbxVGnHPxgiK8oBzR7K0qF1ugvlPAGdvBQYpG9S6l6qkB3BUhU2gK1w4WPOYX_BJdi_ArWNBsHzOfDNHZh7LeuTL5YNb6LEibtpMQ9LdGZpnAjZENBa84hifegZ8nDuVc; _ga=GA1.2.212018236.1622906017; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C18809%7CMCMID%7C06822997612877381543424692258512506413%7CMCAAMLH-1625616225%7C6%7CMCAAMB-1625616225%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1625018625s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-1529527004; _gcl_au=1.1.138998113.1622906018; aam_uuid=07000757872865609933407496805101469158; JSESSIONID="ajax:2093587861622909016"; gpv_pn=www.linkedin.com%2Fcampaignmanager%2Faccounts%2F507131805%2Fcampaigns%2Fnew%2Fdetails; s_tslv=1625140200130; li_sugr=1bfe14c9-67c9-4f52-a88e-1ce3103bbf32; UserMatchHistory=AQJRJk1kA59PkQAAAXpaOo7tvScPpgWMr5zqnhVDn_aamnWi13rAHd-i0apBiGk2PRdtcNtNI0tlw10mpR9CN9l1lY4M3QrochfS4yFhDb5l9fLloz-x2Rd-aL0-c1waNBlfZGk4VOsT8clRNnmNBJydTEzTryjVOWdJuQyOUXwBlJy7vhO7ZJA-Q6nTksgUjP0HpzQmGtGaoudx8fMM7tjQvjmhscsF1JGC0xMxl8wcZCTNeCjruCOL8d1_GmHi-Civ5PuGRIehZgHldfdbYfdB-WCF01eXhyKUVm4; AnalyticsSyncHistory=AQKTN4ku6IdR7AAAAXpaOo7tMJ_iPnOh4y_LMOECs1TkWZEiBv60kDdpqs6YYO9xA1YenyGci3pAurjCCwDZ7Q; lms_ads=AQEXgyfAFVR6GgAAAXpaOpK3oBCSQF7mIDf7JBQnzcAnswsQFiMmloX2rtd8y82ySmIlTYQGQCHwhwjRc4l59ea7Q4epKSWN; lms_analytics=AQEXgyfAFVR6GgAAAXpaOpK3oBCSQF7mIDf7JBQnzcAnswsQFiMmloX2rtd8y82ySmIlTYQGQCHwhwjRc4l59ea7Q4epKSWN; _guid=2ad3c301-26bf-4569-9497-1c5b62ae039b; liveagent_oref=https://www.linkedin.com/help/lms?lang=en; liveagent_vc=2; liveagent_ptid=da3012a4-4bdb-4c0a-9c03-7ef8f6b5e9a3; li_at=AQEDATWfwXIDdQimAAABejQpWggAAAF6fEA6ak4Ab7EhEF_QX_MfJCneBq4ybhGBa_T3GfsnKDSiGm7o22vaceovcaOL1qqF_sq1IPNcGIj8Y2hFY5M-HS0inxBPnxu2XPeh_WmNdQUAV_Z4LR0RYbw4; liap=true; lidc="b=TB94:s=T:r=T:a=T:p=T:g=2696:u=30:i=1625137808:t=1625224208:v=2:sig=AQGo9i_-mkvsJwgiSAUJ-jpMRCrHJnh9"; lang=v=2&lang=en-us; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; s_plt=0.95; s_pltp=www.linkedin.com%2Fcampaignmanager%2Faccounts%2F507131805%2Fcampaigns%2Fnew%2Fdetails; s_ppv=www.linkedin.com%2Fcampaignmanager%2Faccounts%2F507131805%2Fcampaigns%2Fnew%2Fdetails%2C78%2C23%2C3038%2C3%2C8; s_ips=897; s_tp=3879; s_cc=true; s_sq=lnkdprod%3D%2526pid%253Dwww.linkedin.com%25252Fcampaignmanager%25252Faccounts%25252F507131805%25252Fcampaigns%25252Fnew%25252Fdetails%2526pidt%253D1%2526oid%253D%252528...o%252529%25253D%25253EUe%252528e%25252C%2525280%25252Cl.valueForRef%252529%252528t%252529%25252C%2525280%25252Cl.valueForRef%252529%252528r%252529%25252Cn%25252Ci%252529%252528...o%252529%2526oidt%253D2%2526ot%253DTEXT
TE: Trailers
"""
def getHeadersFromFirefox(headers):
    headers1={}
    for line in headers.split("\n")[1:-1]:
        headers1[line.split(':')[0]]= line[line.find(':')+2:]
    return headers1
headers = getHeadersFromFirefox(testheaders)



# Test it with a copied targeting-criteria in data:

response = requests.post(
    'https://www.linkedin.com/campaign-manager-api/campaignManagerAudienceCounts',
    headers=headers,
    data='q=targetingCriteria&cmTargetingCriteria=(include:(and:List((or:List((facet:(urn:urn%3Ali%3AadTargetingFacet%3Alocations,name:Locations),segments:List((urn:urn%3Ali%3Ageo%3A103644278,name:United%20States,facetUrn:urn%3Ali%3AadTargetingFacet%3Alocations,ancestorUrns:List(urn%3Ali%3Ageo%3A102221843)))))),(or:List((facet:(urn:urn%3Ali%3AadTargetingFacet%3AinterfaceLocales,name:Profile%20language),segments:List((urn:urn%3Ali%3Alocale%3Ade_DE,name:German,facetUrn:urn%3Ali%3AadTargetingFacet%3AinterfaceLocales))))))),exclude:(or:List()))&withValidation=true',
)

# Execute to get the result
def get_response(testCriteria):
    response = requests.post(
        'https://www.linkedin.com/campaign-manager-api/campaignManagerAudienceCounts',
        headers=headers,
        data=testCriteria
    )
    return response

# Functions accepts string, delimiter and nth occurence of the delimiter where string is split up.
def split_at(s, delim, n):
    r = s.split(delim, n)[n]
    return s[:-len(r)-len(delim)], r

# Extracts only the count from the returned response string
def parse_response(response_string):
    print("RESPONSE STRING")
    print(response_string)
    print("****")
    print("****")
    temp_str_1 = split_at(response_string, ',', 1)[0]
    temp_str_2 = split_at(temp_str_1, ':', 2)[1][:-2]
    return int(temp_str_2) # convert to number

# Accepts the query built by userand calls appropriate functions
def getCount(testCriteria):
    return parse_response(get_response(testCriteria).text)
