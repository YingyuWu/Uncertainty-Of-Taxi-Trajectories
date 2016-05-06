import psycopg2
import sys
import json

def da2str(a):
    s = a.__str__()
    return s.replace('[','{').replace(']','}')

def traveltime_from_one_point(cur):
    # 04/25/2016
    data = None
    with open('dataBaseTemp.txt','r') as infile:
        data = json.load(infile)
    count = 0
    for key,value in data.items():
        print count
        count += 1
        query = "INSERT INTO TravelTime VALUES(%i,'%s')" % (int(key),da2str(value))
        cur.execute(query)

def create_speed_table(cur):
    #cur.execute("Drop table if exists speed;")
    query = "Create Table speed("
    for day in range(0,31):
        for time in range(0,24):
            query += "day%i_hour%i float[]," % (day,time)
    query = query[0:-1]
    query += ");"
    print query
    cur.execute(query)
        
        
def main():
    con = None
    try:
        con = psycopg2.connect(host='127.0.0.1',port=5432,database='poi', user='postgres', password='qwe') 
        cur = con.cursor()
        
        con.commit()

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)
    
    finally:
        if con:
            con.close()
        
if __name__ == "__main__":
    main()
    
    
    