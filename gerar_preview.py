"""Gera visual analítico estático a partir da base CSV; não é screenshot do Power BI."""
import csv
import collections
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

root = Path(__file__).resolve().parent
rows = list(csv.DictReader((root/'data/lastmile_sintetico.csv').open(encoding='utf-8')))
total = len(rows); entregues = sum(r['entregue']=='1' for r in rows)
pontuais = sum(r['no_prazo']=='1' for r in rows)
pendentes = total-entregues
atrasos = entregues-pontuais
vencidos = sum(r['entregue']=='0' and r['data_prevista'][:10]<='2026-10-26' for r in rows)
meses=collections.defaultdict(lambda:[0,0])
tr=collections.defaultdict(lambda:[0,0,0])
for r in rows:
    if r['entregue']=='1':
        meses[r['mes_referencia']][0]+=1
        meses[r['mes_referencia']][1]+=int(r['no_prazo'])
        tr[r['transportadora']][0]+=1
        tr[r['transportadora']][1]+=int(r['no_prazo'])
    else:tr[r['transportadora']][2]+=1

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':'#CDD7E4', 'axes.labelcolor':'#28384E'})
fig=plt.figure(figsize=(16,9),facecolor='#F2F6FB')
fig.patches.append(plt.Rectangle((0,.91),1,.09, transform=fig.transFigure,facecolor='#13263E',edgecolor='none',zorder=0))
fig.text(.035,.947,'LAST-MILE  /  ANALYTICS',color='white',fontsize=24,fontweight='bold',va='center')
fig.text(.965,.947,'PRÉVIA EM PYTHON  •  NÃO É CAPTURA DO POWER BI',color='#B9CFDE',fontsize=10,ha='right',va='center')

def kpi(x,title,val,sub):
    fig.patches.append(plt.Rectangle((x,.775),.215,.11,transform=fig.transFigure,facecolor='white',edgecolor='#DDE5EF',linewidth=1,zorder=0))
    fig.text(x+.012,.85,title,color='#61748A',fontsize=12,weight='medium')
    fig.text(x+.012,.807,val,color='#13263E',fontsize=23,weight='bold')
    fig.text(x+.202,.80,sub,color='#62758A',fontsize=10,ha='right')
kpi(.035,'Total de pedidos',f'{total:,}'.replace(',','.'),'Jan–Out/2026')
kpi(.276,'Conclusão',f'{entregues/total:.2%}'.replace('.',','),f'{entregues:,}'.replace(',','.'))
kpi(.517,'Pontualidade',f'{pontuais/entregues:.2%}'.replace('.',','),'concluídas')
kpi(.758,'Pendentes vencidos',f'{vencidos:,}'.replace(',','.'),f'de {pendentes:,}'.replace(',','.'))

ax=fig.add_axes([.05,.405,.49,.29],facecolor='white')
seq=sorted(meses)
ys=[meses[m][1]/meses[m][0]*100 for m in seq]
ax.plot(range(len(seq)),ys,color='#2576D2',linewidth=3,marker='o',markersize=7)
ax.axhline(90,color='#EC9352',linestyle='--',linewidth=1.5,label='Referência visual 90%')
ax.set_title('Evolução mensal da pontualidade',loc='left',color='#13263E',fontsize=15,weight='bold',pad=15)
ax.set_xticks(range(len(seq)),[m[5:7]+'/'+m[2:4] for m in seq])
ax.set_ylabel('% das entregas concluídas')
ax.set_ylim(80,100)
ax.grid(axis='y',color='#EDF1F7')
ax.legend(frameon=False,fontsize=10,loc='lower left')

ax2=fig.add_axes([.70,.405,.24,.29],facecolor='white')
items=sorted(tr.items(),key=lambda p:p[1][1]/p[1][0] if p[1][0] else 0)
labels=[a for a,v in items]; values=[v[1]/v[0]*100 if v[0] else 0 for a,v in items]
colors=['#EC9352' if v<90 else '#13B0A9' for v in values]
ax2.barh(labels,values,color=colors,height=.6)
ax2.set_xlim(0,100); ax2.set_title('Pontualidade por transportadora',loc='left',color='#13263E',fontsize=14,weight='bold',pad=15)
ax2.tick_params(labelsize=10)
ax2.grid(axis='x',color='#EDF1F7')
ax2.set_axisbelow(True)
for idx,v in enumerate(values):ax2.text(v+.5,idx,f'{v:.1f}%',va='center',fontsize=10)

fig.patches.append(plt.Rectangle((.035,.10),.93,.235,transform=fig.transFigure,facecolor='white',edgecolor='#DDE5EF',linewidth=1))
fig.text(.05,.292,'LEITURA OPERACIONAL',fontsize=12,weight='bold',color='#61748A')
fig.text(.05,.236,f'•  {atrasos:,} entregas concluídas fora do prazo.'.replace(',','.'),fontsize=14,color='#13263E')
fig.text(.05,.192,f'•  {vencidos:,} pedidos pendentes já vencidos na data de corte (26/10/2026).'.replace(',','.'),fontsize=14,color='#13263E')
fig.text(.05,.147,'•  Comparar taxa de atraso e volume; ranking absoluto não mede eficiência isoladamente.',fontsize=14,color='#13263E')
fig.text(.5,.038,'Base sintética • Seed 20261026 • Dados ilustrativos, sem vínculo com operações reais',ha='center',fontsize=10,color='#62758A')
path=root/'docs'/'preview_sintetico.png'
fig.savefig(path, dpi=130, facecolor=fig.get_facecolor())
plt.close(fig)
print(path)
