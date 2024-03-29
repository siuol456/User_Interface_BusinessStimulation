from django.shortcuts import render
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
from django.http import HttpResponse
import io
from matplotlib import pyplot
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from django_pandas.io import read_frame
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
import mpld3
import nltk, urllib, request, string, re
from nltk import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()

# Create your views here.
from .models import Source, Author, Article, Topic,Article_content

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_sources = Source.objects.all().count()
    num_articles = Article.objects.all().count()
    
    
    num_topic = Topic.objects.all().count()
    
    # The 'all()' is implied by default.    
    num_authors = Author.objects.count()
    
   

    context = {
        'num_sources': num_sources,
        'num_articles': num_articles,
        'num_topic': num_topic,
        'num_authors': num_authors,
       
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)
from django.views import generic
class ArticleListView(generic.ListView):
    model = Article
    paginate_by = 10
    
class ArticleDetailView(generic.DetailView):
    model = Article
   
    
   
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
class AuthorDetailView(generic.DetailView):
    model = Author
   

def report(request):
    term_count = {}
    for i in Article_content.objects.all():
        words = Article_content.key_word(i)
        for word in words:
            if word not in term_count:
                term_count[word] = 1
            else:
                term_count[word] = term_count[word] + 1
    data = pd.DataFrame.from_dict(term_count, orient='index')
    data = data.reset_index()
    data.columns = ['Terms','Count']
    terms =data.sort_values(by = ['Count'],ascending = False).head(20)
    terms = terms[2:]
    terms1=terms.sort_index()
    T1=terms.iloc[0,0]
    T2=terms.iloc[1,0]
    T3=terms.iloc[2,0]
    T4=terms.iloc[0,1]
    T5=terms.iloc[1,1]
    T6=terms.iloc[2,1]
    
    Competitor =('samsung','galaxy','sony','huawei','powerbeats','google','pixel','jbl','powerhbq')
    Competitor=list(Competitor)
    
    context = {
        'T1':T1,
        'T2':T2,
        'T3':T3,
        'T4':T4,
        'T5':T5,
        'T6':T6,
        'c':Competitor
    }
    return render(request, 'report_home.html', context=context)

def detail_freq(request):
    qs=Article_content.objects.all()
    df2=read_frame(qs)
    qs1 = Article.objects.all()
    df1 = read_frame(qs1)
    df2['score']=df2['content'].apply(lambda x: analyser.polarity_scores(x)['compound'])
    df2.loc[df2['score'] >0.5, 'attitude'] = 'Positive' 
    df2.loc[df2['score'] <-0.5, 'attitude'] = 'Negative'
    df2.loc[df2['attitude'].isna(),'attitude']='Neutral'
    df1['date']=df1['date_of_publish'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    df1['YM']=df1['date'].apply(lambda x: str(x.year)+'-'+str(x.month))
    df1 = df1.sort_values(by='date')
    r=pd.DataFrame(list(zip(df1.YM,df2.attitude)), columns =['YM','attitude'])
    p=list()
    n=list()
    n2=list()
    for d in r.YM.unique():
        t=r[r.YM==d]
        for a in r.attitude.unique():
           if a=="Positive":
               count=len(t[t.attitude==a])
               p.append(count)
           elif a=="Negative":
               count=len(t[t.attitude==a])
               n.append(count)
           else:
               count=len(t[t.attitude==a])
               n2.append(count)
    result = pd.DataFrame(list(zip(r.YM.unique(), p,n,n2)), columns =['Time', 'Positive','Negative','Neutral'])
    fig, ax = plt.subplots()
    x = np.arange(len(r.YM.unique()))  # the label locations
    width = 0.35  # the width of the bars
    rects1 = ax.bar(x - width, result.Positive, width, label='Positive')
    rects2 = ax.bar(x , result.Negative, width, label='Negative')
    rects3 = ax.bar(x + width, result.Neutral, width, label='Neutral')
    ax.set_xticks(x)
    ax.set_xticklabels(r.YM.unique())
    ax.legend()
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)
    response=HttpResponse(buf.getvalue(),content_type='image/png')
    # if required clear the figure for reuse 
    fig.clear()
    # I recommend to add Content-Length for Django
    response['Content-Length'] = str(len(response.content))
    return response

    

