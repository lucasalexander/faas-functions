import subprocess
import base64
import json
import sys
import urllib3
urllib3.disable_warnings()

inputpdfpath = "/tmp/myinput.pdf"
unlockedpdfpath = "/tmp/myunlocked.pdf"
outputpdfpath = "/tmp/myoutput.pdf"
fdfpath = "/tmp/mymap.fdf"

def generatefdf(fieldarray):
    fdfheader = '''%FDF-1.2
1 0 obj 
<</FDF 
<</Fields ['''
    fieldvalues = ""
    for d in fieldarray:
        fieldvalue = "<</T (%s) /V (%s) >>" % (d["name"],d["value"])
        fieldvalues = fieldvalues + "\n" + fieldvalue
    fdffooter = ''']>>
>>
endobj 
trailer

<</Root 1 0 R>>
%%EOF'''
    fdf = fdfheader + "\n" + fieldvalues + "\n" + fdffooter
    return fdf.strip()

def handle(req):
    myjson = json.loads(req)

    action = myjson["action"]

    #if there's a pdfurl in the json, download the pdf from there
    if 'pdfurl' in myjson:
        chunk_size = 1024
        http = urllib3.PoolManager()
        r = http.request('GET', myjson["pdfurl"], preload_content=False)
        with open(inputpdfpath, 'wb') as out:
            while True:
                data = r.read(chunk_size)
                if not data:
                    break
                out.write(data)

    #otherwise look for pdfdata in b64 format in request
    elif 'pdfdata' in myjson:
        with open(inputpdfpath, "wb") as fh:
            fh.write(base64.b64decode(myjson["pdfdata"]))
    
    #otherwise raise an error
    else:
        raise ValueError("Could not get PDF from URL or provided b64 data.")
    
    #proactively decrypt pdf to avoid "OWNER PASSWORD REQUIRED, but not given (or incorrect)" errors
    try:
        args = "/usr/bin/qpdf --decrypt " + inputpdfpath + " " + unlockedpdfpath
        output = subprocess.check_output(
            args.split(),
            stderr=subprocess.STDOUT,
            shell=False)
        print(output.decode('ascii'))
    except subprocess.CalledProcessError as e:
        raise ValueError("Could not apply proactive decryption: " + e.output)
    
    #if user requests a dump of form fields, just return them as raw text
    if action=="dumpfields":
        args = "/usr/bin/pdftk " + unlockedpdfpath + " dump_data_fields"
        try:
            output = subprocess.check_output(
                args.split(),
                stderr=subprocess.STDOUT,
                shell=False)
            print(output.decode('ascii'))
        except subprocess.CalledProcessError as e:
            raise ValueError("Could not dump data fields: " + e.output)
    
    #if user requests to render a form
    elif action=="render":
        #generate the fdf file
        fdffile=open(fdfpath, "w")
        fdffile.write(generatefdf(myjson["fields"]))
        fdffile.close()

        #build the argument string for the fill_form operation
        argstring = "/usr/bin/pdftk " + unlockedpdfpath + " fill_form " + fdfpath + " output " + outputpdfpath

        #if params include flatten=true, add the "flatten" flag to the argument string
        if myjson["flatten"] == True:
            argstring = argstring + " flatten"
        
        try:
            #run pdftk
            output = subprocess.check_output(
                argstring.split(),
                stderr=subprocess.STDOUT,
                shell=False)

            #write binary pdf output
            if myjson["output"] == "pdf":
                with open(outputpdfpath,"rb") as pdf:
                    sys.stdout.buffer.write(pdf.read())
            
            #write b64 output
            if myjson["output"] == "b64":
                with open(outputpdfpath, "rb") as pdf:
                    encoded = base64.b64encode(pdf.read())
                    data = {}
                    data['pdfdata'] = encoded.decode('ascii')
                    json_output = json.dumps(data)
                    print(json_output)
        
        except subprocess.CalledProcessError as e:
            raise ValueError("Could complete form and generate output: " + e.output)        
    
    #if neither dumpfields nor render requested, raise an error
    else:
        raise ValueError("No supported action requested")