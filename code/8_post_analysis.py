#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 17:49:14 2023

@author: xintao
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import jellyfish
from collections import Counter
import re
biden_final = pd.read_csv('Biden_final.csv', index_col=0)
trump_final = pd.read_csv('Trump_final.csv', index_col=0)
obama_final = pd.read_csv('Obama_final.csv', index_col=0)


def post_analysis(df):
    names = list(df.Lastnames)
    names.append('Obama')
    for j in range(len(names)):
        names[j] = str(names[j]).strip()

    topics = []
    for top in df.Topics:
        if type(top) != float:
            topics = topics + list(top.split(';;')[1:])
    topics = list(set(topics))

    orgs = []
    for org in df.Orgs:
        if type(org) != float:
            orgs = orgs + list(org.split(';;')[1:])
    orgs = list(set(orgs))

    countries = []
    for c in df.Countries_inv.fillna(''):
        cc = c.split(';;')[1:]
        cc = ['Domestic' if x == 'United States' else x for x in cc]
        countries = countries + cc
    countries = list(set(countries))

    maxs = datetime.strptime(max(df.Dates), '%Y-%m-%d') + timedelta(days=1)
    mins = datetime.strptime(min(df.Dates), '%Y-%m-%d') - timedelta(days=1)
    indt = list(pd.date_range(mins, maxs))

    box = np.empty((len(indt), len(names)), dtype='<U400')
    box2 = np.empty((len(indt), len(countries)), dtype='<U400')
    box3 = np.empty((len(countries), len(names)))
    box4 = np.empty((len(countries), len(topics)))
    box5 = np.empty((len(names), len(topics)))
    box6 = np.empty((len(countries), len(orgs)))
    box7 = np.empty((len(names), len(orgs)))
    box8 = np.empty((len(indt), len(countries)))
    box8[:] = None


    df = df[df.Meet_kind == 1]
    for i in df.index:
        bdate = datetime.strptime(df.Dates[i], '%Y-%m-%d') + timedelta(days=1)
        edate = datetime.strptime(df.Dates[i], '%Y-%m-%d') - timedelta(days=1)
        ns = [df.Lastnames[i]]
        nss = df.Lastnames[i]
        if isinstance(df.Accompanies[i], float):
            ns = ns
        else:
            ns = ns + list(df.Accompanies[i].split(';;')[1:-1])
            nss = nss + df.Accompanies[i]
        locs = df.Countries_inv[i]
        locsl = locs.split(';;')[1:]
        # ranks = []
        # for n in ns:
        #     box[indt.index(bdate):indt.index(edate), names.index(n)] = locs
        #     if n != 'Obama':
        #         rank = df.Rank[df.Lastnames == n].iloc[0]
        #         ranks.append(6 - rank)
        #     else:
        #         ranks.append(1)
        ranks = []
        for n in ns:
            box[indt.index(bdate):indt.index(edate), names.index(n)] = locs
            if n != 'Obama':
                rank = df.Rank[df.Lastnames == n]
                if not rank.empty:
                    ranks.append(6 - rank.iloc[0])
            else:
                ranks.append(1)

            for l in locsl:
                if l == 'United States':
                    l = 'Domestic'
                box3[countries.index(l), names.index(n)] = box3[countries.index(l), names.index(n)] + (edate - bdate).days
        ranks = max(ranks)
        for l in locsl:
            if l == 'United States':
                l = 'Domestic'
            box2[indt.index(bdate):indt.index(edate), countries.index(l)] = nss
            box8[indt.index(bdate):indt.index(edate), countries.index(l)] = ranks
        tps = df.Topics[i]
        if type(tps) != float:
            tps = tps.split(';;')[1:]
            for tp in tps:
                for l in locsl:
                    if l == 'United States':
                        l = 'Domestic'
                    box4[countries.index(l), topics.index(tp)] = box4[countries.index(l), topics.index(tp)] + 1
                for n in ns:
                    box5[names.index(n), topics.index(tp)] = box5[names.index(n), topics.index(tp)] + 1
        og = df.Orgs[i]
        if type(og) != float:
            og = og.split(';;')[1:]
            for g in og:
                for l in locsl:
                    if l == 'United States':
                        l = 'Domestic'
                    box6[countries.index(l), orgs.index(g)] = box6[countries.index(l), orgs.index(g)] + 1
                for n in ns:
                    box7[names.index(n), orgs.index(g)] = box7[names.index(n), orgs.index(g)] + 1

    iDcN = pd.DataFrame(box, index=indt, columns=names)
    iDcC = pd.DataFrame(box2, index=indt, columns=countries)
    iDcR = pd.DataFrame(box8, index=indt, columns=countries)
    iCcN = pd.DataFrame(box3, index=countries, columns=names)
    iCcT = pd.DataFrame(box4, index=countries, columns=topics)
    iNcT = pd.DataFrame(box5, index=names, columns=topics)
    iCcO = pd.DataFrame(box6, index=countries, columns=orgs)
    iNcO = pd.DataFrame(box7, index=names, columns=orgs)

    iDcN.to_excel('travels_index_DATE_columns_Names_cell_Countries.xlsx')
    iDcC.to_excel('travels_index_DATE_columns_Countries_cell_Names.xlsx')
    iDcR.to_excel('travels_index_DATE_columns_Countries_cell_Ranks.xlsx')
    iCcN.to_excel('travels_index_Countries_columns_Names_cell_Days.xlsx')
    iCcT.to_excel('travels_index_Countries_columns_Topics_cell_Counts.xlsx')
    iNcT.to_excel('travels_index_Names_columns_Topics_cell_Counts.xlsx')
    iCcO.to_excel('travels_index_Countries_columns_Orgs_cell_Counts.xlsx')
    iNcO.to_excel('travels_index_Names_columns_Orgs_cell_Counts.xlsx')