def comentionfigure(request):
    term_count = {}
    for i in Article_content.objects.all():
        words = Article_content.key_word(i)
        for word in words:
            if word not in term_count:
                term_count[word] = 1
            else:
                term_count[word] = term_count[word] + 1
    data = pd.DataFrame.from_dict(term_count, orient='index')
    data = data.reset_index()
    data.columns = ['Terms','Count']
    terms =data.sort_values(by = ['Count'],ascending = False).head(20)
    terms = terms[2:]
    terms1=terms.sort_index()
    qs = Article_content.objects.all()
    df = read_frame(qs)
    text = " ".join(content for content in df.content)
    stopwords1 = set(STOPWORDS)
    qs1 = Article.objects.all()
    df1 = read_frame(qs1)
    df1['date']=df1['date_of_publish'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
    df1['YM']=df1['date'].apply(lambda x: str(x.year)+'-'+str(x.month))
    c=list()
    for d in df1.YM.unique():
        count=len(df1[df1.YM==d])
        c.append(count)
    result = pd.DataFrame(list(zip(df1.YM.unique(), c)), columns =['Publish_Time', 'Num']) 
    result['date']=result['Publish_Time'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m'))
    result = result.sort_values(by='date')
    ind=np.arange(len(df1.YM.unique()))
    # Generate a word cloud image
    wordcloud = WordCloud(stopwords=stopwords1, background_color="white",colormap = 'viridis').generate(text)
    font = FontProperties()
    font.set_family('serif')
    font.set_name('Arial Rounded MT')
    font.set_style('italic')
    plt.figure(figsize=(100,120),facecolor='white')
    fig, ax= plt.subplots(2,1)
    ax[1].imshow(wordcloud, interpolation='bilinear')
    ax[1].axis('off')
    ax[0].plot(ind,result.Num)
    ax[0].set_xticks([1,5,10])
    ticks=list(result.Publish_Time)
    t=(ticks[1],ticks[5],ticks[10])
    ax[0].set_xticklabels(t)
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)
    response=HttpResponse(buf.getvalue(),content_type='image/png')
    # if required clear the figure for reuse 
    fig.clear()
    # I recommend to add Content-Length for Django
    response['Content-Length'] = str(len(response.content))
    return response

def competitors_fig(request):
    target=Article_content.objects.all()
    target=read_frame(target)
    target=" ".join(target.content)
    Competitor =('samsung','galaxy','sony','huawei','powerbeats','google','pixel','jbl','powerhbq')
    Competitor=list(Competitor)
    def countW(s,n,W):
           raw = BeautifulSoup(s, 'html.parser').get_text()
           raw=raw.lower()
           raw=re.sub(r'\d+', '', raw)
           tokens = word_tokenize(raw)
           sw = stopwords.words('English')
           new_token=list()
           for t in tokens:
               if t not in sw:
                   new_token.append(t)
           punc=list(string.punctuation)
           manualcheck= ['“','”','’',"n't","'m","th","'d","'s","eant",'priyanka',
                  'bangalore','std','hi','zoe','``',"''",'—',"'re","'ll","'ve",'eh','\x80','airpods','airpod','apple','also'
                 ,'said','want','like','make','even','get','siri','products','product']
           punc.extend(manualcheck)
           new_token2=list()
           for t in new_token:
               if t not in punc:
                  new_token2.append(t)
           freq= nltk.FreqDist(new_token2)
           tryo = pd.DataFrame(list(dict(freq).items()))
           tryo=tryo.sort_values(by=1, ascending=False)
           tryo.columns = ['Words', 'freq']
           if W in list(tryo.Words):
               result= int(tryo[tryo.Words==W].freq)
               return(result)
           else:
               return(0) 
    MT=list()
    for comp in Competitor:
        t2=countW(target,len(target),comp)
        MT.append(t2)
    result=pd.DataFrame({'comp': Competitor,'MT': MT})
    ind=np.arange(len(Competitor)) 
    fig,ax=plt.subplots()
    plt.bar(result['comp'], result['MT'])
    plt.xticks(ind,Competitor) 
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)
    response=HttpResponse(buf.getvalue(),content_type='image/png')
    # if required clear the figure for reuse 
    fig.clear()
    # I recommend to add Content-Length for Django
    response['Content-Length'] = str(len(response.content))
    return response




