from urllib import request
from venv import create
import csv
import psycopg2
from pymongo import MongoClient
import json

DATA_URL= 'http://taas.koroad.or.kr/data/rest/frequentzone/child'

def create_table():
    #postgresql
    conn= psycopg2.connect(dbname="child", user="postgres", password= "qpwoeiruty12")
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS child")
    cur.execute(f"DROP TABLE IF EXISTS schoolzone")
    cur.execute(f"DROP TABLE IF EXISTS locationschool")
    cur.execute(f"""CREATE TABLE IF NOT EXISTS child(
                    id INTEGER NOT NULL PRIMARY KEY,
                    afos_fid integer,
                    afos_id integer,
                    bjd_cd bigint,
                    spot_cd bigint,
                    sido_sgg_nm VARCHAR(128),
                    spot_nm VARCHAR(128),
                    occrrnc_cnt integer,
                    caslt_cnt integer,
                    dth_dnv_cnt integer,
                    se_dnv_cnt integer,
                    sl_dnv_cnt integer,
                    wnd_dnv_cnt integer,
                    lo_crd FLOAT,
                    la_crd FLOAT
                    );""")
    cur.execute(f"""CREATE TABLE IF NOT EXISTS schoolzone(
                    id INTEGER NOT NULL PRIMARY KEY,
                    afos_fid integer,
                    afos_id integer,
                    bjd_cd bigint,
                    spot_cd integer,
                    sido_sgg_nm VARCHAR(128),
                    spot_nm VARCHAR(128),
                    occrrnc_cnt INTEGER,
                    caslt_cnt integer,
                    dth_dnv_cnt integer,
                    se_dnv_cnt integer,
                    sl_dnv_cnt integer,
                    wnd_dnv_cnt integer,
                    lo_crd FLOAT,
                    la_crd FLOAT
                    );""")

    cur.execute(f"""CREATE TABLE IF NOT EXISTS locationschool(
                    id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR(128),
                    class VARCHAR(128),
                    address VARCHAR(128),
                    lo_crd FLOAT,
                    la_crd FLOAT
                );""")
    conn.commit()

    #mongoDB
    client= MongoClient('mongodb+srv://yh:qwe123@cluster0.xosdg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
    db= client['myFirstDatabase']
    col = db['child']

    col.delete_many({})
    return conn, cur, col

def insert_data(conn, cur, name, path, col):
    id = 1
    with open(path) as f:
        contents = csv.DictReader(f)
        for row in contents:
            #postgresql
            cur.execute(f"""INSERT INTO {name}
            VALUES ({id}, {row['사고다발지FID']}, {row['사고다발지ID']}, {row['법정동코드']}, {row['지점코드']}, '{row['시도시군구명']}', '{row['지점명']}', {row['발생건수']}, {row['사상자수']}, {row['사망자수']}, {row['중상자수']}, {row['경상자수']}, {row['부상신고자수']}, {row['경도']}, {row['위도']});""")     
            id += 1

            #MongoDB
            col.insert_one(json.loads(row['다발지역폴리곤']))
            

    conn.commit()

def insert_location_data(conn, cur):
    id= 1
    with open('./school_location.csv') as c:
        contents= csv.DictReader(c)
        for row in contents:
            
            row['소재지도로명주소'] = row['소재지도로명주소'].split(' ')[0]
            
            if row['소재지도로명주소'] == '경기':
                row['소재지도로명주소'] = '경기도'
            if row['소재지도로명주소'] == '대전':
                row['소재지도로명주소'] = '대전광역시'
            
            cur.execute(f"""INSERT INTO locationschool
            VALUES ({id}, '{row['학교명']}', '{row['학교급구분']}', '{row['소재지도로명주소']}', {float(row['위도'])}, {float(row['경도'])} );
            """)
            id += 1
    conn.commit()

#csv데이터 불러오기
child_path = './12_20_child.csv'
schoolzone_path = './12_20_schoolzone.csv'
conn, cur, col = create_table()
insert_data(conn,cur,'child', child_path, col)
insert_data(conn, cur, 'schoolzone', schoolzone_path, col)
insert_location_data(conn,cur)

