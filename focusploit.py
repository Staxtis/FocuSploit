import json, requests, sys, re, os, urllib.parse


red = "\033[1;31;49m"
blue = "\033[1;34;49m"
purple = "\033[1;35;49m"
op = "\033[1;37;49m"

headers = {'Accept': 'application/json'}


def banner():
    banner = f'''{blue}
    A@@@@@@@ P@@@@@  O@@@@@@ S@@  @@@  T@@@@@ O@@@@@@  L@@     O@@@@@  S@@ @@@@@@@ 
    @@!     @@!  @@@ @@      @@!  @@@ !@@     @@!  @@@ @@!    @@!  @@@ @@!   @!!   
    @!!!::  @!@  !@! @!      @!@  !@!  !@@:!  @!@@:@!  @!!    @!@  :@! !!@   @!!   
    !!::    !!!  !!! !!      !!:  !!!     !:! !!::     !!:    !!:  !!! !!:   !!:   
    ::      :::..::: ::::::: :.::.: : ::..::: ::       :::.:: .::..::: :::   :::    
    '''.replace("!",f"{purple}!{op}").replace("@",f"{blue}@")
    
    print(banner)

resultsList = []

def search(query):
    global resultsList
    temp = 0
    # URL Encode the query
    query = urllib.parse.quote(query) 
    # Loop 10 Pages
    for PN in range(1, 10):
        response = requests.get(f'https://bugtraq-api.securityfocus.com/email/list?sortField=sent_date&sortOrder=DESC&pageNumber={PN}&pageSize=10&searchString={query}', headers=headers).json()
        # If you reached the end, stop
        if response.get('emails') == None:
            break
        # Enumerate 10 posts in every page
        for s in range(0,9):
            # Get The Subject of every post of every page.
            Subject = response.get('emails')[s]['subject']
            # If Search Term is in Result, then Highlight it 
            Subject = Subject.upper().replace((urllib.parse.unquote(query).upper()), (purple+urllib.parse.unquote(query).upper()+op))
            # Print it out
            print (f'    {blue}{s + temp + 1}{op}) {Subject}')
            # Append it to the list too
            resultsList.append("https://bugtraq-api.securityfocus.com/email?id="+response.get('emails')[s]['id'])
        # This is to count the findings correctly and not in range [0,9]
        temp = temp + s + 1
    # Write to file list
    f = open("/tmp/list.txt", "w")
    for r in range(len(resultsList)):
        f.write(resultsList[r]+"\n")
    f.close()        
        

def getBody(info, program="less"):
    # If exists, read the list
    try:
        results = open("/tmp/list.txt", "r").read().splitlines()
        if results == ['']:
            print("\n    You have to search something first!")
            sys.exit()
    except FileNotFoundError:
        print("\n    You have to search something first!")
        sys.exit()
    # Request that post
    response = requests.get(results[info-1], headers=headers).json()
    
    # Get The info
    try:
        Subject = response.get('email')[0]['subject']
    except KeyError:
        Subject = 'Null'
    try:
        Fromname = response.get('email')[0]['fromName']
    except KeyError:
        Fromname = 'Null'
    try:
        Fromemail = response.get('email')[0]['fromEmail']
    except KeyError:
        Fromemail = 'Null'
    try:
        id = response.get('email')[0]['id']
    except KeyError:
        id = 'Null'
    try:   
        # Some modifications 
        Body = response.get('email')[0]['body'].replace('&apos;', "'").replace('&quot;', '"').replace("&gt;", "").replace("&lt;", "").replace("&#x9;", "    ").replace("&nbsp;", " ")
    except KeyError:
        Body = 'Null'

    # Replace every HTML Entity (Whatever is between "<" and ">" including them)
    rep = re.findall("<[^>]*>",Body)
    for i in rep:
        Body = Body.replace(i, "\n")
    
    # Build the output of the file and prepare it to read it with "less" to start from top
    toprint = f"Subject: {Subject}\n\nFrom: {Fromname}\n\nEmail: {Fromemail}\n\n{Body}\n\nURL: https://bugtraq.securityfocus.com/detail/{id}"
    f = open("/tmp/tmp.txt", "w")
    f.write(toprint)
    f.close()
    # This is where you can choose the program to Read it with. (sys.argv[3])
    cmd = f"{program} /tmp/tmp.txt"
    os.system(cmd)


if __name__ == "__main__":
    try:
        
        if len(sys.argv) < 2:
            # Just the Banner and the Help Screen 
            banner()
            print(f"     Usage:     python3.11 {sys.argv[0]} <{purple}exploit{op}>\n     Example:   {blue}python3.11 {sys.argv[0]} filezilla{op}\n\n     Info:      python {sys.argv[0]} <{purple}exploit{op}> <{purple}index{op}>\n     Example:   {blue}python3.11 {sys.argv[0]} filezilla 2{op}\n\n     Editor:    python {sys.argv[0]} <{purple}exploit{op}> <{purple}index{op}> <{purple}program{op}>\n     Example:   {blue}python3.11 {sys.argv[0]} filezilla 2 subl{op}\n")
        
        if len(sys.argv) == 2:
            # Search Query
            banner()
            search(sys.argv[1])

        elif len(sys.argv) == 3:
            # Choose to Read
            if sys.argv[2].isnumeric():
                getBody(int(sys.argv[2]))

            else:
                print("\n    The second argument must be an integer!\n")
                sys.exit()
        
        elif len(sys.argv) == 4:
            # Choose to Read with an other Text Editor 
            getBody(int(sys.argv[2]), sys.argv[3])

    except IndexError: 
        # Export the Results even if it hits IndexError
        f = open("/tmp/list.txt", "w")
        for r in range(len(resultsList)):
            f.write(resultsList[r]+"\n")
        f.close()
  
        print(f'\n    End of Results.')
    
    except KeyboardInterrupt:
        # Export the Results even if you hit ctrl+c midsearch
        f = open("/tmp/list.txt", "w")
        for r in range(len(resultsList)):
            f.write(resultsList[r]+"\n")
        f.close()        
    except requests.exceptions.ConnectionError:
        print(f"\n    Connection error.")