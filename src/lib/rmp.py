import requests, re

q = {
    "query":"""
    query NewSearchTeachersQuery($query: TeacherSearchQuery!) {
        newSearch {
            teachers(query: $query) {
                didFallback  
                edges {      
                    cursor 
                    node {    
                        id   
                        legacyId     
                        firstName 
                        lastName     
                        school {           
                            name
                            id     
                        }          
                        department        
                    }   
                }
            }  
        }
    }
    """,
    "variables":{"query":{"text":"","schoolID":"U2Nob29sLTE0NTI="}}
}

headers = {
    "Authorization": "Basic dGVzdDp0ZXN0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Content-Type": "application/json"
}

pat = re.compile(r'<div class="RatingValue__Numerator-qw8sqy-2 liyUjw">((.|\.)*?)</div>')

uri = "https://www.ratemyprofessors.com/professor/"

def get_prof(name):

    q["variables"]["query"]["text"] = name

    r = requests.post("https://www.ratemyprofessors.com/graphql", json=q, headers=headers)

    r1 = requests.get(uri + str(r.json()["data"]["newSearch"]["teachers"]["edges"][0]["node"]["legacyId"])).text

    return pat.findall(r1)[0][0]