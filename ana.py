#encoding: utf8

import urllib2
import json
import school_enum


def fetch_schools_id():
    json.loads(open("data").read())
    print json.dumps(school_enum.schools_id_name_in_province, indent=3)

    for name, data in school_enum.schools_id_name_in_province.items():
        if data.find("<school>") < 0:
            print name.encode("utf8")

    for name, url_name in school_enum.province_names.items():
        print name
        if name.decode("utf8") in school_enum.schools_id_name_in_province:
            print "skip"
            continue

        try:
            print "fetch"
            url = urllib2.urlopen("http://gkcx.eol.cn/htm/schoolBy_%s.xml" % url_name)
            school_enum.schools_id_name_in_province[name] = url.read()
        except Exception, e:
            print e
            print name, url_name

    open("data", "w").write(json.dumps(school_enum.schools_id_name_in_province, indent=3))


# http://gkcx.eol.cn/schoolhtm/scores/provinceScores121_10021_10035_10036.xml

def fetch_schools_score():
    schools_data = []
    for prov_name, data in school_enum.schools_id_name_in_province.items():
        for school_id, school in data:
            if school.find("大学") < 0:
                continue
            if school.find("学院") > 0:
                continue

            schools_data += [(school_id, school, prov_name)]

    schools_data.sort(key=lambda x:x[0])

    school_enum.schools_score_data_from_province = json.loads(open("data").read())
    # print json.dumps(data.schools_id_name_in_province, indent=3)

    # for name, data in school_enum.schools_id_name_in_province.items():
    #     if data.find("<school>") < 0:
    #         print name.encode("utf8")
    count = 0
    for province_name in school_enum.province_names.keys():
        province_name = "湖北"
        print province_name
        province_name_utf8 = province_name
        province_name = province_name.decode("utf8")
        if province_name not in school_enum.schools_score_data_from_province:
            school_enum.schools_score_data_from_province[province_name] = {}

        schools_from_prov = school_enum.schools_score_data_from_province[province_name]
        for school_id, sch_name, sch_prov in schools_data:
            print sch_name

            sch_name = sch_name.decode("utf8")
            score_data = schools_from_prov.get(sch_name, None)
            if score_data is not None and score_data.find("<score>") >= 0:
                print "skip"
                continue

            try:
                print "fetch"
                province_id = school_enum.provinces_id[province_name_utf8]
                score_url = "http://gkcx.eol.cn/schoolhtm/scores/provinceScores%s_%s_10035_10036.xml" % (
                    school_id, province_id)
                print "score_url", score_url
                url = urllib2.urlopen(score_url)
                schools_from_prov[sch_name] = url.read()
                count += 1
                if count >= 10:
                    open("data", "w").write(json.dumps(school_enum.schools_score_data_from_province, indent=3))
                    count = 0

            except Exception, e:
                print "error:", e
                print province_name

        break

    open("data", "w").write(json.dumps(school_enum.schools_score_data_from_province, indent=3))


#fetch_schools_score()


province_name = "湖北"
schools_from_prov = school_enum.schools_score_data_from_province[province_name]

data_rank = []
data_avgs = []
data_name = []
for school_name, score in schools_from_prov.items():
    tip = False
    if score == "": continue
    if len(score) < 7: continue
    if school_name in school_enum.schools_211: continue
    if school_name in school_enum.schools_985: continue

    score.sort(key=lambda x:x[2])
    score.reverse()
    for year, maxs, avgs, mins, diff, class_name, num, rank in score:
        #print year, rank, avg
        year = "%x" % (year - 2000)

        if not tip:
            tip_text = str(rank)
            tip_text = year +" "+ school_name.decode("utf8")
            tip = True
        else:
            tip_text = year
        if avgs > 0 and rank > 0 and rank < 300:
            data_rank += [50*(300 - rank)+ 500]
            data_avgs += [avgs]
            data_name += [tip_text]

import numpy as np

import matplotlib
matplotlib.use("pgf")
pgf_with_custom_preamble = {
    "font.size": 20,
    "pgf.rcfonts": False,
    "text.usetex": True,
    "pgf.preamble": [
        # math setup:
        r"\usepackage{unicode-math}",

        # fonts setup:
        r"\setmainfont{WenQuanYi Zen Hei}",
        r"\setsansfont{WenQuanYi Zen Hei}",
        r"\setmonofont{WenQuanYi Zen Hei Mono}",
    ],
}
matplotlib.rcParams.update(pgf_with_custom_preamble)

import matplotlib.pyplot as plt

#from matplotlib.font_manager import FontProperties
#ChineseFont1 = FontProperties("WenQuanYi Zen Hei")

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)

ax1.set_title(u'全国各个大学在湖北录取分数')
ax1.set_ylabel(u'大学人气排名')
ax1.set_xlabel(u'录取平均分')

ax1.plot(data_avgs, data_rank, ".")
#ax1.scatter(data_rank, data_avgs)

# ax.scatter(z, y)
for i, txt in enumerate(data_name):
    ax1.annotate(txt, (data_avgs[i], data_rank[i])) # , fontproperties = ChineseFont1


# def onpick3(event):
#     thisline = event.artist
#     xdata = thisline.get_xdata()
#     ydata = thisline.get_ydata()
#     ind = event.ind
#     print 'onpick points:', zip(xdata[ind], ydata[ind])
# fig1.canvas.mpl_connect('pick_event', onpick3)

# In the latest release, it is no longer necessary to do anything
# special to share axes across figures:

# ax1.sharex_foreign(ax2)
# ax2.sharex_foreign(ax1)

# ax1.sharey_foreign(ax2)
# ax2.sharey_foreign(ax1)

#plt.show()


fig1.set_size_inches(30, 40)
fig1.savefig("school.png", dpi=160)