post_analysis(trump_final)







def make_post_analysis():
    b=when_who_where(biden_final)
    b.to_csv('Biden_INDDate_COLDip_CELLCountries.csv')
    b.to_csv('whos_where_biden.csv')
    t=when_who_where(trump_final)
    t.to_csv('Trump_INDDate_COLDip_CELLCountries.csv')
    t.to_csv('whos_where_trump.csv')
    o=when_who_where(obama_final)
    o.to_csv('Obama_INDDate_COLDip_CELLCountries.csv')
    o.to_csv('whos_where_obama.csv')

    b=when_where_who(biden_final)
    b.to_csv('Biden_INDCountry_COLDate_CELLVisit.csv')
    t=when_where_who(trump_final)
    t.to_csv('Trump_INDCountry_COLDate_CELLVisit.csv')
    o=when_where_who(obama_final)
    o.to_csv('Obama_INDCountry_COLDate_CELLVisit.csv')

    b=who_where(biden_final)
    b.to_csv('Biden_INDCountries_COLDip.csv')
    t=who_where(trump_final)
    t.to_csv('Trump_INDCountries_COLDip.csv')
    o=who_where(obama_final)
    o.to_csv('Obama_INDCountries_COLDip.csv')

    b=countries_topics('biden')
    b.to_csv('Biden_Meetings_Countries_Topics.csv')
    t=countries_topics('trump')
    t.to_csv('Trump_Meetings_Countries_Topics.csv')
    o=countries_topics('obama')
    o.to_csv('Obama_Meetings_Countries_Topics.csv')
    
    b=meet_countries(biden_final,'biden')
    b.to_csv('Biden_Meetings.csv')
    t=meet_countries(trump_final,'trump')
    t.to_csv('Trump_Meetings.csv')
    o=meet_countries(obama_final,'trump')
    o.to_csv('Obama_Meetings.csv')