def report_fig1(request):
    term_count = {}
    for i in Article_content.objects.all():
        words = Article_content.key_word(i)
        for word in words:
            if word not in term_count:
                term_count[word] = 1
            else:
                term_count[word] = term_count[word] + 1
    data = pd.DataFrame.from_dict(term_count, orient='index')
    data = data.reset_index()
    data.columns = ['Terms','Count']
    terms =data.sort_values(by = ['Count'],ascending = False).head(20)
    terms = terms[2:]
    terms1=terms.sort_index()
    fig,ax=plt.subplots()
    sns.set(rc={'figure.figsize':(15,10)})
    sns.set_context("poster", font_scale = 0.8, rc={"grid.linewidth": 1})
    ax = sns.barplot(x="Terms", y="Count", data=terms1, palette="rocket")
    for item in ax.get_xticklabels():
        item.set_rotation(80)
    plt.grid(False)
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(buf)
    response=HttpResponse(buf.getvalue(),content_type='image/png')
    # if required clear the figure for reuse 
    fig.clear()
    # I recommend to add Content-Length for Django
    response['Content-Length'] = str(len(response.content))
    return response

class TopicListView(generic.ListView):
    model = Topic
    paginate_by = 10
class TopicDetailView(generic.DetailView):
    model = Topic

def Author_R(request,pk):
    t=Article_content.objects.filter(id__author__id=pk)
    A=Article.objects.filter(author__id=pk)
    df1 = read_frame(A)
    df2 = read_frame(t)
    df2['score']=df2['content'].apply(lambda x: analyser.polarity_scores(x)['compound'])
    df2.loc[df2['score'] >0.5, 'attitude'] = 'Positive' 
    df2.loc[df2['score'] <-0.5, 'attitude'] = 'Negative'
    df2.loc[df2['attitude'].isna(),'attitude']='Neutral'
    df1=pd.concat([df1, df2],sort=False)
    fig=plt.figure()
    ax1 = plt.subplot(122)
    Topic=list(df1.topic.unique())
    c2=list()
    for i in Topic:
        t=df1.loc[df1['topic']==i,'topic'].count()
        c2.append(t)
    i2=np.arange(len(Topic))
    ax1=plt.bar(i2,c2)
    plt.xticks(i2,Topic)

    ax2 = plt.subplot(221)
    labels = list(('Positive','Negative','Neutral'))
    sizes = [df1.loc[df1['attitude']=='Positive','attitude'].count(),df1.loc[df1['attitude']=='Negative','attitude'].count(),df1.loc[df1['attitude']=='Neutral','attitude'].count()]
    colors = ['gold', 'yellowgreen', 'lightcoral']
    ax2=plt.pie(sizes, labels=labels, colors=colors,autopct='%1.1f%%', shadow=True, startangle=140) 

    ax3 = plt.subplot(223)
    Source=list(df1.source.unique())
    c=list()
    for i in Source:
        t=df1.loc[df1['source']==i,'source'].count()
        c.append(t)
    i=np.arange(len(Source))
    ax3=plt.bar(i,c)
    plt.xticks(i,Source)
    fig_html=mpld3.fig_to_html(fig)
    t2=df1.loc[df1['attitude']=='Positive','attitude'].count()
    t3=df1.loc[df1['attitude']=='Negative','attitude'].count()
    return render(request, 'Online_Content/author_report.html', {'fig': fig_html,'t1':len(df2),'t2':t2,'t3':t3, 't4':Source,'t5':Topic})
   


