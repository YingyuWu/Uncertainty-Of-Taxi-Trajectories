import psycopg2
import sys
import json

def da2str(a):
    s = a.__str__()
    return s.replace('[','{').replace(']','}')
    
        
def main():
    con = None
    try:
        con = psycopg2.connect(host='127.0.0.1',port=5432,database='poi', user='postgres', password='qwe') 
        cur = con.cursor()
        data = None
        with open('dataBaseTemp.txt','r') as infile:
            data = json.load(infile)
        count = 0
        for key,value in data.items():
            print count
            count += 1
            query = "INSERT INTO TravelTime VALUES(%i,'%s')" % (int(key),da2str(value))
            cur.execute(query)
        con.commit()

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)
    
    finally:
        if con:
            con.close()
        
if __name__ == "__main__":
    main()