def when_who_where(df):
    'returns a df with countries as indexes and date as columns, diplomats in each cell'
    dff = pd.DataFrame(df.Dates)
    dff.index = pd.DatetimeIndex(df.Dates)
    dff = dff.sort_index()
    maxs = datetime.strptime(dff.Dates.iloc[-1], "%Y-%m-%d") + timedelta(days=10)
    mins = datetime.strptime(dff.Dates.iloc[0], "%Y-%m-%d") - timedelta(days=10)
    indt = pd.date_range(mins, maxs)
    ind = []
    for i in indt:
        ind.append(str(i.date()))
    names = list(set(df.Lastnames))
    df = df[df.Travel_kind == 1]
    Box = pd.DataFrame(np.arange(len(ind)), index=ind, columns=['dels'])
    for name in names:
        wheres = [None]*len(ind)
        ndf = df[df.Lastnames == name]
        for i in range(len(ndf)):
            b = ndf.Travel_Beg.iloc[i]
            e = ndf.Travel_End.iloc[i]
            loc = ndf.Countries_inv.iloc[i]
            if loc == 0:
                loc = None
            beg = Box.loc[b][0]
            end = Box.loc[e][0]+1
            wheres[int(beg):int(end)] = [loc]*(int(end)-int(beg))
        Box[name] = wheres
    return Box.iloc[:, 1:]


def when_where_who(df):
    'returns a df with date as indexs and diplomats as columns, visit countries in each cell.'
    
    dff=pd.DataFrame(df.Dates)
    dff.index=pd.DatetimeIndex(df.Dates)

    dff=dff.sort_index()
    
    maxs=datetime.strptime(dff.Dates.iloc[-1],"%d-%b-%y")+timedelta(days=10)
    mins=datetime.strptime(dff.Dates.iloc[0],"%d-%b-%y")-timedelta(days=10)
    indt=pd.date_range(mins,maxs)
    ind=[]
    for i in indt:
        ind.append(str(i.date()))

    names=list(set(df.Lastnames))
    df=df[df.Travel_kind==1]
    cs=[]
    for c in df.Countries_inv:
        cs=list(cs)+list(c.split(';;')[1:])
    cs=list(set(cs))
    
    box=np.zeros([len(cs),len(ind)],dtype='<U30')
    box[:]='Na'
    
    
    for name in names:
        wheres=[None]*len(ind)
        ndf=df[df.Lastnames==name]
        for i in range(len(ndf)):
            b=str(ndf.Travel_Beg.iloc[i])
            e=str(ndf.Travel_End.iloc[i])
            b=ind.index(b)
            e=ind.index(e)+1
            locs=ndf.Countries_inv.iloc[i]
            if locs==0:
                locs=None
            locs=locs.split(';;')[1:]
            
            for loc in locs:
                l=cs.index(loc)
                for sd in range(b,e):
                    box[l,sd]=name
                
    Box=pd.DataFrame(box,index=cs,columns=ind)
    Box=Box.replace(['Na'],None)
                
    return Box


def who_where(df):
    
    'returns a df with countries as indexs and diplomats as columns, visit frequencies in each cell.'
    cc=when_where_who(df)
    cc2=when_who_where(df)
    countries=list(cc.index)
    names=list(cc2.columns)
    
    
    box=np.zeros([len(cc.index),len(cc2.columns)])
    ndf=df[df.Travel_kind==1]
    for i in range(len(ndf)):
            i=ndf.index[i]
            name=ndf.Lastnames[i]
            n=names.index(name)
            conts=ndf.Countries_inv[i].split(';;')[1:]
            for cont in conts:
                c=countries.index(cont)
                box[c,n]=box[c,n]+1
    box=pd.DataFrame(box,index=cc.index,columns=cc2.columns)
  
    return box
    

