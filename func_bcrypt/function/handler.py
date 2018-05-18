import json
import bcrypt

def handle(req):
    myjson = json.loads(req)
    action = myjson["action"]

    if action=="generate":
        try:
            if "password" in myjson:
                hashed = bcrypt.hashpw(myjson["password"].encode('utf-8'), bcrypt.gensalt())
                print(hashed.decode())
            else:
                raise ValueError("No password provided")
        except:
            raise ValueError("Could not generate hash from provided inputs.")
    
    elif action=="validate":
        try:
            if ("password" in myjson) and ("hashed" in myjson):
                if bcrypt.checkpw(myjson["password"].encode('utf-8'), myjson["hashed"].encode('utf-8')):
                    print("true")
                else:
                    print("false")
            else:
                raise ValueError("No password provided")
        except:
            raise ValueError("Could not compare provided inputs.")
    
    #if neither generate nor validate requested, raise an error
    else:
        raise ValueError("No supported action requested")