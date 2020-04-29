'''
可视化相关
'''

from pyecharts.charts import Sunburst
from pyecharts.options import InitOpts, AnimationOpts, SunburstItem
from pyecharts import options as opts
from pyecharts.globals import RenderType
import sqlite3
import random


def randomcolor():
    colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    color = ""
    for _ in range(6):
        color += colorArr[random.randint(0,14)]
    return "#"+color


if __name__ == "__main__":
    myAni = AnimationOpts(animation=True,  # 开启动画
                        animation_threshold=2000,  # 开启动画的阈值 
                        animation_duration=1000,  # 初始动画的时长
                        animation_easing="cubicOut",  # 初始动画的缓动效果
                        animation_delay=0,  # 初始动画的延迟
                        animation_duration_update=300,  # 数据更新动画的时长
                        animation_easing_update="cubicOut", # 数据更新动画的缓动效果
                        animation_delay_update=300)   # 数据更新动画的延迟

    myOpts = InitOpts(width="1600px", 
                    height="800px", 
                    chart_id="myfirstchart", 
                    renderer=RenderType.CANVAS,
                    page_title="firstchart",
                    theme="white",
                    bg_color=None,
                    animation_opts=myAni)

    mysunburst = Sunburst(init_opts=myOpts)

    conn = sqlite3.connect('pdftables.sqlite')
    cur = conn.cursor()

    c = cur.execute("select * from company_info")
    companyinfo = c.fetchone()
    charttitle = companyinfo[1]
    units = companyinfo[2]

    c = cur.execute("select bank, credit, used from credit_info where company = '%d'" % companyinfo[0])
    creditinfo = c.fetchall()
    conn.close()
    myitemlist = []
    for each in creditinfo:
        sunburstitem = SunburstItem(
            name=each[0], 
            value=each[1],  
            itemstyle_opts={"color":randomcolor()}, 
            children=[
                        SunburstItem(name="已用", value=each[2], itemstyle_opts={"color":randomcolor()}),
                        SunburstItem(name="未用", value=(each[1]-each[2]), itemstyle_opts={"color":randomcolor()})
            ]
        )
        myitemlist.append(sunburstitem)
    mysunburst.add(
                    "",
                    myitemlist, 
                    radius=[0, "95%"],
                    highlight_policy="ancestor",
                    sort_="null",
                    levels=[
                        {},
                        {
                            "r0": "15%",
                            "r": "76%",
                            "itemStyle": {"borderWidth": 2},
                            "label": {"rotate": "radial"},
                        },
                        {
                            "r0": "76%", 
                            "r": "80%", 
                            "label": {"align": "right","position": "outside","silent": False},
                            "itemStyle": {"borderWidth": 3},
                        },
                    ]
    )
    mysunburst.set_global_opts(title_opts=opts.TitleOpts(title=charttitle, subtitle="[单位：%s]" % units))
    mysunburst.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
    mysunburst.render("view.html")