def meet_countries(df,case):
    wwt = pd.read_csv('whos_where_trump.csv', index_col=0)
    wwb = pd.read_csv('whos_where_biden.csv', index_col=0)
    wwo = pd.read_csv('whos_where_obama.csv', index_col=0)
    if case == 'trump':
        ww = wwt
    if case == 'biden':
        ww = wwb
    if case == 'obama':
        ww = wwo

    df = df[df.Meet_kind == 1]
    DATE=[]
    DIPT=[]
    MeetPlaces=[]
    CONTS=[]
    TYPEs=[]
    PARTS=[]
    TEXT=[]
    VIRTUAL=[]
    ORGS=[]
    TOPS=[]
    
    for i in df.index:
        count_inv=df.Countries_inv[i]
        date=datetime.strptime(df.Dates[i],"%d-%b-%y").date()
        DATE.append(date)
        name1=df.Lastnames[i]
        
        name=[name1]
        if df.Accompanies[i]!='0' and name1!=df.Accompanies[i]:
            name=list(name)+list([df.Accompanies[i]])
        DIPT.append(name)
        date=str(date)
        try: 
            places=ww.loc[date][name1]
            if places!=None:
                if 'Domestic' not in places and 'United States' not in places:
                    if count_inv[2:] in places:
                        MeetPlaces.append(count_inv.replace(';;United States',''))
                    else:
                        MeetPlaces.append(places.replace(';;United States',''))
                    
                else:
                    MeetPlaces.append(';;Domestic')
       
        except:MeetPlaces.append(';;Domestic')
        
        count=count_inv.replace(';;United States','')
        if len(count)>0:
            CONTS.append(count)
        else:
            CONTS.append(';;Domestic')
            
        tt=str(df.Texts[i])+';;;;'+str(df.content[i])
        tt=tt.replace(';;;;nan','')
        TEXT.append(tt)
        
    for i in range(len(MeetPlaces)):
        m=MeetPlaces[i].split(';;'[1:])
        c=CONTS[i].split(';;'[1:])
        inter=intersection(m, c)
        for c in range(inter.count('')):
            inter.remove('')
        if len(inter)>0 and 'Domestic' not in inter:
            p=''
            for intt in inter:
                
                p=p+';;'+str(intt)
            MeetPlaces[i]=p
            
        if MeetPlaces[i].split(';;')[1:][0]=='Domestic':
            if CONTS[i].split(';;')[1:][0]=='Domestic':
                TYPEs.append('Internal')
                PARTS.append(1)
            else:
                TYPEs.append('Meet_For_Internal')
                part=len(CONTS[i].split(';;')[1:])+1
                PARTS.append(part)
        else:
            TYPEs.append('Meet_For_external')
            part=len(CONTS[i].split(';;')[1:])+1
            PARTS.append(part)
        if "virtual" in TEXT[i]:
            VIRTUAL.append(1)
        else:
            VIRTUAL.append(0)
        ogss=orgs_inv(TEXT[i])
        ORGS.append(ogss)
        to=topics_in_it(TEXT[i])
        TOPS.append(to)
        

            
                              
    box=pd.DataFrame(DIPT,index=DATE,columns=['Diplomat1','Diplomat2'])
    box['Meet_place']=MeetPlaces
    box['Count_inv']=CONTS
    box['Meet_type']=TYPEs
    box['Virtual']=VIRTUAL
    box['Parties']=PARTS
    box['Organizations']=ORGS
    box['Topics']=TOPS
    box['Texts']=TEXT
    return box
 