def competiter(request,pk):
    content=get_object_or_404(Article_content, pk = pk)
    article=get_object_or_404(Article, pk = pk)
    
    target=content.content
    Competitor =('samsung','galaxy','sony','huawei','powerbeats','google','pixel','jbl','powerhbq')
    Competitor=list(Competitor)
    def countW(s,n,W):
           raw = BeautifulSoup(s, 'html.parser').get_text()
           raw=raw.lower()
           raw=re.sub(r'\d+', '', raw)
           tokens = word_tokenize(raw)
           sw = stopwords.words('English')
           new_token=list()
           for t in tokens:
               if t not in sw:
                   new_token.append(t)
           punc=list(string.punctuation)
           manualcheck= ['“','”','’',"n't","'m","th","'d","'s","eant",'priyanka',
                  'bangalore','std','hi','zoe','``',"''",'—',"'re","'ll","'ve",'eh','\x80','airpods','airpod','apple','also'
                 ,'said','want','like','make','even','get','siri','products','product']
           punc.extend(manualcheck)
           new_token2=list()
           for t in new_token:
               if t not in punc:
                  new_token2.append(t)
           freq= nltk.FreqDist(new_token2)
           tryo = pd.DataFrame(list(dict(freq).items()))
           tryo=tryo.sort_values(by=1, ascending=False)
           tryo.columns = ['Words', 'freq']
           if W in list(tryo.Words):
               result= int(tryo[tryo.Words==W].freq)
               return(result)
           else:
               return(0) 
    MT=list()
    for comp in Competitor:
        t2=countW(target,len(target),comp)
        MT.append(t2)
    if any(MT):
        result=pd.DataFrame({'comp': Competitor,'MT': MT})
        ind=np.arange(len(Competitor)) 
        fig,ax=plt.subplots()
        plt.bar(result['comp'], result['MT'])
        plt.xticks(ind,Competitor) 
        fig_html=mpld3.fig_to_html(fig)
    else:
        fig_html=False
    wordct=sum(MT)
    #cometioned term
    def countWords(A):
       dic={}
       for x in A:
          if not x in  dic:        
             dic[x] = A.count(x)
       return dic

    dic = countWords(Article_content.key_word(content))
    sorted_items=sorted(dic.items(),key=lambda x: x[1],reverse=True)  
    sorted_items = pd.DataFrame.from_dict(sorted_items)
    sorted_items.columns = {'Terms','Frequency'}
    datetime_object1 = article.date_of_publish
    release_date = '2019-03-20'
    datetime_object2 = datetime.strptime(release_date, '%Y-%m-%d')
    month_diff = datetime_object1.month-datetime_object2.month
    if month_diff >0:
        term='after'
    else:
        term='before'
    month_diff = abs(month_diff)
    datetime_object1=datetime_object1.strftime("%b %d %Y ")
    T3=len(str(content.content).split(" "))
    fig2,ax=plt.subplots()
    sns.barplot(x="Terms", y="Frequency", data=sorted_items[0:9], palette="muted")
    plt.title("Top 10 Co-mentioned Terms",pad = 15,fontsize = 20)
    fig2_html=mpld3.fig_to_html(fig2)
    return render(request, 'Online_Content/article_report.html', {'fig': fig_html,'fig2': fig2_html, 'content':content,'article':article, 'T1':month_diff, 'T2':term,
                                                                  'T3':T3,'T4':sorted_items.Terms[0],'T5':sorted_items.Terms[1],'T6':sorted_items.Terms[2],'T7':sum(sorted_items.Frequency[:3]),
                                                                  'T8':wordct})


class SourceListView(generic.ListView):
    model = Source
class SourceDetailView(generic.DetailView):
    model = Source

   
