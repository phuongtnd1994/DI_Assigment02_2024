from dbconnect.pg_cnt import PGSQLConnect
import json
import traceback

pgc = PGSQLConnect()
json_file_path = "./etl.json"

insert_query = """
INSERT INTO products (prd_name, prd_price, prd_link, prd_domain, prd_src) 
VALUES (%s, %s, %s, %s, %s)
"""

if __name__ == "__main__":
    print("hello")

    cnn = pgc.connect()
    cur = cnn.cursor()

    with open(json_file_path, 'r', encoding='utf-8') as file:
        etlConfig = json.load(file)
    
    print(etlConfig)

    for inputSrc in etlConfig["InputData"]:
        with open(inputSrc["srcFile"],'r', encoding='utf-8') as file:
            loadedFile = json.load(file)
            data = loadedFile["data"]
            
            for dt in data:
                try:
                    insertData = {}
                    for m in inputSrc['mapping']:
                        insertData[m['DstField']] = m['DefaultValue']
                        if dt.get(m["SrcField"]) is not None:
                            insertData[m['DstField']] = dt.get(m["SrcField"]) 

                    values = (
                        insertData["prd_name"],
                        insertData["prd_price"],
                        insertData["prd_link"],
                        insertData["prd_domain"],
                        insertData["prd_src"]
                    )
                    cur.execute(insert_query, values)
                    cnn.commit()
                except:
                    traceback.print_exc()

        # print(data)

    cur.close()
    cnn.close()
        


