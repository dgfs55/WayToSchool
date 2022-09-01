from flask import Flask, render_template, request
from pymongo import MongoClient
import psycopg2
import pickle


def create_app():
    
    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    def say():
        conn, cur = con_postgres()
        cur.execute("""SELECT name FROM locationschool""")
        school_name= []
        for school in cur.fetchall():
            school_name.append(school[0])

        cur.execute("SELECT DISTINCT address FROM locationschool ORDER BY address asc ")
        region_list=[]
        for region in cur.fetchall():
            region_list.append(region[0])
        return render_template('./frontend/mainpage.html', list=school_name, region_list=region_list)

    @app.route('/button', methods=['POST','GET'])
    def map():
        #모델 정보 받아오기
        with open('./model.pkl', 'rb') as f:
            model = pickle.load(f)

        #셀렉트박스 입력값 받아오기
        region = request.args.get('region')
        school_name=request.args.get('school_name')
        
        #postgres에서 입력값에 따른 학교 좌표값 받아오기
        conn, cur = con_postgres()
        cur.execute(f"SELECT lo_crd, la_crd FROM locationschool WHERE address = '{region}' and name = '{school_name}'")
        loc_list=cur.fetchall()
        lo,la = loc_list[0]

        #postgres에서 사고지역 데이터 가져오기
        cur.execute(f"SELECT occrrnc_cnt, spot_nm, lo_crd, la_crd FROM child union all select occrrnc_cnt, spot_nm, lo_crd, la_crd from schoolzone")
        occ_list=cur.fetchall()
        occurs=[]
        for item in occ_list:
            occurs.append(item)

        #mongodb에서 각 위험지역의 폴리곤 받아오기
        client= MongoClient('mongodb+srv://yh:qwe123@cluster0.xosdg.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
        db= client['myFirstDatabase']
        col= db['child']
        list_coordinates= []
        for datum in col.find():
            list_coordinates.append(datum['coordinates'])
        
        #학교 좌표값에 따라 예측값 출력하기
        cor_list=[[la, lo]]
        label= model.predict(cor_list)[0]
        return render_template('./frontend/mappage.html',list_coordinates=list_coordinates, lo=lo, la=la, label=label, occurs=occurs)

    def con_postgres():
        conn= psycopg2.connect(dbname='dbdoegm1itfp25', user= 'ksbewbdhgntrmc', password='95f0e4c33dc115465fbde72763945efb0c49108df71f0299773c1b05e6226eb2',\
            host='ec2-54-204-128-96.compute-1.amazonaws.com')
        cur= conn.cursor()
        return conn, cur

    return app