def countries_topics(case):
    countries = ''
    topics = ''
    if case == 'biden':
        df = pd.read_csv('Biden_Meetings.csv', index_col=0)
    if case == 'trump':
        df = pd.read_csv('Trump_Meetings.csv', index_col=0)
    if case == 'obama':
        df = pd.read_csv('Obama_Meetings.csv', index_col=0)
    for i in range(len(df.index)):
        if type(df.Topics[i]) is not float:
            topics = topics+df.Topics[i]
        countries = countries+df.Count_inv[i]
    topics = list(set(topics.split(';;')))[1:]
    countries = list(set(countries.split(';;')))[1:]
    box = np.zeros([len(countries), len(topics)])
    for i in range(len(df.index)):
        if type(df.Topics[i]) is not float:
            ts = df.Topics[i].split(';;')[1:]
        cs = df.Count_inv[i].split(';;')[1:]
        print(cs)
        if type(df.Topics[i]) is not float:
            for t in ts:
                for c in cs:
                    tt=topics.index(t)
                    cc=countries.index(c)
                    box[cc, tt] = box[cc, tt]+1
    return pd.DataFrame(box, columns=topics, index=countries)


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def orgs_inv(text):
    ogs = ''
    if 'NATO' in text:
        ogs=ogs+';;NATO'
    if ' USAID ' in text or 'U.S. Agency for International Development.' in text :
        ogs=ogs+';;USAID'  
    if ' WTO ' in text:
        ogs=ogs+';;WTO'
    if ' WHO ' in text:
        ogs=ogs+';;WHO'
    if ' UN ' in text or ' U.N. ' in text or ' United Nation'in text:
        ogs=ogs+';;UN;;'
    if 'ASEAN' in text:
        ogs=ogs+';;ASEAN' 
    if ' IMF' in text:
        ogs=ogs+';;IMF'
    if ' World Bank ' in text:
        ogs=ogs+';;World_Bank'
    if ' OPEC ' in text:
        ogs=ogs+';;OPEC'
    if ' IAEA ' in text:
        ogs=ogs+';;IAEA'  
    if 'G7' in text:
        ogs=ogs+';;G7'
    if 'G20 ' in text:
        ogs=ogs+';;G20'
    if ' UNICEF ' in text:
        ogs=ogs+';;UNICEF'
    if ' OECD ' in text:
        ogs=ogs+';;OECD'
    if ' COP' in text:
        ogs=ogs+';;COP'
    if ' Quad ' in text or ' QUAD' in text:
        ogs=ogs+';;Quad'
    if ' AUKUS ' in text or ' Aukus' in text:
        ogs=ogs+';;Aukus'   
    if " U.S. Embassy " in text:
        ogs=ogs+';;US Embassy'
    if " Pentagon " in text or ' Department of Defense' in text or ' DoD' in text:
        ogs=ogs+';;DOD(US)'   
    if " International Telecommunication Union " in text or ' ITU' in text:
        ogs=ogs+';;ITU'   
    if ' Red Cross' in text:
        ogs=ogs+';;Red Cross'
    if ' University' in text:
        ogs=ogs+';;University'  
    if ' African Union' in text:
        ogs=ogs+';;African Union'          
    if ' Mekong-U.S. Partnership' in text:
        ogs=ogs+';;Mekong-U.S. Partnership'   
    if ' C5+1' in text:
        ogs=ogs+';;C5+1'    
    if ' OSCE' in text:
        ogs=ogs+';;OSCE'                   
    if ' D-ISIS' in text:
        ogs=ogs+';;D-ISIS'      
    if ' Arctic Council' in text:
        ogs=ogs+';;Arctic Council'      
    if ' International Development Finance Corporation' in text or ' DoD' in text:
        ogs=ogs+';;IDFC'    
    if ' Technology Council' in text or ' DoD' in text:
        ogs=ogs+';;EU US Trade and Technology Council'
    return ogs


def topics_in_it(text):
    # find topics in text
    topic=''
    strategic=['arms control','strategic','security','weapons','NATO','Defense']
    aid=['food','grain',' aid ','USAID','Red Cross', 'Humanitarian', 'Relief','U.S. Agency for International Development']
    tech=['technology',' 5g ',' ict ','artificial intelligence','biotech','bio-tech']
    health=['COVID','medical',' vaccine','hygiene','sanitation']  
    econ=['economic','trade','tariff','business','commerce','commercial','economy','investment']    
    nuke=['nuclear','proliferation']
    supply_chain=['supply chain','semi-conductor']
    climate=['climate','emission',' CO2 ','carbon']
    energy=['energy',' oil ', ' petro ', ' battery ']
    finance=['banking','finance','financial']

    if any([s.lower() in text.lower() for s in strategic])==True:
        topic=topic+';;StrategicSecurity'
    if any([s.lower() in text.lower() for s in aid])==True:
        topic=topic+';;Aid'
    if any([s.lower() in text.lower() for s in tech])==True:
        topic=topic+';;Tech'
    if any([s.lower() in text.lower() for s in health])==True:
        topic=topic+';;Health'
    if any([s.lower() in text.lower() for s in econ])==True:
        topic=topic+';;Econ'
    if any([s.lower() in text.lower() for s in nuke])==True:
        topic=topic+';;Nuke'
    if any([s.lower() in text.lower() for s in supply_chain])==True:
        topic=topic+';;Supply_chain'
    if any([s.lower() in text.lower() for s in climate])==True:
        topic=topic+';;Climate'
    if any([s.lower() in text.lower() for s in energy])==True:
        topic=topic+';;Energy'
    if any([s.lower() in text.lower() for s in finance])==True:
        topic=topic+';;Finance'
    return topic



    
